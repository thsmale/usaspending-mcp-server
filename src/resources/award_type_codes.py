from mcp.types import Resource
from pydantic import FileUrl

award_type_groups = {
    "contracts": {
        "A": "BPA (Blanket Purchase Agreement) Call",
        "B": "Purchase Order",
        "C": "Delivery Order",
        "D": "Definitive Contract",
    },
    "loans": {"07": "Direct Loan", "08": "Guaranteed/Insured Loan"},
    "idvs": {
        "IDV_A": "GWAC Government Wide Acquisition Contract",
        "IDV_B": "IDC Multi-Agency Contract, Other Indefinite Delivery Contract",
        "IDV_B_A": "IDC Indefinite Delivery Contract / Requirements",
        "IDV_B_B": "IDC Indefinite Delivery Contract / Indefinite Quantity",
        "IDV_B_C": "IDC Indefinite Delivery Contract / Definite Quantity",
        "IDV_C": "FSS Federal Supply Schedule",
        "IDV_D": "BOA Basic Ordering Agreement",
        "IDV_E": "BPA Blanket Purchase Agreement",
    },
    "grants": {
        "02": "Block Grant",
        "03": "Formula Grant",
        "04": "Project Grant",
        "05": "Cooperative Agreement",
    },
    "other_financial_assistance": {
        "06": "Direct Payment for Specified Use",
        "10": "Direct Payment with Unrestricted Use",
    },
    "direct_payments": {
        "09": "Insurance",
        "11": "Other Financial Assistance",
        "-1": "Not Specified",
    },
}

resource_name = "award_type_codes"
resource_award_type_codes = Resource(
    uri=FileUrl(f"file:///{resource_name}.json"),
    name=resource_name,
    title="award_type_codes defined and sorted by their group.",
    description=(
        "award_type_codes must only contain types from one group. "
        "This returns JSON explaining which award_type_codes belong to which group."
        "It also includes the definition for all award_type_codes values. "
    ),
    mime_type="application/json",
)
