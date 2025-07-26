import os
from LLM.OpenAIModel import OpenAIModel
from dotenv import load_dotenv
from pathlib import Path
from Agents.PlannerAgent import PlannerAgent
from Agents.OrchestratorAgent import OrchestratorAgent
import utils.prompts as prompts
from MCP.client import MCPClient
import asyncio

load_dotenv(Path("./.env"))


async def execute():
    mcp_client = MCPClient()  # initialize MCP client instance
    await mcp_client.connect()  # connect to mcp client
    tools = await mcp_client.get_tools()  # get tools
    print("tools: ", tools)  # print tools
    llm_model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY")).get_client()

    planner = PlannerAgent(
        dev_prompt=prompts.PLANNER_AGENT_PROMPT,
        mcp_client=mcp_client,
        llm=llm_model,
        messages=[],
        tools=tools,
    )

    orchestrator = OrchestratorAgent(
        dev_prompt=prompts.ORCHESTRATOR_AGENT_PROMPT,
        mcp_client=mcp_client,
        llm=llm_model,
        messages=[],
        tools=tools,
    )

    plan = planner.create_plan()
    orchestrator.excute(plan)
    # pass


if __name__ == "__main__":
    asyncio.run(execute())
