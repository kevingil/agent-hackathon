# Simple Makefile for backend application

# Variables
PORT?=8080
HOST?=0.0.0.0

# Install dependencies
.PHONY: install
install:
	@echo "Installing dependencies..."
	uv pip install -r requirements.txt

# Run the application
.PHONY: run
run:
	@echo "Starting application..."
	FLASK_APP=run.py FLASK_ENV=development flask run --host=${HOST} --port=${PORT}

# Run agent workflow to process test emails and place orders
.PHONY: agent
agent:
	@echo "Starting agent workflow to process test emails..."
	PYTHONPATH=. python -m app.agents.process_emails

# Start the MCP server
.PHONY: mcp
mcp:
	@echo "Starting MCP server..."
	PYTHONPATH=. python -m app.agents.MCP.server
