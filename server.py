import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

#Tools
"""
TODO: kinda useless compared to the other endpoints, not much value at this stage, possibly add back later
from tools.v2.awards.count.federal_account.award_id import (
    tool_awards_count_federal_accounts,
    call_tool_awards_count_federal_accounts,
)
"""
from tools.v2.budget_functions.list_budget_functions import (
    call_tool_list_budget_functions,
    tool_list_budget_functions,
)
from tools.v2.federal_accounts import (
    call_tool_federal_accounts,
    tool_federal_accounts,
)
"""
TODO: rarely used, test MCP client chooses spending over this
from tools.v2.federal_obligations import (
    call_tool_federal_obligations,
    tool_federal_obligations,
)
"""
from tools.v2.financial_spending.major_object_class import (
    call_tool_major_object_class,
    tool_major_object_class,
)
from tools.v2.recipient import (
    call_tool_recipient,
    tool_recipient,
)
"""
TODO: resolve file conflict names
from tools.v2.recipient.state import (
    call_tool_state,
    tool_state,
)
"""
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
"""
TODO: with test mcp-client only this tool is invoked
from tools.v2.search.spending_by_geography import (
    tool_spending_by_geography,
    call_tool_spending_by_geography,
)
"""
from tools.v2.spending import (
    call_tool_spending,
    tool_spending,
)
from tools.v2.subawards import (
    call_tool_subawards,
    tool_subawards,
)
"""
TODO: don't see this endpoint called on the USA Spending website, tool almost never invoked.
from tools.v2.transactions import (
    call_tool_transactions,
    tool_transactions,
)
"""

logger = logging.getLogger(__name__)

def main() -> int:
    # Configure logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("mcp-streamable-http-stateless-demo")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """
        TODO: add back later, not much value atm
        if name == 'awards_count_federal_accounts':
            return call_tool_awards_count_federal_accounts(arguments)
        """

        if name == 'federal_accounts':
            return call_tool_federal_accounts(arguments)

        """
        TODO: Not really needed, spending tool is invoked over this
        if name == 'federal_obligations':
            return call_tool_federal_obligations(arguments)
        """
        
        if name == 'list_budget_functions':
            return call_tool_list_budget_functions()

        if name == 'major_object_class':
            return call_tool_major_object_class(arguments)
        
        if name == 'recipient':
            return call_tool_recipient(arguments)

        """
        TODO: Resolve file conflict names
        if name == 'state':
            return call_tool_state()
        """

        if name == 'spending':
            return call_tool_spending(arguments)

        if name == 'spending_by_award':
            return call_tool_spending_by_award(arguments)

        """
        TODO: for test/mcp-client need to update tool descriptions because this will be the only tool invoked no matter what
        if name == 'spending_by_geography':
            return call_tool_spending_by_geography(arguments)
        """

        if name == 'subawards':
            return call_tool_subawards(arguments)

        if name == 'total_budgetary_resources':
            return call_tool_total_budgetary_resources(arguments)

        if name == 'toptier_agencies':
            return call_tool_toptier_agencies(arguments)
        
        """
        TODO: Haven't found anywhere this is called on the website, Tool never invoked
        if name == 'transactions':
            return call_tool_transactions(arguments)
        """
        
        raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            # tool_awards_count_federal_accounts, TODO: add back later if there is demand
            tool_federal_accounts,
            # tool_federal_obligations, TODO: spending invoked mostly over this
            tool_list_budget_functions,
            tool_major_object_class,
            tool_recipient,
            #tool_state, TODO: resolve file conflict names
            tool_spending,
            tool_spending_by_award,
            #tool_spending_by_geography, TODO: with test/mcp-client it only invokes this tool even for simple hello world message
            tool_subawards,
            tool_total_budgetary_resources,
            tool_toptier_agencies,
            # tool_transactions, Don't see it used on the website, Tool rarely invoked.
        ]


    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        stateless=True,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
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

    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)

    return 0

main()
