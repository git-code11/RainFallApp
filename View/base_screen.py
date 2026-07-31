from kivy.properties import ObjectProperty, StringProperty

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock, mainthread
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.metrics import dp


from Utility.observer import Observer


class BaseScreenView(MDScreen, Observer):
    """
    A base class that implements a visual representation of the model data.
    The view class must be inherited from this class.
    """

    controller = ObjectProperty()
    """
    Controller object - :class:`~Controller.controller_screen.ClassScreenControler`.

    :attr:`controller` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    model = ObjectProperty()
    """
    Model object - :class:`~Model.model_screen.ClassScreenModel`.

    :attr:`model` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    manager_screens = ObjectProperty()
    """
    Screen manager object - :class:`~kivymd.uix.screenmanager.MDScreenManager`.

    :attr:`manager_screens` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    error = StringProperty()
    """
    Error Handling Mechanism
    """

    info = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        # Often you need to get access to the application object from the view
        # class. You can do this using this attribute.
        self.app = MDApp.get_running_app()
        # Adding a view class as observer.
        self.model.add_observer(self)

    @mainthread
    def on_error(self, _, text):
        if text == "":
            return
        Clock.schedule_once(lambda _: self.setter("error")(None, ""), 0)
        # Show snackbar
        MDSnackbar(
            MDSnackbarText(
                text=text,
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1),
            ),
            y=dp(36),
            pos_hint={"right": 1, "top": 1.},
            size_hint_x=.85,
        ).open()

    @mainthread
    def on_info(self, _, text):
        if text == "":
            return
        Clock.schedule_once(lambda _: self.setter("info")(None, ""), 0)
        # Show snackbar
        MDSnackbar(
            MDSnackbarText(
                text=text,
                theme_text_color="Custom",
                text_color=(0, .5, .5, 1),
            ),
            y=dp(36),
            pos_hint={"right": 1, "top": 1.},
            size_hint_x=.85,
        ).open()
