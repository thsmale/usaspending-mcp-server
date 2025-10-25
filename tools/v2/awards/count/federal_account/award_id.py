from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import (
    INVALID_PARAMS,
    ErrorData,
    Tool,
)

from utils.http import GetClient

tool_awards_count_federal_accounts = Tool(
    name="awards_count_federal_accounts",
    description="Returns the number of federal accounts associated with the given award",
    inputSchema={
        "type": "object",
        "required": ["award_id"],
        "properties": {
            "award_id": {"type": "string", "description": "The name of the award"},
        },
    },
)

response_schema = {
    "type": "object",
    "properties": {
        "federal_accounts": {
            "type": "number",
        }
    },
}


def call_tool_awards_count_federal_accounts(arguments: dict[str, Any]):
    award_id = arguments.get("award_id")
    if not award_id:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="award_id is required"))

    endpoint = f"/api/v2/awards/count/federal_account/{award_id}/"
    get_client = GetClient(endpoint=endpoint, response_schema=response_schema)
    return get_client.send()
