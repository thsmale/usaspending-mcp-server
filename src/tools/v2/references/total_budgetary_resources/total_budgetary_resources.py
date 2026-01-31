from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

from .total_budgetary_resources_schemas import (
    input_schema,
    output_schema,
)

tool_total_budgetary_resources = Tool(
    name="total_budgetary_resources",
    description=(
        "This is used to provide information on the federal budgetary resources of the government"
    ),
    inputSchema=input_schema,
    title="Total Government Budgetary Resources",
)

endpoint = "/api/v2/references/total_budgetary_resources/?"


async def call_tool_total_budgetary_resources(arguments: dict[str, Any]):
    fiscal_year = arguments.get("fiscal_year")
    fiscal_period = arguments.get("fiscal_period")

    if fiscal_year is not None and fiscal_year < 2017:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="The fiscal_year must be 2017 or later.",
                data=(
                    "If fiscal_period and fiscal_year are both omitted then "
                    "the entire history available will be returned."
                ),
            )
        )

    if fiscal_period is not None and fiscal_year is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="If fiscal_period is provided then fiscal_year must be provided as well.",
                data=(
                    "If fiscal_period and fiscal_year are both omitted then "
                    "the entire history available will be returned."
                ),
            )
        )

    params = {}
    if fiscal_year is not None:
        params["fiscal_year"] = fiscal_year
    if fiscal_period is not None:
        params["fiscal_period"] = fiscal_period

    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=output_schema
    )
    return await get_client.send()
