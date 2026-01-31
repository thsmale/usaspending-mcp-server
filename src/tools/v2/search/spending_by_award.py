from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

from .spending_by_award_schemas import (
    input_schema,
    output_schema,
)

"""
We are going to take a different approach for this tool versus spending_by_geography.
I am not adding every single filter property.
Since I am worried a more complex input schema may overwhelm the LLM.
Weird, initially I didn't event supply recipient_search_text.
Regardless, the LLM still tried to use it in a query so I added it.
"""
tool_spending_by_award = Tool(
    name="spending_by_award",
    description=(
        "This allows for complex filtering for specific subsets of spending data. "
        "This accepts filters and fields, and returns the fields of the filtered awards."
    ),
    inputSchema=input_schema,
    title="Spending by Award",
)


async def call_tool_spending_by_award(arguments: dict[str, Any]):
    endpoint = "/api/v2/search/spending_by_award/"
    filters = arguments.get("filters")
    fields = arguments.get("fields")
    limit = arguments.get("limit")
    order = arguments.get("order")
    page = arguments.get("page")
    sort = arguments.get("sort")
    subawards = arguments.get("subawards")
    spending_level = arguments.get("spending_level")

    if not bool(filters):
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="filters must be provided.",
            )
        )
    if fields is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="fields must be provided.",
            )
        )

    payload = {
        "filters": filters,
        "fields": fields,
    }

    if limit is not None:
        payload["limit"] = limit
    if order is not None:
        payload["order"] = order
    if page is not None:
        payload["page"] = page
    if sort is not None:
        payload["sort"] = sort
    if subawards is not None:
        payload["subawards"] = subawards
    if spending_level is not None:
        payload["spending_level"] = spending_level

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=output_schema
    )
    return await post_client.send()
