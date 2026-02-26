from fiscalyear import FiscalYear

input_schema = {
    "type": "object",
    "required": ["fiscal_year", "funding_agency_id"],
    "additionalProperties": False,
    "properties": {
        "fiscal_year": {
            "type": "number",
            "description": "The fiscal year that you are querying data for",
            "default": FiscalYear.current().fiscal_year,
        },
        "funding_agency_id": {
            "type": "number",
            "description": (
                "The unique USAspending.gov agency identifier. "
                "This ID is the agency_id value returned in the toptier_agencies tool "
                "i.e 1137."
            ),
        },
    },
}

output_schema = {
    "type": "object",
    "required": ["results"],
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "major_object_class_code",
                    "major_object_class_name",
                    "obligated_amount",
                ],
                "additionalProperties": False,
                "properties": {
                    "major_object_class_code": {"type": "string"},
                    "major_object_class_name": {"type": "string"},
                    "obligated_amount": {"type": "string"},
                },
            },
        }
    },
}
