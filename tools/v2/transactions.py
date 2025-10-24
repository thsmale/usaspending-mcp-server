from typing import Any
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, Tool
from utils.http import PostClient

tool_transactions = Tool(
    name="transactions",
    description="This returns a list of transactions, their amount, type, action date, action type, modification number, and description",
    inputSchema={
        "type": "object",
        "required": ["award_id"],
        "properties": {
            "award_id": {
                "type": "string",
                "description": "Either a generated natural id or a database surrogate award id. Generated award identifiers are preferred as they are effectively permanent. Surrogate award ids are retained for backward compatibility but are deprecated",
            },
            "limit": {"type": "number", "min": 1, "max": 5000},
            "page": {"type": "number", "default": 1},
            "sort": {
                "type": "string",
                "enum": [
                    "modification_number",
                    "action_date",
                    "federal_action_obligation",
                    "face_value_loan_guarantee",
                    "original_loan_subsidy_cost",
                    "action_type_description",
                    "description",
                ],
                "default": "action_date",
            },
            "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
        },
    },
)

response_schema = {
    "type": "object",
    "required": [],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "action_date",
                    "action_type",
                    "action_type_description",
                    "description",
                    "face_value_loan_guarantee",
                    "federal_action_obligation",
                    "id",
                    "modification_number",
                    "original_loan_subsidy_cost",
                    "type",
                    "type_description",
                ],
                "properties": {
                    "action_date": {
                        "type": "string",
                        "description": "Action date in the format YYYY-MM-DD",
                    },
                    "action_type": {"type": "string"},
                    "action_type_description": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "face_value_loan_guarantee": {
                        "type": ["number", "null"],
                        "description": "Face value of the loan. Null for results with award type codes that do not correspond to loans",
                    },
                    "federal_action_obligation": {
                        "type": ["number", "null"],
                        "description": "Monetary value of the transaction. Null for results with award type codes that correspond to loans.",
                    },
                    "id": {"type": "string"},
                    "modification_number": {"type": "number"},
                    "original_loan_subsidy_cost": {
                        "type": ["number", "null"],
                        "description": "Original subsidy cost of the loan. Null for results with award type codes that do not correspond to loans.",
                    },
                    "type": {"type": "string"},
                    "type_description": {"type": ["string", "null"]},
                    "cfda_number": {"type": ["string", "null"]},
                },
            },
        },
        "page_metadata": {
            "type": "object",
            "required": ["page", "next", "previous", "hasNext", "hasPrevious"],
            "properties": {
                "page": {"type": "number"},
                "next": {"type": ["number", "null"]},
                "previous": {"type": ["number", "null"]},
                "hasNext": {"type": "boolean"},
                "hasPrevious": {"type": "boolean"},
            },
        },
    },
}


def call_tool_transactions(arguments: dict[str, Any]):
    endpoint = "/api/v2/transactions/"
    award_id = arguments.get("award_id")
    limit = arguments.get("limit")
    page = arguments.get("page")
    sort = arguments.get("sort")
    order = arguments.get("order")

    if award_id is None:
        raise McpError(
            ErrorData(code=INVALID_PARAMS, message="award_id is a required argument")
        )

    payload = {"award_id": award_id}

    if limit is not None:
        payload["limit"] = limit

    if page is not None:
        payload["page"] = page

    if sort is not None:
        payload["sort"] = sort

    if order is not None:
        payload["order"] = order

    post_client = PostClient(endpoint, payload, response_schema)
    return post_client.send()
