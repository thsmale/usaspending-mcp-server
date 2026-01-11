from mcp.types import Tool

from utils.http import HttpClient

input_schema = {"type": "object", "properties": {}}

output_schema = {
    "type": "object",
    "required": ["results"],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["budget_function_code", "budget_function_title"],
                "additionalProperties": False,
                "properties": {
                    "budget_function_code": {"type": "string"},
                    "budget_function_title": {"type": "string"},
                },
            },
        }
    },
}

tool_list_budget_functions = Tool(
    name="list_budget_functions",
    description="This retrieves a list of all Budget Functions ordered by their title",
    inputSchema=input_schema,
)


async def call_tool_list_budget_functions():
    endpoint = "/api/v2/budget_functions/list_budget_functions/"
    get_client = HttpClient(endpoint=endpoint, method="GET", output_schema=output_schema)
    return await get_client.send()
