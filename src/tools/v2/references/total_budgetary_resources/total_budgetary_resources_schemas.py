input_schema = {
    "type": "object",
    "required": [],
    "additionalProperties": False,
    "properties": {
        "fiscal_year": {
            "type": "number",
            "description": "The fiscal year to retrieve, 2017 or later",
        },
        "fiscal_period": {
            "type": "number",
            "description": (
                "The fiscal period. "
                "If this optional parameter is provided than fiscal_year is required. "
                "Valid values: 2-12 (2=November ... 12=September). "
                "For retrieving quarterly data, provide the period which equals "
                "quarter * 3 (e.g Q2=P6). "
                "If neither parameter is provided, than the entire available history "
                "will be returned."
            ),
        },
    },
}

output_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "messages": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "An array of warnings or instructional directives to aid consumers "
                "of this endpoint with development and debugging."
            ),
        },
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "fiscal_year",
                    "fiscal_period",
                    "total_budgetary_resources",
                ],
                "additionalProperties": False,
                "properties": {
                    "fiscal_year": {
                        "type": "number",
                    },
                    "fiscal_period": {
                        "type": "number",
                    },
                    "total_budgetary_resources": {"type": "number"},
                },
            },
        },
    },
}
