# OrderMail Agent

This project features an agentic workflow for automated email order processing and customer service.


![Order Processing Agent Screenshot](screenshot/Xnip2025-07-26_22-27-36.png)



## Tech Stack
- Python (asyncio, Flask, SQLAlchemy)
- OpenAI (LLM extraction and reasoning)
- Agentic orchestration (custom OrchestratorAgent)
- MCP tool server for inventory/order actions
- PostgreSQL database


## Main Commands (from backend/Makefile)
- `make install` — Install backend dependencies
- `make run` — Start the Flask backend
- `make mcp` — Start the MCP tool server
- `make agent` — Run the agent workflow to process test emails

