input_schema = {
    "type": "object",
    "required": [],
    "additionalProperties": False,
    "properties": {
        "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
        "sort": {"type": "string", "enum": ["name", "duns", "amount"], "default": "amount"},
        "limit": {"type": "number", "default": 50, "maximum": 1000},
        "page": {"type": "number", "default": 1},
        "keyword": {
            "type": "string",
            "description": ("They keyword results are filtered by. Searches on name, UEI, or DUNS"),
        },
        "award_type": {
            "type": "string",
            "enum": [
                "all",
                "contracts",
                "grants",
                "loans",
                "direct_payments",
                "other_financial_assistance",
            ],
            "default": "all",
        },
    },
}


output_schema = {
    "type": "object",
    "required": [],
    "additionalProperties": False,
    "properties": {
        "page_metadata": {
            "type": "object",
            "required": ["page", "limit", "total"],
            "additionalProperties": False,
            "properties": {
                "page": {"type": "number"},
                "limit": {"type": "number"},
                "total": {"type": "number"},
            },
        },
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "duns", "uei", "id", "recipient_level"],
                "additionalProperties": False,
                "properties": {
                    "name": {
                        "type": ["string", "null"],
                        "description": "Name of the recipient. null when the name is not provided",
                    },
                    "duns": {
                        "type": ["string", "null"],
                        "description": (
                            "Recipient's DUNS (Data Universal Numbering System) number. "
                            "null when no DUNS is provided"
                        ),
                    },
                    "uei": {
                        "type": ["string", "null"],
                        "description": (
                            "Recipient's UEI (Unique Entity Identifier). "
                            "null when no UEI is provided"
                        ),
                    },
                    "amount": {
                        "type": "number",
                        "description": (
                            "The aggregate monetary value of all "
                            "transactions associated with this recipient "
                            "for the trailing 12 months."
                        ),
                    },
                    "recipient_level": {
                        "type": "string",
                        "enum": ["R", "P", "C"],
                        "description": (
                            "A letter representing the recipient level. "
                            "R for neither parent nor child. "
                            "P for Parent recipient, or C for child recipient"
                        ),
                    },
                },
            },
        },
    },
}
