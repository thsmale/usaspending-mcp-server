from copy import deepcopy
from typing import Any

from mcp.types import (
    Tool,
)

from utils.http import HttpClient

from .toptier_agencies_custom import (
    cached_file_is_current,
    create_mcp_response,
    custom_filters_input_schema,
    custom_pagination_output_schema,
    filter_by_keyword,
    get_fresh_toptier_agencies,
    get_pagination,
    read_cached_file,
    sort_results,
)

original_input_schema = {
    "type": "object",
    "required": [],
    "additionalProperties": False,
    "properties": {
        "sort": {
            "type": "string",
            "description": "A data field used to sort the response array",
            "enum": [
                "agency_id",
                "agency_name",
                "active_fy",
                "active_fq",
                "outlay_amount",
                "obligated_amount",
                "budget_authority_amount",
                "current_total_budget_authority_amount",
                "percentage_of_total_budget_authority",
            ],
            "default": "percentage_of_total_budget_authority",
        },
        "order": {
            "type": "string",
            "description": "The direction that the sort field will be sorted in",
            "enum": ["asc", "desc"],
            "default": "desc",
        },
    },
}

original_output_schema = {
    "type": "object",
    "required": ["results"],
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "abbreviation",
                    "active_fq",
                    "active_fy",
                    "agency_id",
                    "agency_name",
                    "budget_authority_amount",
                    "congressional_justification_url",
                    "current_total_budget_authority_amount",
                    "obligated_amount",
                    "outlay_amount",
                    "percentage_of_total_budget_authority",
                    "toptier_code",
                    "agency_slug",
                ],
                "additionalProperties": False,
                "properties": {
                    "abbreviation": {"type": "string"},
                    "active_fq": {"type": "string"},
                    "active_fy": {"type": "string"},
                    "agency_id": {
                        "type": "number",
                        "description": (
                            "The unique identifier for the agency. "
                            "This is used in other endpoints when requesting "
                            "detailed information about this specific agency"
                        ),
                    },
                    "agency_name": {"type": "string"},
                    "budget_authority_amount": {"type": "number"},
                    "congressional_justification_url": {"type": ["string", "null"]},
                    "current_total_budget_authority_amount": {"type": "number"},
                    "obligated_amount": {"type": "number"},
                    "outlay_amount": {"type": "number"},
                    "percentage_of_total_budget_authority": {
                        "type": "number",
                        "description": (
                            "This is the percentage of the agency's budget authority "
                            "compared to the total budget authority"
                        ),
                    },
                    "toptier_code": {"type": "string"},
                    "agency_slug": {
                        "type": "string",
                        "description": (
                            "The name of the agency in lowercase with dashed "
                            "to be used for profile link construction"
                        ),
                    },
                },
            },
        }
    },
}

# Get the contents of the cached toptier agencies
filename = "src/resources/toptier_agencies.json"
toptier_agencies, use_cached_file = read_cached_file(filename)
current = cached_file_is_current(toptier_agencies)
# Try to fetch fresh version of file if outdated or error occurs during read
if current is False or use_cached_file is False:
    toptier_agencies, use_cached_file = get_fresh_toptier_agencies(
        toptier_agencies, original_output_schema, use_cached_file
    )
toptier_agencies_len = len(toptier_agencies)


# Update input/output schema if using cached_file
# Since I added extra features like keyword search
input_schema = deepcopy(original_input_schema)
if use_cached_file:
    input_schema["properties"].update(custom_filters_input_schema)

output_schema = deepcopy(original_output_schema)
if use_cached_file:
    output_schema["properties"].update(custom_pagination_output_schema)


tool_toptier_agencies = Tool(
    name="toptier_agencies",
    description=(
        "This data can be used to better understand the different ways "
        "that a specific agency spends money"
    ),
    inputSchema=input_schema,
    title="Toptier Agency Profile",
)


async def call_tool_toptier_agencies(arguments: dict[str, Any]):
    # Arguments for USA Spending API schema
    sort = arguments.get("sort", "percentage_of_total_budget_authority")
    order = arguments.get("order", "desc")
    params = {}
    if sort is not None:
        params["sort"] = sort
    if order is not None:
        params["order"] = order

    endpoint = "/api/v2/references/toptier_agencies/?"
    get_client = HttpClient(
        endpoint=endpoint, method="GET", params=params, output_schema=output_schema
    )
    # If unable to read toptier_agencies cached file, use the API endpoint.
    if not use_cached_file:
        return await get_client.send()

    # Arguments for custom schema
    keyword = arguments.get("keyword")
    limit = arguments.get("limit", 5)
    page = arguments.get("page", 1)

    # Filter results by keyword search if provided
    results = filter_by_keyword(toptier_agencies, keyword)

    # Sort results by asc/desc
    sort_results(results, sort, order)

    # Get the snippet of results based off pagination
    paginated_results, page_metadata = get_pagination(results, limit, page)

    return create_mcp_response(paginated_results, page_metadata, get_client)
