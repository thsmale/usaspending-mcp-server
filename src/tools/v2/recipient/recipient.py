from typing import Any

from mcp.types import Tool

from utils.http import HttpClient

from .recipient_schemas import (
    input_schema,
    output_schema,
)

tool_recipient = Tool(
    name="recipient",
    description=(
        "This can be used to visualize government spending that pertains to a specific recipient. "
        "This returns a list of recipients, their level, DUNS, UEI, and amount."
    ),
    inputSchema=input_schema,
    title="Recipient",
)

endpoint = "/api/v2/recipient/"


async def call_tool_recipient(arguments: dict[str, Any]):
    order = arguments.get("order")
    sort = arguments.get("sort")
    limit = arguments.get("limit")
    page = arguments.get("page")
    keyword = arguments.get("keyword")
    award_type = arguments.get("award_type")

    payload = {}
    if order is not None:
        payload["order"] = order
    if sort is not None:
        payload["sort"] = sort
    if limit is not None:
        payload["limit"] = limit
    if page is not None:
        payload["page"] = page
    if keyword is not None:
        payload["keyword"] = keyword
    if award_type is not None:
        payload["award_type"] = award_type

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=output_schema
    )
    return await post_client.send()
