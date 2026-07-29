from View.base_screen import BaseScreenView
import datetime
from kivy.properties import ObjectProperty, BooleanProperty, DictProperty, StringProperty, ReferenceListProperty
from kivy.clock import Clock
from kivy.animation import Animation, AnimationTransition
from kivymd.uix.pickers import MDModalInputDatePicker
from kivymd.uix.menu import MDDropdownMenu
from .components.ChartGraph import ChartGraph


class MainScreenView(BaseScreenView):
    chat_layout = ObjectProperty()
    chat_visibility = BooleanProperty(False)
    graph = ObjectProperty()
    date_label = ObjectProperty()
    data = ObjectProperty()
    date = DictProperty()
    selected_region = StringProperty()
    labels = ReferenceListProperty(selected_region, date)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.month_gap = 12
        self.interval = 4
        today_month = datetime.date.today().replace(year=2015)
        older_month = today_month - datetime.timedelta(days=self.month_gap*30)

        self.refresh = Clock.create_trigger(self._refresh)
        self.chat_animation = None

        self.bind(labels=self.label_handler)

        def cb(_):
            self.date = dict(
                start=older_month.replace(day=1),
                end=today_month.replace(day=1)
            )
            self.selected_region = self.model.unique_key[0]
        Clock.schedule_once(cb, 0)

    def on_chat_visibility(self, _, val: bool):
        chat_width = self.chat_layout.width
        target_x = -chat_width*(0 if val else 1)
        if self.chat_animation is not None:
            Animation.cancel_all(self.chat_layout, 'x')
        self.chat_animation = Animation(
            x=target_x, duration=.5, transition=AnimationTransition.in_back)
        self.chat_animation.start(self.chat_layout)

    def on_data(self, _, data):
        self.graph.data = [data['period'], data['precipitation']]

    def label_handler(self, _, __):
        self.date_label.text = f"Region ID: {self.selected_region}\nStart Date: {self.date['start'].strftime(
            r'%m/%Y')}      End Date: {self.date['end'].strftime(r'%m/%Y')}"
        self.refresh()

    def _refresh(self, _):
        self.controller.forecast(region_key=self.selected_region,
                                 start_time=self.date['start'],
                                 end_time=self.date['end'])

    def toggle_chat(self):
        self.chat_visibility = not self.chat_visibility

    def set_date(self):
        date_dialog = MDModalInputDatePicker(
            mark_today=False,
            date_format="dd/mm/yyyy",
            default_input_date=True,
            mode="range"
        )

        def on_ok(instance):
            instance.dismiss()
            result = instance.get_date()
            if len(result) != 2:
                return
            if result[1] < result[0]:
                result = [result[1], result[0]]
            self.date = dict(
                start=result[0].replace(day=1),
                end=result[1].replace(day=1)
            )

        date_dialog.bind(on_ok=on_ok)
        date_dialog.open()

    def shift_date(self, dec=False):
        offset = datetime.timedelta(days=self.interval*30)
        offset = -offset if dec else offset
        new_date = dict(
            start=(self.date['start'] + offset).replace(day=1),
            end=(self.date['end'] + offset).replace(day=1)
        )
        self.date = new_date

    def open_menu(self, item):
        def cb(region_id):
            self.selected_region = region_id
        menu_items = [
            {
                "text": k,
                "on_release": lambda x=k: cb(x),
            } for k in self.model.unique_key
        ]
        MDDropdownMenu(caller=item, items=menu_items).open()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
