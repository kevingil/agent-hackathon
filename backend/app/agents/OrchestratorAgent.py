from collections.abc import AsyncGenerator
from openai import OpenAI
from .MCP.client import MCPClient
from app.agents.utils.schemas import (
    CalledToolHistoryResponse, 
    Plan, 
    PlannerTask
)
from typing import Any
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

    async def stream_llm(self, prompt: str = None) -> AsyncGenerator[str, None]:
        """Stream LLM response.

        Args:
            prompt (str, optional): The prompt to add to messages before streaming.
                                 If None, uses existing messages.

        Yields:
            str: Chunks of the LLM response.
        """
        try:
            # Add the prompt to messages if provided
            if prompt is not None:
                self.add_messages(prompt)
                
            # Create the streaming response
            stream = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.llm.responses.create(
                    model=self.model_name,
                    input=self.messages,
                    stream=True
                )
            )
            
            # Stream the response
            for event in stream:
                yield event.text if hasattr(event, 'text') else str(event)
                
        except Exception as e:
            print(f"Error in stream_llm: {str(e)}")
            yield f"Error: {str(e)}"

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

    async def decide(self, question: str, called_tools: list[dict] | None = None) -> AsyncGenerator[str, None]:
        """Decide which tool to use to answer the question.

        Args:
            question (str): The question to answer.
            called_tools (list[dict]): The tools that have been called.

        Yields:
            str: Chunks of the LLM response.
        """
        try:
            tools = await self.mcp_client.get_tools()  # get list of tools
            if called_tools:  # we have had previous tool calls format it
                called_tools_prompt = CalledToolHistoryResponse(
                    question=question, tools=tools, called_tools=called_tools
                )
            else:
                called_tools_prompt = []  # else pass an empty list

            from app.agents.utils.schemas import DecideResponse
            prompt = DecideResponse.render(
                tools=tools,
                question=question,
                called_tools=called_tools_prompt,
            )

            self.add_messages(prompt)  # add the prompt to the messages
            
            # Stream the LLM response
            async for chunk in self.stream_llm(prompt):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error in decide: {str(e)}")
            yield f"Error: {str(e)}"

    async def stream(self, question: str) -> AsyncGenerator[dict, None]:
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

            response_chunks = []
            async for chunk in self.decide(question, called_tools):
                # Extract text from ResponseCreatedEvent if needed
                chunk_text = getattr(chunk, 'text', str(chunk))
                response_chunks.append(chunk_text)
                
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": chunk_text,
                }
                
            # Join all response chunks for tool extraction
            response = ''.join(response_chunks)
            tools = self.extract_tools(response)

            if not tools:
                break
                
            results = await self.call_tool(tools)

            for i in range(len(results)):
                result_text = ''
                if hasattr(results[i], 'content') and results[i].content:
                    result_text = results[i].content[0].text if hasattr(results[i].content[0], 'text') else str(results[i].content[0])
                    
                called_tools.append(
                    {
                        "tool": tools[i].get("name", "unknown"),
                        "arguments": tools[i].get("arguments", {}),
                        "isError": getattr(results[i], 'isError', False),
                        "result": result_text,
                    }
                )

            called_tools_history = CalledToolHistoryResponse(
                question=question,
                tools=[],
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
