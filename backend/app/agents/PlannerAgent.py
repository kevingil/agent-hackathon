import logging
from utils.schemas import Plan
from openai import OpenAI
from MCP.client import MCPClient

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(
        self,
        dev_prompt,
        mcp_client,
        llm,
        messages,
        tools,
        model_name: str = "gpt-4.1-mini",
    ):
        """
        Initialize the PlannerAgent.

        Args:
            dev_prompt (str): The developer prompt.
            mcp_client (MCPClient): The MCP client.
            llm (OpenAI): The LLM client.
            messages (list[dict]): The input messages.
            tools (list[dict]): The tools.
            model_name (str): The name of the model.

        Returns:
            None
        """
        self.model_name: str = model_name
        self.dev_prompt: str = dev_prompt
        self.mcp_client: MCPClient = mcp_client
        self.llm: OpenAI = llm
        self.messages: list[dict] = messages
        self.tools: list[dict] = tools
        if self.dev_prompt:
            self.messages.append({"role": "developer", "content": self.dev_prompt})

    def create_plan(self):
        respponse = self.llm.responses.parse(
            model=self.model_name,
            input=self.messages,
            text_format=Plan,
        )
        parsed = respponse.output_parsed
        return parsed  # instance of ResponseFormat

    def run(self, query: str):
        plan = self.handle_query(query=query)
        return plan

    def handle_query(self, query: str):
        self.add_messages(query)
        return self.create_plan()

    def add_messages(self, query: str):
        """Add a message to the LLM's input messages.

        Args:
            prompt (str): The prompt to add to the LLM's input messages.

        Returns:
            None
        """
        self.messages.append({"role": "user", "content": query})
