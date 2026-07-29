import pandas as pd
from libs.app import ForecastApp

data_path = r"./assets/data.xls"
model_path = r"./assets/RainFallModelLinear.tflite"

app = ForecastApp(data_path, model_path)

selected_region = app.data.unique_key[0]
# result = app.forecast(region_key=selected_region, length=10)
# print(f"{result=}")
# result = app.forecast(region_key=selected_region, end_time=pd.Timestamp.now())
# print(app.data.filtered_df(selected_region).iloc[-20:])
result = app.forecast(region_key=selected_region,
                      start_time=pd.Timestamp(year=1980, month=1, day=1), end_time=pd.Timestamp(year=2020, month=1, day=1))
