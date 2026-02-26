from typing import Any

from mcp.types import Tool

from utils.http import HttpClient

from .federal_accounts_schemas import (
    input_schema,
    output_schema,
)

tool_federal_accounts = Tool(
    name="federal_accounts",
    description=(
        "The government has more than 2,000 unique Federal Accounts, "
        "which are similar to bank accounts. "
        "Use this tool to get a better understanding of how agencies receive "
        "and spend congressional funding to carry out their programs, projects, and activities."
    ),
    inputSchema=input_schema,
    title="Federal Accounts",
)

endpoint = "/api/v2/federal_accounts/"


async def call_tool_federal_accounts(arguments: dict[str, Any]):
    filters = arguments.get("filters")
    sort = arguments.get("sort")
    limit = arguments.get("limit", 5)
    page = arguments.get("page")
    keyword = arguments.get("keyword")

    payload = {}
    if bool(filters):
        payload["filters"] = filters
    if bool(sort):
        payload["sort"] = sort
    if limit is not None:
        payload["limit"] = limit
    if page is not None:
        payload["page"] = page
    if keyword is not None:
        payload["keyword"] = keyword

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=output_schema
    )
    return await post_client.send()
