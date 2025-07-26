from typing import Any, Dict

# import asyncio
from fastmcp import Client


class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8050/sse"):
        """Initialize the MCP client.

        Args:
            base_url (str): The base URL of the MCP server.

        Returns:
            None"""
        self.base_url = base_url
        self.session = None

    async def connect(self):
        """Connect to the MCP server."""
        self.session = await Client(self.base_url).__aenter__()

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None

    async def list_tools(self) -> list:
        """List available tools."""
        if not self.session:
            raise RuntimeError("Session not connected")
        return await self.session.list_tools()

    async def get_tools(self) -> list[dict[str, Any]]:
        """Retrieve tools in a format compatible with OpenAI.

        Returns:
            list[dict[str, Any]]: List of tools in OpenAI format.
        """
        if not self.session:
            raise RuntimeError("Session not connected")

        tools = await self.session.list_tools()
        openai_tools = []

        for tool in tools:
            openai_tools.append(
                {
                    "type": "function",
                    "name": tool.name,  # Accessing 'name' attribute
                    "description": tool.description,  # Accessing 'description' attribute
                    "parameters": {
                        "type": "object",
                        "properties": tool.inputSchema[
                            "properties"
                        ],  # Accessing 'input_schema' attribute
                        "required": tool.inputSchema.get(
                            "required", []
                        ),  # Accessing 'input_schema' attribute
                    },
                }
            )

        return openai_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool.

        Args:
            tool_name (str): The name of the tool to call.
            arguments (Dict[str, Any]): The arguments to pass to the tool.

        Returns:
            Any: The result of the tool call.
        """
        if not self.session:
            raise RuntimeError("Session not connected")
        result = await self.session.call_tool(tool_name, arguments)
        return result.content[0].text if result.content else None
