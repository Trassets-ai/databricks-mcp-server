#!/bin/bash

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please create it first:"
    echo "uv venv"
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Load .env file if present and env vars are not already set
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    if [ -f ".env" ]; then
        set -a
        source .env
        set +a
    fi
fi

# Check if environment variables are set
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "Warning: DATABRICKS_HOST and/or DATABRICKS_TOKEN environment variables are not set."
    echo "The server will attempt to load them from other sources (.env, config, etc.)."
fi

# Start the server by running the module directly
echo "Starting Databricks MCP server at $(date)"
if [ -n "$DATABRICKS_HOST" ]; then
    echo "Databricks Host: $DATABRICKS_HOST"
fi

uv run -m src.server.databricks_mcp_server

echo "Server stopped at $(date)" 