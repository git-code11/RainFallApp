import importlib
from multitasking import task
from kivy.clock import mainthread
from libs.chat import ChatAgent
from libs.common import SYSTEM_PROMPT
from contextlib import contextmanager
import View.MainScreen.main_screen
# We have to manually reload the view module in order to apply the
# changes made to the code on a subsequent hot reload.
# If you no longer need a hot reload, you can delete this instruction.
importlib.reload(View.MainScreen.main_screen)


class MainScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = View.MainScreen.main_screen.MainScreenView(
            controller=self, model=self.model)
        self.max_length = 5
        self.agent = ChatAgent(
            system_prompt=SYSTEM_PROMPT,
            forecast=self.agent_forecast,
            plot_forecast=self.agent_plot_forecast,
        )
        self.agent.init()

    @contextmanager
    def error_manager(self):
        try:
            yield
        except Exception as e:
            # print(f"{e.args} \n{e}")
            self.view.error = e.args[0]
        # finally:
        #     print("we are okay")

    def agent_forecast(self, **kwargs):
        with self.error_manager():
            [X, y] = self.model.forecast(plot_format=True, **kwargs)
            X = X.dt.strftime("%m/%Y")
            y = y.astype(str)
            out = f"""**Forecast Result for {kwargs.get('region_key')}**
            **Periods** = {",".join(X)}
            **Precipitation** = {",".join(y)}
            """
            return out
        return "Error Occured during forecating"

    def agent_plot_forecast(self, **kwargs):
        with self.error_manager():
            self.view.selected_key = [
                kwargs.get('region_key'),
                dict(
                    start=kwargs.get('start_time'),
                    end=kwargs.get('end_time')
                )
            ]
            return "The graph has been plotted"
        return "Failed to plot graph"

    @task
    def send_text(self, text: str):
        with self.error_manager():
            min_date = self.model.forecaster.get_min_date(
                self.view.selected_region)
            self.view.info = "sending text"
            self.agent.send(
                text=text,
                on_sent=self.message_sent_callback,
                all_region_keys=self.model.unique_key,
                current_region_key=self.view.selected_region,
                current_date_range=(
                    self.view.date['start'], self.view.date['end']),
                min_date=min_date
            )

    @mainthread
    def message_sent_callback(self, user_text, ai_text):
        # update views for message list
        self.view.info = "sent"
        self.view.chat_layout.chat_list.messages = [
            *self.view.chat_layout.chat_list.messages[-self.max_length:],
            dict(text=user_text, is_bot=False),
            dict(text=ai_text, is_bot=True)
        ]
        self.view.chat_layout.input_field.text = ""

    @task
    def forecast(self, **kwargs):
        with self.error_manager():
            result = self.model.forecast(**kwargs)
            self.view.data = result

    def get_view(self) -> View.MainScreen.main_screen:
        return self.view
