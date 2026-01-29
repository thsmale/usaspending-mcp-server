from mcp.types import Resource
from pydantic import FileUrl

from tools.v2.references.toptier_agencies import (
    toptier_agencies,
    use_cached_file,
)

error_details = """
This means the MCP server is fetching/returning all toptier_agencies
from the USA Spending API every time the toptier_agencies tool is called.
It was unable to read a local copy of the toptier_agencies and unable to
fetch a fresh version when it was started. Try the toptier_agencies tool
to view all toptier_agencies, it will return all of them.
"""


def get_toptier_agencies():
    if use_cached_file is False:
        return {"error": "No local toptier_agencies found", "details": error_details}

    return toptier_agencies


resource_name = "toptier_agencies"
resource_toptier_agencies = Resource(
    uri=FileUrl(f"file:///{resource_name}.json"),
    name=resource_name,
    title="All the toptier_agencies used by this MCP server.",
    description=(
        "This is a list of all the agencies and how they spend money."
        "If an error occurred in the MCP server and it is not using a "
        "local copy of toptier_agencies, a response indicating this "
        "will be returned."
    ),
    mime_type="application/json",
)
