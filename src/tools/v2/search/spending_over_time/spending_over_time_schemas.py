from copy import deepcopy

from tools.v2.search.config import advanced_filter_object

award_advanced_filter_object = deepcopy(advanced_filter_object)
award_advanced_filter_object["minProperties"] = 1

input_schema = {
    "type": "object",
    "required": ["group", "filters"],
    "additionalProperties": False,
    "properties": {
        "group": {
            "type": "string",
            "enum": ["calendar_year", "fiscal_year", "quarter", "month"],
            "default": "fiscal_year",
        },
        "filters": advanced_filter_object,
        "subawards": {
            "type": "boolean",
            "description": "True to group by sub-awards instead of prime awards.",
            "default": False,
        },
        "spending_level": {
            "type": "string",
            "enum": ["transactions", "awards", "subawards"],
            "description": (
                "Group the spending by level. "
                "This also determines what data source is used for the totals."
            ),
            "default": "transactions",
        },
    },
}

output_schema = {
    "type": "object",
    "required": ["group", "spending_level", "results", "messages"],
    "additionalProperties": False,
    "properties": {
        "group": {
            "type": "string",
            "enum": ["calendar_year", "fiscal_year", "quarter", "month"],
        },
        "spending_level": {
            "type": "string",
            "enum": ["transactions", "awards", "subawards"],
        },
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "time_period",
                    "aggregated_amount",
                    "Contract_Obligations",
                    "Loan_Obligations",
                    "Idv_Obligations",
                    "Grant_Obligations",
                    "Direct_Obligations",
                    "Other_Obligations",
                    "total_outlays",
                    "Contract_Outlays",
                    "Loan_Outlays",
                    "Idv_Outlays",
                    "Grant_Outlays",
                    "Direct_Outlays",
                    "Other_Outlays",
                ],
                "additionalProperties": False,
                "properties": {
                    "time_period": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "calendar_year": {"type": "string"},
                            "fiscal_year": {"type": "string"},
                            "quarter": {"type": "string"},
                            "month": {"type": "string"},
                        },
                    },
                    "aggregated_amount": {"type": "number"},
                    "Contract_Obligations": {"type": "number"},
                    "Loan_Obligations": {"type": "number"},
                    "Idv_Obligations": {"type": "number"},
                    "Grant_Obligations": {"type": "number"},
                    "Direct_Obligations": {"type": "number"},
                    "Other_Obligations": {"type": "number"},
                    "total_outlays": {"type": ["number", "null"]},
                    "Contract_Outlays": {"type": ["number", "null"]},
                    "Loan_Outlays": {"type": ["number", "null"]},
                    "Idv_Outlays": {"type": ["number", "null"]},
                    "Grant_Outlays": {"type": ["number", "null"]},
                    "Direct_Outlays": {"type": ["number", "null"]},
                    "Other_Outlays": {"type": ["number", "null"]},
                },
            },
        },
        "messages": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "An array of warnings or instructional directives to aid consumers "
                "of this endpoint with development and debugging."
            ),
        },
    },
}
