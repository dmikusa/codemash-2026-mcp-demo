from fastmcp import Client
import pytest

from codemash_mcp.server import _init_mcp_server
from starlette.routing import Route
from starlette.testclient import TestClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def server(monkeypatch):
    # Set required environment variables for codemash config
    monkeypatch.setenv("CODEMASH_DATA_FILE", "data/test-data.json")

    # Import and create a custom server MCP object
    server = _init_mcp_server()
    return server


class TestMcpServer:
    @pytest.mark.anyio
    async def test_should_list_tools(self, server):
        mcp_client = Client(server.test())
        async with mcp_client as client:
            tools = [t.name for t in await client.list_tools()]
            assert {
                "event",
                "hotels",
                "speakers",
                "sessions",
                "rooms",
                "tracks",
                "venue",
            }.issubset(tools)

    @pytest.mark.anyio
    async def test_custom_route_with_mcp_context_returns_ok(self, server):
        server_app = server.test().http_app()

        route = [
            r for r in server_app.routes if isinstance(r, Route) and r.path == "/health"
        ]
        assert len(route) == 1
        assert route[0].methods == {"GET", "HEAD"}

        client = TestClient(server_app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}
