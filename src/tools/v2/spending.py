from datetime import date
from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.http import HttpClient

input_schema = {
    "type": "object",
    "required": ["type", "filters"],
    "additionalProperties": False,
    "properties": {
        "type": {
            "type": "string",
            "enum": [
                "federal_account",
                "object_class",
                "recipient",
                "award",
                "budget_function",
                "budget_subfunction",
                "agency",
                "program_activity",
            ],
        },
        "filters": {
            "type": "object",
            "anyOf": [
                {"required": ["fy", "quarter"]},
                {"required": ["fy", "period"]},
            ],
            "additionalProperties": False,
            "properties": {
                "fy": {
                    "type": "string",
                    "default": date.today().strftime("%Y"),
                    # Adding length to ensure it is 2017, not 17
                    "minLength": 4,
                    "maxLength": 4,
                    "description": "YYYY",
                },
                "quarter": {"type": "string", "enum": ["1", "2", "3", "4"]},
                "period": {
                    "type": "string",
                    "enum": [
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "10",
                        "11",
                        "12",
                    ],
                },
                "agency": {"type": "number"},
                "federal_account": {"type": "number"},
                "object_class": {"type": "number"},
                "budget_function": {"type": "number"},
                "budget_subfunction": {"type": "number"},
                "recipient": {"type": "number"},
                "program_activity": {"type": "number"},
            },
        },
    },
}

output_schema = {
    "type": "object",
    "required": ["total", "end_date", "results"],
    "additionalProperties": False,
    "properties": {
        "total": {"type": ["number", "null"]},
        "end_date": {"type": "string"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["code", "id", "type", "name", "amount"],
                "additionalProperties": False,
                "properties": {
                    "code": {"type": "string"},
                    "id": {"type": "string"},
                    "generated_unique_number_id": {"type": "string"},
                    "type": {"type": "string"},
                    "name": {"type": "string"},
                    "amount": {"type": "number"},
                    "account_number": {"type": "string"},
                    "link": {"type": "string"},
                },
            },
        },
    },
}

tool_spending = Tool(
    name="spending",
    description=(
        "This data can be used to drill down into specific subsets of data by level of detail. "
        "This data represents all government spending in the specified time period, "
        "grouped by the data type of your choice. "
        # This was needed other wise the model kept forgetting to add a quarter or period.
        # Despite the json schema saying either one was required.
        "Provide either a quarter or a period."
    ),
    inputSchema=input_schema,
    title="Spending Explorer",
)


async def call_tool_spending(arguments: dict[str, Any]):
    endpoint = "/api/v2/spending/"
    spending_type = arguments.get("type")
    filters = arguments.get("filters")

    if spending_type is None:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="type must be provided.",
            )
        )

    if not bool(filters):
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="filters must be provided.",
            )
        )

    # Very obtuse code to check if the date range contains any data.
    try:
        if int(filters["fy"]) <= 2017 and int(filters["quarter"]) < 2:
            raise McpError(
                ErrorData(code=INVALID_PARAMS, message="Data is not available prior to FY 2017 Q2.")
            )
    except McpError as e:
        raise e
    except KeyError:
        # If the agent provided a period, give the API request a shot
        # API request could still fail for example, if period is 1, and fy is 2020
        pass
    except ValueError as e:
        # Continue in case it was just a cast error with python
        print(
            f"Failed to check if fy and quarter was before 2017 Q2 due to error {e=} with {type(e)}"
        )
        pass
    except Exception as e:
        # Something really funky happened, try the API request anyways
        print(
            "Unexpected failure checking if fy and quarter was before 2017 Q2 "
            f"due to error {e=} with {type(e)}"
        )
        pass

    payload = {
        "type": spending_type,
        "filters": filters,
    }

    post_client = HttpClient(
        endpoint=endpoint, method="POST", payload=payload, output_schema=output_schema
    )
    return await post_client.send()
