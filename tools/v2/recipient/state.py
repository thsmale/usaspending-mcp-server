from mcp.types import Tool
from utils.util import send

tool_state = Tool(
    name="state",
    description=(
        "This data contains the government spending that occurs in a specific state or territory"
    ),
    inputSchema={"type": "object", "properties": {}},
)

response_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["name", "code", "fips", "amount", "type"],
        "properties": {
            "name": {"type": "string"},
            "code": {"type": "string"},
            "fips": {"type": "string"},
            "type": {"type": "string", "enum": ["state", "territory", "district"]},
        },
    },
}


def call_tool_state():
    endpoint = "/api/v2/recipient/state/"
    return send(endpoint=endpoint, response_schema=response_schema)
