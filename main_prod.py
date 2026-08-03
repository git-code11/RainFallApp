from kivymd.uix.screenmanager import MDScreenManager
from kivymd.tools.hotreload.app import MDApp
import importlib
import os

class RainfallProject(MDApp):
    KV_DIRS = [os.path.join(os.getcwd(), "View")]
    AUTORELOADER_IGNORE_PATTERNS = [*MDApp.AUTORELOADER_IGNORE_PATTERNS.defaultvalue, "*.git*", "*.venv*"]

    def build_app(self) -> MDScreenManager:
        """
        In this method, you don't need to change anything other than the
        application theme.
        """

        import View.screens
        self.forecaster = forecaster
        self.manager_screens = MDScreenManager()
        Window.bind(on_key_down=self.on_keyboard_down)
        importlib.reload(View.screens)
        screens = View.screens.screens

        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)
        Clock.schedule_once(lambda _: self.go_to_main(), 5)
        return self.manager_screens

    def go_to_main(self):
        self.manager_screens.current = "main screen"

    def on_keyboard_down(self, window, keyboard, keycode, text, modifiers) -> None:
        """
        The method handles keyboard events.

        By default, a forced restart of an application is tied to the
        `CTRL+R` key on Windows OS and `COMMAND+R` on Mac OS.
        """

        if "meta" in modifiers or "ctrl" in modifiers and text == "r":
            self.rebuild()

