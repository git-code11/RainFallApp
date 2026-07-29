import numpy as np
import pandas as pd
import datetime
from sklearn.preprocessing import StandardScaler, LabelEncoder


def int_to_binary(ints, bits=8):
    # Create a range of bit positions: [bits-1, bits-2, ..., 0]
    shift_amounts = np.arange(bits - 1, -1, -1, dtype=np.int32)

    # Expand dims to allow broadcasting: (N, 1) and (bits,)
    ints_expanded = np.array(ints)[..., np.newaxis]

    # Shift bits to the right and take the last bit (modulo 2)
    binary = (ints_expanded >> shift_amounts) % 2
    return binary

# Feature extraction cyclic encode


def cyclical_encode(data, max_val):
    return np.sin(2 * np.pi * data / max_val)


class ForecastEngine:
    def __init__(self,
                 df: pd.DataFrame,
                 group_key: str,
                 feature_label: str,
                 period_label: str,
                 sequence_length: int = 6,
                 advance_length: int = 10
                 ) -> None:

        self.feature_label = feature_label
        self.feature_label_std = f'STD_{feature_label}'
        self.period_label = period_label
        self.unique_id_label = f'GID_{group_key}'
        self.sequence_length = sequence_length
        self.group_key = group_key
        self.advance_length = advance_length

        self.standard_scaler = StandardScaler()
        self.df = df.dropna(axis=1).reset_index(drop=True).copy()
        self.df[self.feature_label_std] = self.standard_scaler.fit_transform(
            self.df[feature_label].to_numpy().reshape(-1, 1))

        unique_key = pd.unique(self.df[group_key])
        unique_key = unique_key.tolist()
        unique_key.sort()
        self.unique_key = unique_key

        self.bit_count = np.ceil(np.log2(len(unique_key) + 1))

        labelEncoder = LabelEncoder()
        labelEncoder.fit(unique_key)
        self.df[self.unique_id_label] = labelEncoder.transform(
            self.df[group_key]) + 1
        self.labelEncoder = labelEncoder

        self.df_last_timestamp = self.df.groupby(self.group_key)[
            'period'].max()

    def extract_features(self, df: pd.DataFrame):
        # Lagging feature extraction
        df["lag_0"] = df[self.feature_label_std].shift(1)
        df["clag_0"] = cyclical_encode(df[self.period_label].dt.month, 12)

        # Drop rows with NaN created by lagging
        result = df.dropna()
        timestamps = result['period'].to_numpy()
        # print(f'KEY_ID: {result[self.unique_id_label][:3]}')
        key_id = result[self.unique_id_label].iloc[0]
        # the integer size can fit into 6 bits
        id_binarys = int_to_binary([int(key_id)], bits=self.bit_count)
        id_binarys = np.repeat(id_binarys, np.shape(result)[0], axis=0)
        # print(f'ID Binary {np.shape(id_binarys)}')
        lag_features = result["lag_0"].to_numpy()
        # print(f'Lag Features {np.shape(lag_features)}')
        clag_features = result["clag_0"].to_numpy()
        # print(f'Clag Features {np.shape(clag_features)}')
        X = np.concat([id_binarys, clag_features[..., np.newaxis],
                      lag_features[..., np.newaxis]], axis=1)
        # print(f'X {X.shape}')
        y = result[self.feature_label_std].to_numpy()
        data = (timestamps, X, y)
        return data

    def feature_at_time(self, region_key: str, time: pd.Timestamp | None = None):
        next_timestamp_ = self.next_timestamp(region_key)
        if time is None:
            time = next_timestamp_

        df1 = self.filtered_df(region_key)
        df1 = df1.iloc[-(self.sequence_length + 4):]
        data = None

        if next_timestamp_ == time:
            new_df = df1.iloc[-1:]
            new_df[self.period_label] = new_df[self.period_label] + \
                pd.DateOffset(months=1)
            new_df[self.feature_label] = 0
            df2 = pd.concat([df1, new_df]).reset_index(drop=True)
            data = self.extract_features(df2)

        elif self.last_timestamp(region_key) == time:
            data = self.extract_features(df1)

        else:
            raise Exception("Timestamp Gap too much")
        return [data[0][-1], data[1][-self.sequence_length:]]

    def filtered_df(self, region_key: str):
        return self.df[self.df[self.group_key] ==
                       region_key].reset_index(drop=True)

    def last_timestamp(self, region_key: str):
        df1 = self.filtered_df(region_key)
        return pd.Timestamp(df1[self.period_label].iloc[-1])

    def next_timestamp(self, region_key: str):
        return self.last_timestamp(region_key) + pd.DateOffset(months=1)

    def has_timestamp(self, region_key: str, time: pd.Timestamp):
        periods = self.filtered_df(region_key)[self.period_label]
        assert pd.Timestamp(periods.iloc[0]) <= time, f"Model can not forecast value less than {
            periods.iloc[0]}"
        return pd.Timestamp(periods.iloc[-1]) >= time

    def get_data(self, region_key: str, time_range: list[pd.Timestamp]):
        df1 = self.filtered_df(region_key)
        return df1[df1[self.period_label].between(*time_range)][[self.period_label, self.feature_label]].reset_index(drop=True)

    def update_record(self, region_key: str, period: pd.Timestamp, feature_std: float):
        if self.last_timestamp(region_key) == period:
            return

        data = {
            self.feature_label_std: feature_std,
            self.feature_label: self.standard_scaler.inverse_transform([[feature_std]])[
                0][0],
            self.period_label: period,
            self.group_key: region_key,
            self.unique_id_label: self.labelEncoder.transform([region_key])[
                0] + 1
        }

        new_df = pd.DataFrame([data])
        self.df = pd.concat([self.df, new_df])

    def forecast(self, model,
                 region_key: str,  start_time: pd.Timestamp | datetime.datetime | None = None,
                 end_time: pd.Timestamp | datetime.datetime | None = None,
                 length: int | None = None):
        if isinstance(start_time, (datetime.datetime, datetime.date)):
            start_time = pd.Timestamp(start_time)

        if isinstance(end_time, (datetime.datetime, datetime.date)):
            end_time = pd.Timestamp(end_time)

        if start_time is None:
            start_time = self.df_last_timestamp[region_key]
        assert end_time is None or length is None, "Both end_time and length are mutually exclusive"
        if end_time is None:
            end_time = start_time + pd.DateOffset(months=length or 6)
        else:
            length = len(pd.date_range(
                start=start_time, end=end_time, freq="MS"))

        if not (self.has_timestamp(region_key, start_time) and self.has_timestamp(region_key, end_time)):
            timestamps = pd.date_range(
                start=self.last_timestamp(region_key), end=end_time + pd.DateOffset(months=self.advance_length), freq="MS")
            for time in timestamps:
                feature = self.feature_at_time(region_key, time)
                output = model(feature[1].astype(np.float32))
                assert time == feature[0], "Different timestamp during forecast"
                self.update_record(region_key, time, output[0])
        result = self.get_data(region_key, [start_time, end_time])
        return result
        # return result.set_index(self.period_label, drop=False)


if __name__ == '__main__':
    df = pd.read_excel(r"assets/data.xls")
    df = df[['period', 'precipitation', 'key']]

    data_gen = ForecastEngine(
        df=df,
        group_key='key',
        feature_label='precipitation',
        period_label='period',
        sequence_length=6,
    )

    unique_key = data_gen.unique_key[0]

    print(f"{data_gen.unique_key=}")
    out = data_gen.feature_at_time(
        unique_key, data_gen.next_timestamp(unique_key))
    out2 = data_gen.feature_at_time(
        unique_key, data_gen.last_timestamp(unique_key))
    print(f"{out=}")
    print(f"{out2=}")
