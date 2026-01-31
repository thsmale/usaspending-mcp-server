import json
from collections.abc import Iterable
from copy import deepcopy

from httpx import HTTPError, Response, get
from jsonschema import ValidationError, validate
from mcp.shared.exceptions import McpError
from mcp.types import (
    INTERNAL_ERROR,
    ErrorData,
    TextContent,
)

from utils.dates import (
    get_cur_fy_fq,
    is_outdated_fy_fq,
    latest_fy_fq_with_data,
)

"""
USA Spending API only returns all the top tier agencies, which is about 111.
I have added custom logic so the LLM can get more specific results.
This uses a cached file, so make sure every quarter or so it is updated.
"""

# Not from the official API schema, adding this so the LLM can get more specific results.
custom_filters_input_schema = {
    "keyword": {
        "type": "string",
        "description": (
            "Search by agency name or abbreviation i.e DOT or Department of Transportation"
        ),
    },
    "limit": {
        "type": "number",
        "description": "The number of results to include",
        "default": 5,
        "minimum": 1,
        "maximum": 10,
    },
    "page": {
        "type": "number",
        "description": "The page of results to return based on the limit",
        "minimum": 1,
        "default": 1,
    },
}

# Not from the official API schema, adding pagination so the LLM can get more specific results.
custom_pagination_output_schema = {
    "previous": {"type": ["number", "null"]},
    "count": {
        "type": "number",
        "description": "The total number of results",
    },
    "limit": {"type": "number"},
    "hasNext": {"type": "boolean"},
    "page": {"type": "number"},
    "hasPrevious": {"type": "boolean"},
    "next": {"type": ["number", "null"]},
}


# Take the toptier_agencies and return in an MCP format
def create_mcp_response(paginated_results, page_metadata, get_client):
    try:
        response = {
            "results": paginated_results,
            **page_metadata,
        }

        # Do a check to make sure the response schema is valid
        mock_response = Response(status_code=200, json=response)
        get_client.validate_response(mock_response)

        # Turn into a JSON string and minify
        response = json.dumps(response, separators=(",", ":"))
        return [TextContent(type="text", text=response)]
    except Exception as e:
        print("Failed to create_mcp_response in toptier_agencies")
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=("Internal MCP server error."),
            )
        ) from e


# Credit to the USA Spending API
# https://github.com/fedspendingtransparency/usaspending-api/blob/04cfc1cffdf0ef8d8684cc28a9cac9f9bc7d3b34/usaspending_api/common/helpers/generic_helper.py#L163
def get_pagination(results, limit, page):
    page_metadata = {
        "page": page,
        "count": len(results),
        "next": None,
        "previous": None,
        "hasNext": False,
        "hasPrevious": False,
    }
    if limit < 1 or page < 1:
        return [], page_metadata

    page_metadata["hasNext"] = limit * page < len(results)
    page_metadata["hasPrevious"] = page > 1 and limit * (page - 2) < len(results)

    if not page_metadata["hasNext"]:
        paginated_results = results[limit * (page - 1) :]
    else:
        paginated_results = results[limit * (page - 1) : limit * page]

    page_metadata["next"] = page + 1 if page_metadata["hasNext"] else None
    page_metadata["previous"] = page - 1 if page_metadata["hasPrevious"] else None
    return paginated_results, page_metadata


# This search algorithm could be improved.
def filter_by_keyword(toptier_agencies, keyword):
    if keyword is None or keyword == "":
        return deepcopy(toptier_agencies)
    keyword = keyword.lower()

    # Just in case some rotten data is passed in
    if not isinstance(toptier_agencies, Iterable):
        print("Received non iterable data in filter_by_keyword")
        return []

    results = [
        agency
        for agency in toptier_agencies
        if keyword in agency.get("abbreviation", "").lower()
        or keyword in agency.get("agency_name", "").lower()
    ]
    return results


def sort_results(results, sort="percentage_of_total_budget_authority", order="desc"):
    reverseOrder = True
    if order == "asc":
        reverseOrder = False

    try:
        results.sort(key=lambda x: x[sort], reverse=reverseOrder)
    except Exception as e:
        # Possibly add extra message here to let the LLM know
        print(f"Failed to sort the results {e=}")
        return results


def read_cached_file(filename: str):
    toptier_agencies = []
    use_cached_file = False
    try:
        f = open(filename)
        toptier_agencies = json.loads(f.read())
        f.close()
        if not f.closed:
            print("File descriptor was not closed for toptier_agencies.json")
    except OSError as e:
        print(f"Error occurred while reading filename {filename} {e=}")
    except Exception as e:
        print(f"Unexpected error occurred while reading filename {filename} {e=}")

    if len(toptier_agencies) > 0:
        use_cached_file = True

    return toptier_agencies, use_cached_file


# Check to make sure the cached file is not out of date
# All key, vals of the cached value have already been validated in the unit tests
# Expect about a 45 day delay after a fq to end for data to be updated.
# https://github.com/fedspendingtransparency/usaspending-api/blob/master/loading_data.md
def cached_file_is_current(toptier_agencies):
    outdated_agencies = 0
    cur_fy, cur_fq = get_cur_fy_fq()
    max_fy_with_data, max_fq_with_data = latest_fy_fq_with_data(lag=45)
    for agency in toptier_agencies:
        fy = agency.get("active_fy")
        fq = agency.get("active_fq")
        outdated = is_outdated_fy_fq(max_fy_with_data, max_fq_with_data, fy, fq)
        if outdated is False:
            outdated_agencies += 1

    if outdated_agencies > 0:
        print(f"{outdated_agencies} out of {len(toptier_agencies)} agencies are out of date.")
        return False

    return True


# This will fetch a new version of toptier_agencies from the API endpoint
# It can be used if on startup it is detected the cached file is outdated
# It can also be a backup in case the cached file was not able to be read
def get_fresh_toptier_agencies(toptier_agencies, output_schema, use_cached_file):
    url = "https://api.usaspending.gov/api/v2/references/toptier_agencies/"
    fresh_toptier_agencies = []
    try:
        response = get(url, timeout=60)
        fresh_toptier_agencies = response.json()
    except HTTPError as e:
        print(f"Error occurred while fetching fresh toptier_agencies {e=}")
    except Exception as e:
        print(f"Unexpected occurred while fetching fresh toptier_agencies {e=} and {type(e)=}")

    try:
        validate(fresh_toptier_agencies, schema=output_schema)
    except ValidationError as e:
        print(
            "Failed to validate fresh_toptier_agencies so defaulting to cached file. "
            f"{e.message} in path {e.relative_schema_path}"
        )
        return toptier_agencies, use_cached_file
    except Exception as e:
        print(
            "Unexpected error occurred while validating fresh_toptier_agencies "
            "so defaulting to cached file. "
            f"{e=} and {type(e)=}"
        )
        return toptier_agencies, use_cached_file

    if toptier_agencies == fresh_toptier_agencies["results"]:
        print(
            "Detected no differences between cached and fresh toptier_agencies.",
            "Defaulting to cached toptier_agencies.",
        )
        return toptier_agencies, use_cached_file

    print("Successfully fetched fresh toptier_agencies, this data will be used.")
    return fresh_toptier_agencies, True
