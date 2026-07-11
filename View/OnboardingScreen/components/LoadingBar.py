
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properies import ColorProperty, NumericProperty


class LoadingBar(MDBoxLayout):
    border_width = NumericProperty()
    pad = NumericProperty()
    bg_color = ColorProperty()
    bar_color = ColorProperty()
    border_color = ColorProperty()
    radius = NumericProperty()
    value = NumericProperty()
    radius = NumericProperty()
