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
