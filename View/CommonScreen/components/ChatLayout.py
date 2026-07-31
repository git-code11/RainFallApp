from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import AliasProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivy.core.text import Label as CoreLabel
from kivy.core.text.text_layout import layout_text
from kivymd.uix import MDAdaptiveWidget
from kivy.uix.textinput import TextInput
from kivymd.uix.behaviors.backgroundcolor_behavior import BackgroundColorBehavior


class ChatText(ButtonBehavior, RecycleDataViewBehavior, MDBoxLayout):
    def __init__(self, **kwargs):
        super(ChatText, self).__init__(**kwargs)

    def on_press(self):
        print(f"Wonderful {self.height=} {self.width=}")


def refresh_view_attrs(self, rv, index, data):
    ''' Catch and handle the view changes '''
    super().refresh_view_attrs(
        rv, index, data)


class ChatTextInput(BackgroundColorBehavior, TextInput, MDAdaptiveWidget):

    def __init__(self, *args, **kwargs):
        super(ChatTextInput, self).__init__(**kwargs)


class ChatList(MDRecycleView):
    MAX_WIDTH = 270

    def __init__(self, **kwargs):
        super(ChatList, self).__init__(**kwargs)
        self.messages = [dict(text="Let help in analysis", is_bot=True)]

    def determine_height(self, text: str):
        ll = CoreLabel()
        lines = []
        # TODO: If there is a better way to make this stuff work
        w, h, _ = layout_text(text, lines, (0, 0), (self.MAX_WIDTH, None),
                              ll.options, ll.get_cached_extents(), True, False)
        # print(f"{(w, h)=}")
        return (w, h)

    def height_update(self, value):
        value = [
            {**data,
             "item_size": self.determine_height(data['text']),
             # "pos_hint": {"right": 1 if data['is_bot'] else None}
             } for data in value]
        self.data = value

    def get_message(self):
        return self.data

    messages = AliasProperty(get_message, height_update, bind=["data"])


class ChatLayout(MDBoxLayout):
    action = ObjectProperty()
    input_field = ObjectProperty()
