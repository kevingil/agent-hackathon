from typing import Any, Dict, Optional, Union
from fastmcp import FastMCP, Client
from contextlib import asynccontextmanager

class MCPClient:
    def __init__(self, config: Union[str, dict] = "http://localhost:8050/sse"):
        """Initialize the MCP client.

        Args:
            config (Union[str, dict]): Either a URL string or a configuration dictionary.
                If string: Treated as the URL of the MCP server.
                If dict: Should follow the MCP configuration format with 'mcpServers' key.
        """
        self.config = config
        self._client = None
        self._is_connected = False

    async def connect(self):
        """Connect to the MCP server(s)."""
        if self._is_connected:
            return

        if isinstance(self.config, str):
            # Single server mode - pass the URL directly to Client
            self._client = Client({
                "mcpServers": [{
                    "name": "default",
                    "url": self.config
                }]
            })
        else:
            # Configuration mode with multiple servers
            self._client = Client(self.config)

        await self._client.__aenter__()
        self._is_connected = True

    async def disconnect(self):
        """Disconnect from the MCP server(s)."""
        if self._is_connected and self._client:
            await self._client.__aexit__(None, None, None)
            self._is_connected = False
            self._client = None

    @asynccontextmanager
    async def session(self):
        """Context manager for session management."""
        try:
            await self.connect()
            yield self
        finally:
            await self.disconnect()

    async def list_servers(self) -> list:
        """List available MCP servers."""
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")
        return list(self._client.servers.keys())

    async def list_tools(self, server: str = None) -> list:
        """List available tools.
        
        Args:
            server (str, optional): Specific server to list tools from. 
                                  If None, lists tools from all servers.
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")
        return await self._client.list_tools(server)

    async def get_tools(self, server: str = None) -> list[dict[str, Any]]:
        """Retrieve tools in a format compatible with OpenAI.

        Args:
            server (str, optional): Specific server to get tools from.
                                 If None, gets tools from all servers.

        Returns:
            list[dict[str, Any]]: List of tools in OpenAI format.
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")

        tools = await self.list_tools(server)
        openai_tools = []

        for tool in tools:
            openai_tools.append(
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.inputSchema.get("properties", {}),
                        "required": tool.inputSchema.get("required", []),
                    },
                }
            )

        return openai_tools

    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any], 
        server: str = None
    ) -> Any:
        """Call a tool.

        Args:
            tool_name (str): The name of the tool to call.
            arguments (Dict[str, Any]): The arguments to pass to the tool.
            server (str, optional): Specific server to call the tool on.
                                 If None, the client will try to find the tool
                                 in any of the available servers.

        Returns:
            Any: The result of the tool call.
        """
        if not self._is_connected:
            raise RuntimeError("Not connected to MCP server(s)")
            
        result = await self._client.call_tool(tool_name, arguments, server)
        return result.content[0].text if result.content else None
