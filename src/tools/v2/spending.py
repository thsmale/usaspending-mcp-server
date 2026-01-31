from datetime import date
from sys import maxsize as MAX_INT
from typing import Any

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData, Tool

from utils.dates import (
    is_outdated_fy_fq,
    latest_fy_fq_with_data,
    period_to_quarter,
)
from utils.http import HttpClient

input_schema = {
    "type": "object",
    # Filters is required, omitting bc LLM struggled setting FY & FQ/Period
    "required": ["type"],
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
            # FY and quarter or period is required
            # However, LLM really struggles with this
            # So set default values in tool handler
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

    # Data is not reported until 45 days after the quarter closes
    # Adjust cur fq/fy to reflect most recent fy/fq that has data
    fy, fq = latest_fy_fq_with_data(lag=45)
    fy = str(fy)
    fq = str(fq)
    # FY and FQ/Period was marked as required in the schema
    # However, the LLM messes this up frequently
    # So changed to not required to facilitate smoother tool calls
    if not bool(filters):
        filters = {"fy": fy, "quarter": fq}

    if filters.get("fy") is None:
        filters["fy"] = fy

    if filters.get("quarter") is None and filters.get("period") is None:
        filters["quarter"] = "1"

    # Very obtuse code to check if the date range contains any data.
    # Note this doesn't take into account if period and quarter provided.
    # If LLM provided a period != 1-12 this could break.
    try:
        fiscal_year = int(filters.get("fy", 0))
        quarter = int(filters.get("quarter", MAX_INT))
        period = int(filters.get("period", MAX_INT))
        if fiscal_year <= 2017 and (quarter < 2 or period < 6):
            raise McpError(
                ErrorData(code=INVALID_PARAMS, message="Data is not available prior to FY 2017 Q2.")
            )
        # If period was provided instead of quarter, check the period has data
        if quarter == MAX_INT:
            quarter = period_to_quarter(int(period))
        if (
            is_outdated_fy_fq(lower_fy=fy, lower_fq=fq, upper_fy=fiscal_year, upper_fq=quarter)
            is True
        ):
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Most recently available data is from FY {fy} Q{fq}.",
                )
            )
    except McpError as e:
        raise e
    except TypeError as e:
        # Continue in case it was just a cast error with python
        print(f"Failed to check if fy/fq is valid date range due to error {e=}")
        pass
    except Exception as e:
        # Something really funky happened, try the API request anyways
        print(
            "Unexpected failure checking if fy and quarter was valid range "
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
