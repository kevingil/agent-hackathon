import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from app import create_app, socketio
from app.agents.OrchestratorAgent import OrchestratorAgent
from app.agents.MCP.client import MCPClient

# Load environment variables
load_dotenv(Path("./.env"))

async def initialize_agent_service():
    """Initialize and return the OrchestratorAgent with MCP client integration."""
    # Initialize MCP client
    mcp_client = MCPClient()
    await mcp_client.connect()
    
    # Get tools from MCP
    tools = await mcp_client.get_tools()
    print(f"Loaded {len(tools)} tools from MCP")
    
    # Initialize OpenAI client
    openai_client = OpenAI()
    
    # Initialize messages with system prompt
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to various tools. "
                      "Use the available tools when needed to assist the user effectively."
        }
    ]
    
    # Initialize OrchestratorAgent
    agent = OrchestratorAgent(
        dev_prompt=("You are a helpful assistant with access to various tools. "
                   "Use the available tools when needed to assist the user effectively."),
        mcp_client=mcp_client,
        llm=openai_client,
        messages=messages,
        tools=tools,
        model_name="gpt-4.1-mini",
        max_iterations=5
    )
    
    return agent, mcp_client

async def main():
    """Main entry point for the agent service."""
    # Initialize services
    agent, mcp_client = await initialize_agent_service()
    
    try:
        # Example usage of the agent
        question = "Hello, can you help me with something?"
        
        print("Agent is ready to process messages...")
        async for chunk in agent.stream(question):
            if chunk.get('is_task_complete', False):
                print(f"\nFinal response: {chunk['content']}")
                if 'tool_history' in chunk and chunk['tool_history']:
                    print("\nTool execution history:")
                    for tool in chunk['tool_history']:
                        status = "✓" if not tool.get('isError', False) else "✗"
                        print(f"{status} {tool['tool']}({tool['arguments']}) -> {tool['result']}")
            else:
                print(chunk['content'], end='', flush=True)
    finally:
        # Clean up
        await mcp_client.disconnect()

if __name__ == '__main__':
    # Start the web application
    app = create_app()
    
    # Start the agent service in the background
    asyncio.create_task(main())
    
    # Run the web server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)