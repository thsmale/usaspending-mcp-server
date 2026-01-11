from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": [],
    "additionalProperties": False,
    "properties": {
        "fiscal_year": {
            "type": "number",
            "description": "The fiscal year to retrieve, 2017 or later",
        },
        "fiscal_period": {
            "type": "number",
            "description": (
                "The fiscal period. "
                "If this optional parameter is provided than fiscal_year is required. "
                "Valid values: 2-12 (2=November ... 12=September). "
                "For retrieving quarterly data, provide the period which equals "
                "quarter * 3 (e.g Q2=P6). "
                "If neither parameter is provided, than the entire available history "
                "will be returned."
            ),
        },
    },
}

output_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "messages": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "An array of warnings or instructional directives to aid consumers "
                "of this endpoint with development and debugging."
            ),
        },
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "fiscal_year",
                    "fiscal_period",
                    "total_budgetary_resources",
                ],
                "additionalProperties": False,
                "properties": {
                    "fiscal_year": {
                        "type": "number",
                    },
                    "fiscal_period": {
                        "type": "number",
                    },
                    "total_budgetary_resources": {"type": "number"},
                },
            },
        },
    },
}

tool_total_budgetary_resources = Tool(
    name="total_budgetary_resources",
    description=(
        "This is used to provide information on the federal budgetary resources of the government"
    ),
    inputSchema=input_schema,
)


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

    endpoint = "/api/v2/references/total_budgetary_resources/?"
    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=output_schema
    )
    return await get_client.send()
