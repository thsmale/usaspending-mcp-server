from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

from .subawards_schemas import (
    input_schema,
    output_schema,
)

tool_subawards = Tool(
    name="subawards",
    description="This returns a filtered set of subawards",
    inputSchema=input_schema,
    title="Subawards",
)

endpoint = "/api/v2/subawards/"


async def call_tool_subawards(arguments: dict[str, Any]):
    page = arguments.get("page")
    limit = arguments.get("limit")
    sort = arguments.get("sort")
    order = arguments.get("order")
    award_id = arguments.get("award_id")

    if page is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="page must be provided.",
            )
        )

    if sort is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="sort must be provided.",
            )
        )

    if order is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="order must be provided.",
            )
        )

    payload = {
        "page": page,
        "sort": sort,
        "order": order,
    }

    if limit is not None:
        payload["limit"] = limit

    if award_id is not None:
        payload["award_id"] = award_id

    post_client = HttpClient(
        endpoint=endpoint,
        method="POST",
        payload=payload,
        output_schema=output_schema,
    )
    return await post_client.send()
