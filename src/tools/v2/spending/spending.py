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

from .spending_schemas import (
    input_schema,
    output_schema,
)

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

endpoint = "/api/v2/spending/"


async def call_tool_spending(arguments: dict[str, Any]):
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
