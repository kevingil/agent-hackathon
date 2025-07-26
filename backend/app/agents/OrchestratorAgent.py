from collections.abc import AsyncGenerator
from openai import OpenAI
from .MCP.client import MCPClient
from .utils.schemas import (
    CalledToolHistoryResponse, 
    DecideResposnse,
    Plan, 
    PlannerTask
)
from typing import Any

# import asyncio
import json


class OrchestratorAgent:
    """
    OrchestratorAgent class.
    Methods:
        stream_llm(): Stream LLM response.
        add_messages(): Add a message to the LLM's input messages.
        decide(): Decide which tool to use to answer the question.
        stream(): Stream the process of answering a question, possibly involving tool calls.
        extract_tools(): Extract the tool calls from the response.
        call_tool(): Call the tool.

    Attributes:
        model_name (str): The name of the model.
        dev_prompt (str): The developer prompt.
        mcp_client (MCPClient): The MCP client.
        llm (OpenAI): The LLM client.
        messages (list[dict]): The input messages.
        tools (list[dict]): The tools.

    """

    def __init__(
        self,
        dev_prompt: str,
        mcp_client: MCPClient,
        llm: OpenAI,
        messages: list[dict],
        tools: list[dict],
        model_name: str = "gpt-4.1-mini",
    ):
        """
        Initialize the OrchestratorAgent.

        Args:
            dev_prompt (str): The developer prompt.
            mcp_client (MCPClient): The MCP client.
            llm (OpenAI): The LLM client.
            messages (list[dict]): The input messages.
            max_turns (int): The maximum number of turns.
            tools (list[dict]): The tools.
            model_name (str): The name of the model.
        """
        self.model_name = model_name
        self.dev_prompt = dev_prompt
        self.mcp_client = mcp_client
        self.llm = llm
        self.messages = messages
        self.tools = tools
        if self.dev_prompt:
            self.messages.append({"role": "developer", "content": self.dev_prompt})

    def select_agent(self, agent_name: str) -> Any | str:
        """Select the agent to use.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            The agent.
        """
        if agent_name == "OrchestratorAgent":
            agent = OrchestratorAgent()
        elif agent_name == "PlannerAgent":
            agent = OrchestratorAgent()
        elif agent_name == "ToolAgent":
            agent = OrchestratorAgent()
        elif agent_name == "ExecutorAgent":
            agent = OrchestratorAgent()
        else:
            agent = f"No available agent found with name: {agent_name}"
        return agent

    def execute(self, plan: Plan):
        """Execute the plan.

        Args:
            plan (Plan): The plan to execute.

        Returns:
            None
        """
        responses: dict = {}
        for i in range(len(plan)):
            task: PlannerTask = plan[i]
            agent_name = task.assigned_agent
            agent = self.select_agent(agent_name)

            response = agent.execute_task(task)
            responses[agent_name] = response
        pass

    def stream_llm(self):
        """Stream LLM response.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            Generator[str, None, None]: A generator of the LLM response.
        """
        stream = self.llm.responses.create(
            model=self.model_name, input=self.messages, stream=True
        )
        for event in stream:
            yield event

    def add_messages(self, query: str):
        """Add a message to the LLM's input messages.

        Args:
            prompt (str): The prompt to add to the LLM's input messages.

        Returns:
            None
        """
        self.messages.append({"role": "user", "content": query})

    async def call_tool(self, tool_calls: list[dict]) -> list[dict]:
        """Recives a list of tool calls and calls the tools

        Args:
            tools (list[dict]): The tools to call.

        REturns:
            list[dict]: The results of the tool calls.
        """
        results = []
        for i in range(len(tool_calls)):  # for each tool
            name = tool_calls[i]["name"]  # get name
            args = tool_calls[i]["arguments"]  # get arguments
            result = await self.mcp_client.call_tool(name, args)  # call tool
            results.append({"name": name, "result": result})  # append result to list
        return results

    def extract_tools(self, response: str) -> list[dict] | str:
        """Extract the tool calls from the response. Create a tool call list containing tool name and arguments

        Args:
            response (str): The response from the LLM.

        Returns:
            list[dict]: List of tools | str
        """
        tool_calls: list[dict] = []
        for tool_call in response.output:
            if tool_call.type != "function_call":
                continue
            # select tool name
            name = tool_call.name
            # get the arguments for the tool
            args = json.loads(tool_call.arguments)

            tool_calls.append({"name": name, "arguments": args})
        if not tool_calls:
            return "No tools called"
        return tool_calls

    async def decide(self, question: str, called_tools: list[dict] | None = None):
        """Decide which tool to use to answer the question.

        Args:
            question (str): The question to answer.
            called_tools (list[dict]): The tools that have been called.
        """
        tools = await self.mcp_client.get_tools()  # get list of tools
        if called_tools:  # we have had previos tool calls format it
            called_tools_prompt = CalledToolHistoryResponse(
                question=question, tools=tools, called_tools=called_tools
            )
        else:
            called_tools_prompt = ""  # else just pass an empty string

        prompt = DecideResposnse.render(
            question=question,
            tool_prompt=tools,
            called_tools=called_tools_prompt,
        )

        self.add_messages(prompt)  # add the prompt to the messages
        return self.stream_llm(prompt)  # return the model call

    async def stream(self, question: str) -> AsyncGenerator[str]:
        """Stream the process of answering a question, possibly involving tool calls.

        Args:
            question (str): The question to answer.

        Yields:
            dict: Streaming output, including intermediate steps and final result.
        """
        called_tools = []
        for i in range(10):
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": f"Step {i}",
            }

            response = ""
            for chunk in await self.decide(question, called_tools):
                response += chunk
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": chunk,
                }
            tools = self.extract_tools(response)

            if not tools:
                break
            results = await self.call_tool(tools)

            for i in range(len(results)):
                called_tools.append(
                    {
                        "tool": tools[i]["name"],
                        "arguments": tools[i]["arguments"],
                        "isError": results[i].isError,
                        "result": results[i].content[0].text,
                    }
                )

            called_tools_history = CalledToolHistoryResponse(
                question=question,
                tools="",
                called_tools=called_tools,
            )

            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": called_tools_history,
            }

        yield {
            "is_task_complete": True,
            "require_user_input": False,
            "content": "Task completed",
        }
