import pandas as pd
from libs.data import ForecastEngine

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
