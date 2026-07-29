from Model.base_model import BaseScreenModel
from libs.app import ForecastApp


data_path = r"./assets/data.xls"
model_path = r"./assets/RainFallModelLinear.tflite"
forecaster = ForecastApp(data_path, model_path)


class MainScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.main_screen.MainScreen.MainScreenView` class.
    """

    @property
    def unique_key(self):
        return forecaster.unique_key

    def forecast(self, **kwargs):
        return forecaster.forecast(**kwargs)
