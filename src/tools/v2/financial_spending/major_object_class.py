from datetime import date
from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": ["fiscal_year", "funding_agency_id"],
    "additionalProperties": False,
    "properties": {
        "fiscal_year": {
            "type": "number",
            "description": "The fiscal year that you are querying data for",
            "default": date.today().year,
        },
        "funding_agency_id": {
            "type": "number",
            "description": (
                "The unique USAspending.gov agency identifier. "
                "This ID is the agency_id value returned in the toptier_agencies tool "
                "i.e 1137."
            ),
        },
    },
}

output_schema = {
    "type": "object",
    "required": ["results"],
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "major_object_class_code",
                    "major_object_class_name",
                    "obligated_amount",
                ],
                "additionalProperties": False,
                "properties": {
                    "major_object_class_code": {"type": "string"},
                    "major_object_class_name": {"type": "string"},
                    "obligated_amount": {"type": "string"},
                },
            },
        }
    },
}

tool_major_object_class = Tool(
    name="major_object_class",
    description=(
        "This data can be used to better understand the different ways "
        "that a specific agency spends money"
    ),
    inputSchema=input_schema,
    title="Major Object Classes",
)


async def call_tool_major_object_class(arguments: dict[str, Any]):
    fiscal_year = arguments.get("fiscal_year")
    funding_agency_id = arguments.get("funding_agency_id")

    if fiscal_year is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="fiscal_year must be provided.",
                data="This is the fiscal year that you are querying data for.",
            )
        )
    if funding_agency_id is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="funding_agency_id must be provided.",
                data=(
                    "The unique USAspending.gov agency identifier. "
                    "This ID is the agency_id returned in the toptier_agencies tool."
                ),
            )
        )

    params = {
        "fiscal_year": fiscal_year,
        "funding_agency_id": funding_agency_id,
    }

    endpoint = "/api/v2/financial_spending/major_object_class/?"
    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=output_schema
    )
    return await get_client.send()
