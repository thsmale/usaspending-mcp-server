import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any
import os

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

from dotenv import load_dotenv

# Tools
from tools.v2.budget_functions.list_budget_functions import (
    call_tool_list_budget_functions,
    tool_list_budget_functions,
)
from tools.v2.federal_accounts import (
    call_tool_federal_accounts,
    tool_federal_accounts,
)
from tools.v2.financial_spending.major_object_class import (
    call_tool_major_object_class,
    tool_major_object_class,
)
from tools.v2.recipient import (
    call_tool_recipient,
    tool_recipient,
)
from tools.v2.references.toptier_agencies import (
    call_tool_toptier_agencies,
    tool_toptier_agencies,
)
from tools.v2.references.total_budgetary_resources import (
    call_tool_total_budgetary_resources,
    tool_total_budgetary_resources,
)
from tools.v2.search.spending_by_award import (
    tool_spending_by_award,
    call_tool_spending_by_award,
)
from tools.v2.spending import (
    call_tool_spending,
    tool_spending,
)
from tools.v2.subawards import (
    call_tool_subawards,
    tool_subawards,
)

load_dotenv()
logger = logging.getLogger(__name__)
HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))


def main() -> int:
    # Configure logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("mcp-streamable-http-stateless-demo")

    @app.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[types.ContentBlock]:
        if name == "federal_accounts":
            return call_tool_federal_accounts(arguments)

        if name == "list_budget_functions":
            return call_tool_list_budget_functions()

        if name == "major_object_class":
            return call_tool_major_object_class(arguments)

        if name == "recipient":
            return call_tool_recipient(arguments)

        if name == "spending":
            return call_tool_spending(arguments)

        if name == "spending_by_award":
            return call_tool_spending_by_award(arguments)

        if name == "subawards":
            return call_tool_subawards(arguments)

        if name == "total_budgetary_resources":
            return call_tool_total_budgetary_resources(arguments)

        if name == "toptier_agencies":
            return call_tool_toptier_agencies(arguments)

        raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            tool_federal_accounts,
            tool_list_budget_functions,
            tool_major_object_class,
            tool_recipient,
            tool_spending,
            tool_spending_by_award,
            tool_subawards,
            tool_total_budgetary_resources,
            tool_toptier_agencies,
        ]

    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Wrap ASGI application with CORS middleware to expose Mcp-Session-Id header
    # for browser-based clients (ensures 500 errors get proper CORS headers)
    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],  # Allow all origins - adjust as needed for production
        allow_methods=["GET", "POST", "DELETE"],  # MCP streamable HTTP methods
        expose_headers=["Mcp-Session-Id"],
    )

    import uvicorn

    uvicorn.run(starlette_app, host=HOST, port=PORT)

    return 0


main()
