#!/usr/bin/env bash

echo "Starting CodeMash 2026 MCP Server..."

cd /workspace
export PYTHONPATH=/workspace/src:$PYTHONPATH
uvicorn --factory \
    --host 0.0.0.0 \
    --port 8000 \
    --proxy-headers \
    --no-server-header \
    codemash_mcp:server.host