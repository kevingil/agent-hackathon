import asyncio
from collections.abc import AsyncGenerator
from openai import OpenAI # type: ignore
from .MCP.client import MCPClient
from typing import Any, Optional
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
        """Select the agent to use. Instantiate with required params, no LLM client passed."""
        if agent_name == "OrchestratorAgent":
            agent = OrchestratorAgent(self.dev_prompt, self.mcp_client, [], self.tools, self.model_name)
        elif agent_name == "PlannerAgent":
            from .PlannerAgent import PlannerAgent
            agent = PlannerAgent(self.dev_prompt, self.mcp_client, [], self.tools, self.model_name)
        elif agent_name == "ToolAgent":
            agent = OrchestratorAgent(self.dev_prompt, self.mcp_client, [], self.tools, self.model_name)
        elif agent_name == "ExecutorAgent":
            agent = OrchestratorAgent(self.dev_prompt, self.mcp_client, [], self.tools, self.model_name)
        else:
            agent = f"No available agent found with name: {agent_name}"
        return agent

    def execute(self, plan: Any):
        """Execute the plan.

        Args:
            plan (Plan): The plan to execute.

        Returns:
            None
        """
        responses: dict = {}
        for i in range(len(plan)):
            task: Any = plan[i]
            agent_name = task.assigned_agent
            agent = self.select_agent(agent_name)

            response = agent.execute_task(task)
            responses[agent_name] = response
        pass

    async def stream_llm(self, prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
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
        """
        Extract tool calls from the response and convert to internal format.
        Handles:
        - List of tool call objects (OpenAI or dict)
        - Dict with 'tool_calls' key
        - String (try to parse as JSON)
        Adds detailed debugging output for every step and error.
        """
        import json
        print(f"[extract_tools] Type of response: {type(response)}")
        print(f"[extract_tools] Repr of response: {repr(response)[:500]}")
        if not response:
            print("[extract_tools] No response received")
            return "No response received"
        # If response is a list of tool calls (OpenAI objects or dicts), process directly
        if isinstance(response, list):
            print(f"[extract_tools] Response is a list with {len(response)} items.")
            tool_calls = response
        # If response is a dict with 'tool_calls'
        elif isinstance(response, dict) and 'tool_calls' in response:
            print("[extract_tools] Response is a dict with 'tool_calls' key.")
            tool_calls = response['tool_calls']
        # If response is a string, try to parse as JSON
        elif isinstance(response, str):
            # Defensive: if it's a Python repr of tool call objects, don't try to parse as JSON
            if response.strip().startswith("[") and "ChatCompletionMessageToolCall" in response:
                print("[extract_tools] WARNING: Response is a string repr of tool call objects, not JSON. This is a bug upstream.")
                return "Tool calls were passed as a string repr, not as objects. Pass the actual list of tool call objects."
            try:
                print(f"[extract_tools] Attempting to parse string as JSON: {response[:200]}")
                data = json.loads(response)
                tool_calls = data['tool_calls'] if 'tool_calls' in data else data
            except Exception as e:
                print(f"[extract_tools] ERROR: Failed to parse response as JSON: {e}")
                print(f"[extract_tools] Offending string: {response[:500]}")
                return f"Failed to parse response as JSON: {e}"
        # If response has .text, try to parse as JSON
        elif hasattr(response, 'text'):
            try:
                print(f"[extract_tools] Attempting to parse response.text as JSON: {response.text[:200]}")
                data = json.loads(response.text)
                tool_calls = data['tool_calls'] if 'tool_calls' in data else data
            except Exception as e:
                print(f"[extract_tools] ERROR: Failed to parse response.text as JSON: {e}")
                print(f"[extract_tools] Offending string: {getattr(response, 'text', '')[:500]}")
                return f"Failed to parse response.text as JSON: {e}"
        else:
            print(f"[extract_tools] Unsupported response type: {type(response)}")
            return "Unsupported response type for tool extraction"
        # Now process tool_calls (should be a list)
        if not tool_calls or not isinstance(tool_calls, list):
            print(f"[extract_tools] No tool_calls found or not a list. tool_calls: {repr(tool_calls)}")
            return "No tool_calls found in response"
        print(f"[extract_tools] Extracting {len(tool_calls)} tool calls...")
        internal_calls = []
        for i, call in enumerate(tool_calls):
            print(f"[extract_tools] Tool call {i} type: {type(call)} dir: {dir(call)}")
            # OpenAI object: has attribute 'function'
            if hasattr(call, 'function'):
                fn = call.function
                name = getattr(fn, 'name', None)
                args = getattr(fn, 'arguments', '{}')
            # Dict fallback
            elif isinstance(call, dict):
                fn = call.get('function', {})
                name = fn.get('name')
                args = fn.get('arguments', '{}')
            else:
                print(f"[extract_tools] Tool call {i} is neither OpenAI object nor dict: {repr(call)}")
                continue
            try:
                arguments = json.loads(args) if isinstance(args, str) else (args if args is not None else {})
            except Exception as e:
                print(f"[extract_tools] ERROR: Failed to parse arguments for tool call {i}: {e}")
                print(f"[extract_tools] Offending args: {args}")
                arguments = {}
            if not name:
                print(f"[extract_tools] Tool call {i} missing name: {repr(fn)}")
                continue
            print(f"[extract_tools] Tool call {i}: name={name}, arguments={arguments}")
            internal_calls.append({'name': name, 'arguments': arguments})
        if not internal_calls:
            print("[extract_tools] No valid tool calls found after extraction.")
            return "No valid tool calls found"
        print(f"[extract_tools] Successfully extracted {len(internal_calls)} tool calls.")
        return internal_calls

    async def decide(self, question: str, called_tools: list[dict] | None = None) -> AsyncGenerator[list, None]:
        """
        Prompt the PlannerAgent and yield the tool call response as a list (not JSON string).
        """
        try:
            from .PlannerAgent import PlannerAgent
            planner = PlannerAgent(self.dev_prompt, self.mcp_client, [], self.tools, self.model_name)
            result = planner.run(question)
            # Directly yield the tool_calls list (may be OpenAI objects)
            yield result.get('tool_calls', [])
        except Exception as e:
            error_msg = f"Error in decide: {str(e)}"
            print(error_msg)
            yield []

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
        """Stream the process of answering a question, possibly involving tool calls."""
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
            tool_call_list = None
            async for chunk in self.decide(question, called_tools):
                # If decide yields a list (tool calls), use it directly
                if isinstance(chunk, list):
                    tool_call_list = chunk
                else:
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
            # For logging, print the raw response
            if tool_call_list is not None:
                print("\n📝 Raw response (tool call objects):")
                print(tool_call_list)
            else:
                response = ''.join(response_chunks)
                print("\n📝 Raw response:")
                print(response)
            # Extract tools from response
            print("\n🛠️  Extracting tools...")
            # Pass the actual tool call objects if available
            tools = self.extract_tools(tool_call_list if tool_call_list is not None else response)
            print(f"[stream] Passed to extract_tools: {type(tool_call_list) if tool_call_list is not None else type(response)}")
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
            called_tools_history = {"question": question, "tools": [], "called_tools": called_tools}
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
