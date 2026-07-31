from View.base_screen import BaseScreenView
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.animation import Animation, AnimationTransition


class OnboardingScreenView(BaseScreenView):
    progress = NumericProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self.start, 0.2)

    def start(self, _):
        config = dict(
            transition=AnimationTransition.in_out_cubic,
            step=1/20,
            duration=5
        )
        self.anim = Animation(progress=1, **config) + \
            Animation(progress=0, **config)
        self.anim.repeat = True
        self.anim.start(self)

    def stop(self):
        self.anim.stop_all(self, 'progress')
        self.progress = 1

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
