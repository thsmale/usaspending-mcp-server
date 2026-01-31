from fiscalyear import FiscalYear

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
                    "default": FiscalYear.current().fiscal_year,
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
