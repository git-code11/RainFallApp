import pandas as pd
from libs.dl import TFLiteRuntime
from libs.data import ForecastEngine


class ForecastApp:
    def __init__(self, data_path: str, model_path: str, **kwargs):
        params = dict(
            group_key='key',
            feature_label='precipitation',
            period_label='period',
            sequence_length=6,
            **kwargs
        )

        df = pd.read_excel(data_path)
        df = df[[params['period_label'],
                 params['feature_label'], params['group_key']]]

        self.data = ForecastEngine(
            df=df,
            **params
        )

        self.tflite = TFLiteRuntime.load(model_path)

    def forecast(self, **kwargs):
        return self.data.forecast(self.tflite, **kwargs)

    @property
    def unique_key(self):
        return self.data.unique_key
