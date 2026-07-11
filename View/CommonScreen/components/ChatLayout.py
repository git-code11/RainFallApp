from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import AliasProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivy.core.text import Label as CoreLabel
from kivy.core.text.text_layout import layout_text


class ChatText(ButtonBehavior, RecycleDataViewBehavior, MDBoxLayout):
    def __init__(self, **kwargs):
        super(ChatText, self).__init__(**kwargs)

    def on_press(self):
        print(f"Wonderful {self.height}")


def refresh_view_attrs(self, rv, index, data):
    ''' Catch and handle the view changes '''
    super().refresh_view_attrs(
        rv, index, data)


class ChatList(MDRecycleView):
    def __init__(self, **kwargs):
        super(ChatList, self).__init__(**kwargs)
        self.messages = [dict(
            is_bot=idx % 2 == 0,
            text=f"We are currently at the value \n{
                idx} and \nwhen we equate \nit we have `{'q'*(idx+1)}` \n {'0'*20*(idx+5)}") for idx in range(20)]

    def determine_height(self, text: str):
        ll = CoreLabel()
        lines = []
        w, h, _ = layout_text(text, lines, (0, 0), (300, None),
                              ll.options, ll.get_cached_extents(), True, False)
        return (w, h)

    def height_update(self, value):

        value = [
            dict(**data,
                 item_size=self.determine_height(data['text'])) for data in value]

        self.data = value

    messages = AliasProperty(lambda x: None, height_update, bind=["data"])


class ChatLayout(MDBoxLayout):
    pass
