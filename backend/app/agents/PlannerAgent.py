import logging
import uuid
from openai import OpenAI # type: ignore
import json

logger = logging.getLogger(__name__)

class PlannerAgent:
    def __init__(self, dev_prompt, mcp_client, messages, tools, model_name: str = "gpt-4.1-mini"):
        self.model_name = model_name
        self.dev_prompt = dev_prompt
        self.mcp_client = mcp_client
        self.messages = messages
        self.tools = tools
        if self.dev_prompt:
            self.messages.append({"role": "developer", "content": self.dev_prompt})
        self.llm = OpenAI()  # Instantiate internally

    def add_messages(self, query: str):
        self.messages.append({"role": "user", "content": query})

    def run(self, query: str):
        self.add_messages(query)
        response = self.llm.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            tools=self.tools
        )
        # OpenAI returns tool_calls in response.choices[0].message.tool_calls
        try:
            tool_calls = response.choices[0].message.tool_calls
            # tool_calls is already a list of dicts in OpenAI format
            return {"tool_calls": tool_calls or []}
        except Exception as e:
            logger.error(f"Failed to extract tool calls: {e}")
            return {"tool_calls": []}
