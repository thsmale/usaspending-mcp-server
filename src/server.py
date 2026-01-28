import contextlib
import logging
import os
from collections.abc import AsyncIterator
from typing import Any

import mcp.types as types
import uvicorn
from dotenv import load_dotenv
from mcp.server.lowlevel import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from pydantic import AnyUrl
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

# Import prompts
from prompts.award_type_codes import (
    prompt_award_type_codes_guide,
    prompt_message_award_type_codes_guide,
)
from prompts.general_guidance import (
    prompt_general_guidance,
    prompt_message_general_guidance,
)

# Import resources
from resources.award_type_codes import (
    award_type_groups,
    resource_award_type_codes,
)
from resources.award_type_codes import (
    resource_name as resource_name_award_type_codes,
)
from resources.toptier_agencies import (
    get_toptier_agencies,
    resource_toptier_agencies,
)
from resources.toptier_agencies import (
    resource_name as resource_name_toptier_agencies,
)

# Import tools
from tools.config import (
    # Tool handlers
    call_tool_federal_accounts,
    call_tool_list_budget_functions,
    call_tool_major_object_class,
    call_tool_recipient,
    call_tool_spending,
    call_tool_spending_by_award,
    call_tool_spending_over_time,
    call_tool_subawards,
    call_tool_toptier_agencies,
    call_tool_total_budgetary_resources,
    # Tool definitions
    tool_federal_accounts,
    tool_list_budget_functions,
    tool_major_object_class,
    tool_recipient,
    tool_spending,
    tool_spending_by_award,
    tool_spending_over_time,
    tool_subawards,
    tool_toptier_agencies,
    tool_total_budgetary_resources,
)

load_dotenv()
logger = logging.getLogger(__name__)
HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = Server("usa-spending-mcp-server")


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    if name == "federal_accounts":
        return await call_tool_federal_accounts(arguments)

    if name == "list_budget_functions":
        return await call_tool_list_budget_functions()

    if name == "major_object_class":
        return await call_tool_major_object_class(arguments)

    if name == "recipient":
        return await call_tool_recipient(arguments)

    if name == "spending":
        return await call_tool_spending(arguments)

    if name == "spending_by_award":
        return await call_tool_spending_by_award(arguments)

    if name == "spending_over_time":
        return await call_tool_spending_over_time(arguments)

    if name == "subawards":
        return await call_tool_subawards(arguments)

    if name == "total_budgetary_resources":
        return await call_tool_total_budgetary_resources(arguments)

    if name == "toptier_agencies":
        return await call_tool_toptier_agencies(arguments)

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
        tool_spending_over_time,
        tool_subawards,
        tool_total_budgetary_resources,
        tool_toptier_agencies,
    ]


@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [prompt_award_type_codes_guide, prompt_general_guidance]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    valid_prompt_names = ["award_type_codes_guide", "general_guidance"]
    if name not in valid_prompt_names:
        raise ValueError(f"Unknown prompt: {name}. Valid prompt names are {valid_prompt_names}.")

    if name == "award_type_codes_guide":
        return types.GetPromptResult(
            messages=prompt_message_award_type_codes_guide(),
            description="A Guide to using award_type_codes.",
        )

    if name == "general_guidance":
        return types.GetPromptResult(
            messages=prompt_message_general_guidance(),
            description="A general guide to using the USA spending MCP server.",
        )


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        resource_award_type_codes,
        resource_toptier_agencies,
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl):
    if uri.path is None:
        raise ValueError(f"Invalid resource path: {uri}")
    name = uri.path.replace(".json", "").lstrip("/")

    valid_resource_names = [resource_name_award_type_codes, resource_name_toptier_agencies]

    if name not in valid_resource_names:
        raise ValueError(
            f"Unknown resource: {uri}.Valid resource names are {','.join(valid_resource_names)}"
        )

    if name == resource_name_award_type_codes:
        return [ReadResourceContents(content=f"{award_type_groups}", mime_type="application/json")]

    if name == resource_name_toptier_agencies:
        return [
            ReadResourceContents(content=f"{get_toptier_agencies()}", mime_type="application/json")
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


def main():
    uvicorn.run(starlette_app, host=HOST, port=PORT)
    return 0


if __name__ == "__main__":
    main()
