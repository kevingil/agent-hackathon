import asyncio
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

    async def call_tool(self, tool_calls) -> list[dict]:
        """Receives a list of tool calls and calls the tools

        Args:
            tool_calls: Either a list of tool call dicts or a string error message

        Returns:
            list[dict]: The results of the tool calls or error information
        """
        # If we received an error message instead of tool calls
        if isinstance(tool_calls, str):
            return [{"error": True, "message": tool_calls}]
            
        # Ensure tool_calls is a list
        if not isinstance(tool_calls, list):
            return [{"error": True, "message": f"Expected list of tool calls, got {type(tool_calls).__name__}"}]

        results = []
        for tool in tool_calls:  # for each tool
            try:
                if not isinstance(tool, dict):
                    results.append({"error": True, "message": f"Expected dict, got {type(tool).__name__}"})
                    continue
                    
                name = tool.get("name")
                args = tool.get("arguments", {})
                
                if not name:
                    results.append({"error": True, "message": "Tool call missing 'name' field"})
                    continue
                    
                # Call the tool through MCP client
                result = await self.mcp_client.call_tool(name, args)
                results.append({
                    "name": name,
                    "arguments": args,
                    "result": result,
                    "error": False
                })
                
            except Exception as e:
                results.append({
                    "error": True,
                    "name": name if 'name' in locals() else "unknown",
                    "message": f"Error calling tool: {str(e)}"
                })
                
        return results

    def extract_tools(self, response) -> list[dict] | str:
        """Extract the tool calls from the response.

        Args:
            response: The response from the LLM (could be string, object with text attribute, or event object)

        Returns:
            list[dict] | str: List of tool call dicts or error message string
        """
        if not response:
            return "No response received"

        response_text = None
        
        # Handle different response types
        if hasattr(response, 'part') and hasattr(response.part, 'text'):
            # Handle event object with part.text
            response_text = response.part.text
        elif hasattr(response, 'text'):
            # Handle simple object with text attribute
            response_text = response.text
        elif isinstance(response, str):
            # Handle direct string response
            response_text = response
        else:
            # Try to convert to string as last resort
            response_text = str(response)
            
        # If we still don't have text to process
        if not response_text:
            return "No valid response text found"
            
        # If the response is already a list of tool calls in OpenAI format, return it
        if isinstance(response_text, list) and all(isinstance(x, dict) and 'function' in x for x in response_text):
            # Convert to the format expected by call_tool
            return [{
                'name': call['function']['name'],
                'arguments': json.loads(call['function']['arguments']) if call['function'].get('arguments') else {}
            } for call in response_text]

        # If the response is a string that looks like JSON, try to parse it
        if isinstance(response_text, str):
            response_text = response_text.strip()
            
            # First, try to find and extract the innermost JSON object
            json_objects = []
            stack = []
            start_index = -1
            
            for i, char in enumerate(response_text):
                if char == '{':
                    if not stack:
                        start_index = i
                    stack.append(char)
                elif char == '}':
                    if stack:
                        stack.pop()
                        if not stack and start_index != -1:
                            json_objects.append(response_text[start_index:i+1])
                            start_index = -1
            
            # Process all found JSON objects
            for json_str in reversed(json_objects):  # Try most recent (deepest) JSON first
                try:
                    response_data = json.loads(json_str)
                    
                    # Handle OpenAI tool calls format
                    if 'tool_calls' in response_data:
                        return [{
                            'name': call['function']['name'],
                            'arguments': json.loads(call['function']['arguments']) if call['function'].get('arguments') else {}
                        } for call in response_data['tool_calls']]
                    
                    # Handle direct function calls format
                    if 'function' in response_data and 'name' in response_data['function']:
                        return [{
                            'name': response_data['function']['name'],
                            'arguments': json.loads(response_data['function']['arguments']) 
                                        if response_data['function'].get('arguments') 
                                        else {}
                        }]
                        
                    # Handle legacy formats for backward compatibility
                    if 'selected_tools' in response_data and 'thoughts' in response_data:
                        tool_names = response_data.get('selected_tools', [])
                        if tool_names:  # Only return if we actually have tools
                            return [{'name': name, 'arguments': {}} for name in tool_names]
                    
                    if 'tools' in response_data and response_data['tools']:
                        return response_data['tools']
                        
                    if 'name' in response_data:
                        return [response_data]
                        
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Error processing JSON: {str(e)}")
                    continue
            
            # If we get here, no valid JSON was found - try regex as fallback
            try:
                import re
                # Match both new and old formats
                tool_pattern = r'(?:\"name\"\s*:\s*\"([^\"]+)\"[^}]*\"arguments\"\s*:\s*({[^}]*})|\"function\"\s*:\s*{\s*\"name\"\s*:\s*\"([^\"]+)\"[^}]*\"arguments\"\s*:\s*\"({[^\"]*})\"|\b(\w+)\s*\(([^)]*)\))'
                matches = re.finditer(tool_pattern, response_text)
                
                tool_calls = []
                for match in matches:
                    try:
                        args = {}
                        # Try new format first (function/name/arguments)
                        if match.group(3) and match.group(4):
                            name = match.group(3)
                            args_str = match.group(4).replace('\\\"', '\"')
                            try:
                                args = json.loads(args_str) if args_str.strip() else {}
                            except json.JSONDecodeError:
                                # If not valid JSON, try to parse as key=value pairs
                                for pair in re.findall(r'\"?([\w_]+)\"?\s*:\s*\"?([^\",}]+)\"?', args_str):
                                    args[pair[0]] = pair[1].strip('\"\\\'')
                        # Fall back to old format
                        elif match.group(1) and match.group(2):
                            name = match.group(1)
                            args_str = match.group(2)
                            try:
                                args = json.loads(args_str) if args_str.strip() else {}
                            except json.JSONDecodeError:
                                # If not valid JSON, try to parse as key=value pairs
                                for pair in re.findall(r'\"?([\w_]+)\"?\s*:\s*\"?([^\",}]+)\"?', args_str):
                                    args[pair[0]] = pair[1].strip('\"\\\'')
                        # Try simple function call format: function_name(arg1=val1, arg2=val2)
                        elif match.group(5) and match.group(6):
                            name = match.group(5)
                            args_str = match.group(6)
                            for pair in re.findall(r'([\w_]+)\s*=\s*([^,)]+)', args_str):
                                args[pair[0]] = pair[1].strip('\"\\\'')
                        else:
                            continue
                            
                        tool_calls.append({
                            'name': name,
                            'arguments': args
                        })
                    except Exception as e:
                        print(f"Error parsing tool call: {str(e)}")
                        continue
                
                if tool_calls:
                    return tool_calls
                    
            except Exception as e:
                print(f"Error in regex extraction: {str(e)}")
                
        return "No tools called or could not parse tool calls"

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
            print(f"Error in decide: {str(e)}")
            yield f"Error: {str(e)}"

    def _format_tool_call(self, tool_call: dict) -> str:
        """Format a tool call for debug output."""
        name = tool_call.get('name', 'unknown')
        args = tool_call.get('arguments', {})
        args_str = ', '.join(f"{k}={v}" for k, v in args.items()) if args else 'no arguments'
        return f"{name}({args_str})"

    def _format_tool_result(self, result: dict) -> str:
        """Format a tool result for debug output."""
        if isinstance(result, str):
            return f"Error: {result}"
        
        error = result.get('error', False)
        name = result.get('name', 'unknown')
        result_text = result.get('result', 'No result')
        
        if error:
            return f"❌ {name} failed: {result_text}"
        return f"✅ {name} succeeded: {result_text}"

    async def stream(self, question: str) -> AsyncGenerator[dict, None]:
        """Stream the process of answering a question, possibly involving tool calls.

        Args:
            question (str): The question to answer.

        Yields:
            dict: Streaming output, including intermediate steps and final result.
        """
        called_tools = []
        for i in range(10):
            # Print step header
            step_header = f"\n{'='*80}\nStep {i+1}\n{'='*80}"
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": step_header,
            }
            print(step_header)

            # Collect response chunks
            response_chunks = []
            print("\n🤖 Processing response...")
            async for chunk in self.decide(question, called_tools):
                # Extract text from ResponseCreatedEvent if needed
                chunk_text = getattr(chunk, 'text', str(chunk))
                response_chunks.append(chunk_text)
                
                # Only yield non-empty chunks
                if chunk_text.strip():
                    yield {
                        "is_task_complete": False,
                        "require_user_input": False,
                        "content": chunk_text,
                    }
                
            # Join all response chunks for tool extraction
            response = ''.join(response_chunks)
            print("\n📝 Raw response:")
            print(response)
            
            # Extract tools from response
            print("\n🛠️  Extracting tools...")
            tools = self.extract_tools(response)
            
            if isinstance(tools, str):
                # Handle error case
                error_msg = f"Error extracting tools: {tools}"
                print(f"❌ {error_msg}")
                called_tools.append({
                    "tool": "orchestrator",
                    "arguments": {},
                    "isError": True,
                    "result": error_msg
                })
                break
                
            if not tools:
                print("ℹ️  No tools found in response. Assuming task is complete.")
                break
                
            # Print tool calls
            print("\n🔧 Tool calls:")
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {self._format_tool_call(tool)}")
            
            # Call the tools
            print("\n🚀 Executing tool calls...")
            results = await self.call_tool(tools)
            
            # Process the results
            print("\n📋 Tool results:")
            for i, (tool, result) in enumerate(zip(tools, results)):
                # Handle both string error messages and structured results
                if isinstance(result, str):
                    result_text = result
                    is_error = True
                else:
                    # Handle different result formats
                    if hasattr(result, 'content') and result.content:
                        if isinstance(result.content, list) and hasattr(result.content[0], 'text'):
                            result_text = result.content[0].text
                        else:
                            result_text = str(result.content[0]) if result.content else str(result)
                    else:
                        result_text = str(result)
                    
                    is_error = result.get('error', False) if isinstance(result, dict) else False
                
                # Get tool info
                tool_name = tool.get('name', f'tool_{i}')
                
                # Print formatted result
                result_display = self._format_tool_result({
                    'name': tool_name,
                    'error': is_error,
                    'result': result_text[:200] + ('...' if len(result_text) > 200 else '')
                })
                print(f"{i+1}. {result_display}")
                
                # Store in called_tools
                called_tools.append({
                    "tool": tool_name,
                    "arguments": tool.get('arguments', {}),
                    "isError": is_error,
                    "result": result_text,
                })

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
