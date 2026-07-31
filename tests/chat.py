import pandas as pd
from libs.app import ForecastApp
from libs.chat import ChatAgent
from libs.common import SYSTEM_PROMPT

import dotenv

dotenv.load_dotenv()

df = pd.read_excel(r"assets/data.xls")
df = df[['period', 'precipitation', 'key']]


data_path = r"./assets/data.xls"
model_path = r"./assets/RainFallModelLinear.tflite"
forecaster = ForecastApp(data_path, model_path)


def forecast(**kwargs):
    print(f"forecast {kwargs=}")
    [X, y] = forecaster.forecast(plot_format=True, **kwargs)
    X = X.dt.strftime("%m/%Y")
    y = y.astype(str)
    out = f"""**Forecast Result for {kwargs.get('region_key')}**
    **Periods** = {",".join(X)}
    **Precipitation** = {",".join(y)}
    """
    print(f"{out=}")
    return out


def plot_forecast(**kwargs):
    print("plot_forecast {kwargs=}")
    result = forecaster.forecast(plot_format=True, **kwargs)
    return "The graph has been plotted"


agent = ChatAgent(
    system_prompt=SYSTEM_PROMPT,
    forecast=forecast,
    plot_forecast=plot_forecast,
)


# Todo: add svaing of cuurent_region_key
print("Use CTRL-D to end")
while True:
    text = input(">>")
    if text == "":
        break
    # text = "make forecast for makoko from quater of 2021"
    output = agent.send(
        text=text,
        all_region_keys=forecaster.unique_key,
        current_region_key=forecaster.unique_key[0],
        min_date=forecaster.get_min_date(forecaster.unique_key[0])
    )
    print(output)
print("Donw and doested")
print(agent.chat_history.messages)
