import typing as tp
import datetime
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.utils.uuid import uuid7
from langchain.messages import HumanMessage
from langchain.agents.middleware import ModelRequest, ModelResponse, dynamic_prompt
from md2bbcode import process_readme

# os.environ['GOOGLE_API_KEY'] = "your-api-key"


default_agent_config = dict(
    model="google_genai:gemini-3.5-flash-lite",
)


@dataclass
class ChatContext[T]:
    app: T
    all_region_keys: list[str]
    current_region_key: str
    current_date_range: list[datetime.datetime]
    min_date: datetime.datetime


class ChatAgent:
    def __init__(self, system_prompt: str, forecast: tp.Any,
                 plot_forecast: tp.Any, **kwargs):
        self.system_prompt = system_prompt
        self.user_config = {"configurable": {
            "thread_id": str(uuid7())}}
        self.agent_config = default_agent_config
        self._forecast = forecast
        self._plot_forecast = plot_forecast
        # replace uuid7 with region_key
        self.init()

    def init(self, *,
             checkpointer: BaseCheckpointSaver | None = None):
        config = {
            **default_agent_config,
            **dict(
                tools=self.tools,
                system_prompt="You are a helpful assistant",
            )
        }

        self.checkpointer = checkpointer or InMemorySaver()

        @dynamic_prompt
        def update_system_prompt(request: ModelRequest[ChatContext]) -> str:
            ctx = request.runtime.context
            prompt_context = dict(
                all_region_keys=','.join(ctx.all_region_keys),
                current_region_key=ctx.current_region_key,
                current_start_date=ctx.current_date_range[0].strftime("%m/%Y"),
                current_end_date=ctx.current_date_range[1].strftime("%m/%Y"),
                min_date=ctx.min_date.strftime("%m/%Y"),

            )
            return self.system_prompt.format_map(prompt_context)

        self._agent = create_agent(
            **config,
            checkpointer=self.checkpointer,
            middleware=[update_system_prompt],
            context_schema=ChatContext,
        )

    @property
    def tools(self):
        return [self.forecast, self.display_graph]

    @tool
    @staticmethod
    def forecast(region_key: str,
                 start_time: datetime.datetime,
                 end_time: datetime.datetime,
                 runtime: ToolRuntime[ChatContext]) -> list[list[datetime.datetime], list[float]]:
        """Get weather forecast result for a region within a bounded period of time in month interval

        Args:
        region_key: The id of region to be forecasted
        start_time: The intial bounding time
        end_time: The final bounding time
        """
        app = runtime.context.app
        return app._forecast(
            region_key=region_key,
            start_time=start_time,
            end_time=end_time
        )

    @tool(return_direct=True)
    @staticmethod
    def display_graph(region_key: str,
                      start_time: datetime.datetime,
                      end_time: datetime.datetime,
                      runtime: ToolRuntime[ChatContext]) -> str:
        """Show plot of the forecast within the specified time range on the graph in month interval

        Args:
        region_key: The id of region to be forecasted
        start_time: The intial bounding time
        end_time: The final bounding time
        """
        app = runtime.context.app
        return app._plot_forecast(
            region_key=region_key,
            start_time=start_time,
            end_time=end_time
        )
        # Fore cast work here and graoh plot here

    def send(self, text: str, on_sent: tp.Callable[[str, str], None] | None = None, bbcode_format: bool = True, **kwargs) -> str:
        context = ChatContext(app=self, **kwargs)
        agent = self._agent
        result = agent.invoke(
            {"messages": [HumanMessage(text)]},
            config=self.user_config,
            context=context,
        )
        output = result["messages"][-1].text
        if bbcode_format:
            output = process_readme(output)
        if on_sent is not None:
            on_sent(text, output)
        return output
