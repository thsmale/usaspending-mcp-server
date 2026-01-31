from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

from .spending_over_time_schemas import (
    input_schema,
    output_schema,
)

tool_spending_over_time = Tool(
    name="spending_over_time",
    description=(
        "This returns a list of aggregated award amounts grouped by time period "
        "in ascending order (earliest to most recent)"
    ),
    inputSchema=input_schema,
    title="Spending Over Time",
)


async def call_tool_spending_over_time(arguments: dict[str, Any]):
    endpoint = "/api/v2/search/spending_over_time/"
    group = arguments.get("group")
    filters = arguments.get("filters")
    subawards = arguments.get("subawards")
    spending_level = arguments.get("spending_level")

    if not group:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="group must be provided.",
            )
        )

    if not bool(filters):
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="filters must be provided.",
            )
        )

    payload = {
        "group": group,
        "filters": filters,
    }

    if subawards is not None:
        payload["subawards"] = subawards
    if spending_level is not None:
        payload["spending_level"] = spending_level

    post_client = HttpClient(
        endpoint=endpoint,
        method="POST",
        payload=payload,
        output_schema=output_schema,
    )
    return await post_client.send()
