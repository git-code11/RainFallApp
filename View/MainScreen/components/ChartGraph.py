import io
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, ListProperty, DictProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import mainthread
from kivy.core.image import Image as CoreImage
from kivy.metrics import Metrics
from multitasking import task


default_graph_config = dict(
    color="#FF5733",
    linewidth=3,
    # ylimit=[0, 10],
    # xlimit=[0, 30],
    # xyoffset=[10, 0],
    ylimit=[None, None],
    xlimit=[None, None],
    xyoffset=[None, None],
    enable_limit=True,
    scale=2,
    ticklabelsize=14
)


class ChartGraph(MDBoxLayout):
    data = ObjectProperty()
    figsize = ListProperty([10, 8])
    graph_config = DictProperty(default_graph_config)
    texture = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(MDBoxLayout, self).__init__(*args, **kwargs)
        self.register_event_type('on_graph_update')
        self.raw_image = io.BytesIO()
        self.bind(data=lambda _, __: self.reload())

    def on_size(self, _, __):
        perpixel = self.graph_config['scale'] / Metrics.dpi
        self.figsize = [
            int(x*perpixel) or 2 for x in self.size]

    def reload(self):
        self.plot_graph()

    @task
    def plot_graph(self) -> plt.Figure:
        try:
            self.__plot_graph(self.data)
            self.dispatch('on_graph_update')
        except Exception as e:
            self.view.error = e.args[0]

    def __plot_graph(self, data) -> plt.Figure:
        fig = plt.Figure(figsize=self.figsize)
        ax = fig.subplots()
        ax.plot(
            *data, linewidth=self.graph_config['linewidth'], color=self.graph_config['color'])
        ax.tick_params(
            axis='both', labelsize=self.graph_config['ticklabelsize'])

        if self.graph_config['enable_limit']:
            y_min, y_max = self.graph_config['ylimit']
            x_min, x_max = self.graph_config['xlimit']
            x_offset, y_offset = self.graph_config['xyoffset']
            if y_offset is not None:
                if y_min is not None:
                    y_min = y_min + y_offset
                if y_max is not None:
                    y_max = y_max + y_offset

            if x_offset is not None:
                if x_min is not None:
                    x_min = x_min + x_offset
                if x_max is not None:
                    x_max = x_max + x_offset

            ax.set_ylim(ymin=y_min, ymax=y_max)
            ax.set_xlim(xmin=x_min, xmax=x_max)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout(pad=0, rect=(1, 1, 1, 1))
        self.raw_image.seek(0)  # Ensure pointer is at the beginning of buffer
        self.raw_image.truncate(0)  # Empty buffer
        fig.savefig(self.raw_image, dpi=100, bbox_inches='tight', format="png")

    @mainthread
    def on_graph_update(self):
        app = App.get_running_app()
        try:
            self.raw_image.seek(0)  # Ensure buffer pointer is at the beginning
            core_image = CoreImage(self.raw_image, ext="png")
            self.texture = core_image.texture
        except Exception as e:
            app.manager_screens.current_screen.error = e.args[0]
