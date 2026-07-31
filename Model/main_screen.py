from Model.base_model import BaseScreenModel
from kivy.app import App


class MainScreenModel(BaseScreenModel):
    """
    Implements the logic of the
    :class:`~View.main_screen.MainScreen.MainScreenView` class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._forecaster = App.get_running_app().forecaster

    @property
    def forecaster(self):
        return self._forecaster

    @property
    def unique_key(self):
        return self._forecaster.unique_key

    def forecast(self, **kwargs):
        return self._forecaster.forecast(**kwargs)
