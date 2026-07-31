
"""
Script for managing hot reloading of the project.
For more details see the documentation page -

https://kivymd.readthedocs.io/en/latest/api/kivymd/tools/patterns/create_project/

To run the application in hot boot mode, execute the command in the console:
DEBUG=1 python main.py
"""
import dotenv
dotenv.load_dotenv()
from kivy import Config

# Change the values of the application window size as you need.
# Config.set("graphics", "height", resolution[1])
Config.set("graphics", "height", "360")
Config.set("graphics", "width", "480")

# TODO: You may know an easier way to get the size of a computer display.
try:
    from PIL import ImageGrab
    resolution = ImageGrab.grab().size
except OSError:
    import pyautogui
    resolution = pyautogui.size()

from kivy.core.window import Window
# Place the application window on the right side of the computer screen.
Window.top = 0
Window.left = resolution[0] - Window.width

from View.screens import screens
from kivy.properties import BooleanProperty
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.app import MDApp
from multitasking import task
from kivy.clock import Clock, mainthread



# """
# The entry point to the application.
#
# The application uses the MVC template. Adhering to the principles of clean
# architecture means ensuring that your application is easy to test, maintain,
# and modernize.
#
# You can read more about this template at the links below:
#
# https://github.com/HeaTTheatR/LoginAppMVC
# https://en.wikipedia.org/wiki/Model–view–controller
# """
#


class RainfallProject(MDApp):
    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        # This is the screen manager that will contain all the screens of your
        # application.
        self.manager_screens = MDScreenManager()
        self.onboarding_screen = "onboarding screen"


    def build(self) -> MDScreenManager:
        self.add_screen(self.onboarding_screen)
        self.load_forecaster()
        return self.manager_screens

    @task
    def load_forecaster(self):
        from libs.app import ForecastApp

        data_path = r"./assets/data.xls"
        model_path = r"./assets/RainFallModelLinear.tflite"
        self.forecaster = ForecastApp(data_path, model_path)
        self.active = True

    @mainthread
    def on_active(self, _, __):
        onboarding_screen = self.manager_screens.current_screen
        self.generate_application_screens()
        onboarding_screen.stop()

    def generate_application_screens(self) -> None:
        """
        Creating and adding screens to the screen manager.
        You should not change this cycle unnecessarily. He is self-sufficient.

        If you need to add any screen, open the `View.screens.py` module and
        see how new screens are added according to the given application
        architecture.
        """
        for i, name_screen in enumerate(screens.keys()):
            if self.onboarding_screen == name_screen:
                continue
            self.add_screen(name_screen)

        def go_to_main(_):
            self.manager_screens.current = "main screen"

        Clock.schedule_once(go_to_main, 0)

    def add_screen(self, name_screen: str):
        model = screens[name_screen]["model"]()
        print(model)
        controller = screens[name_screen]["controller"](model)
        view = controller.get_view()
        view.manager_screens = self.manager_screens
        view.name = name_screen
        self.manager_screens.add_widget(view)

if __name__ == "__main__":
    RainfallProject().run()
