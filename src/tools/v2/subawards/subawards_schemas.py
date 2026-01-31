input_schema = {
    "type": "object",
    "required": ["page", "sort", "order"],
    "additionalProperties": False,
    "properties": {
        "page": {"type": "number", "default": 1},
        "limit": {"type": "number", "default": 10},
        "sort": {
            "type": "string",
            "enum": [
                "subaward_number",
                "id",
                "description",
                "action_date",
                "amount",
                "recipient_name",
            ],
            "default": "amount",
        },
        "order": {"type": "string", "enum": ["asc", "desc"], "default": "desc"},
        "award_id": {
            "type": "string",
            "description": (
                "Either a generated natural award id or a database surrogate award id. "
                "Generated award identifiers are preferred as they are effectively permanent. "
                "Surrogate award ids retained for backward compatibility but are deprecated."
            ),
        },
    },
}

output_schema = {
    "type": "object",
    "required": ["results", "page_metadata"],
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "id",
                    "subaward_number",
                    "description",
                    "action_date",
                    "amount",
                    "recipient_name",
                ],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "number"},
                    "subaward_number": {"type": "string"},
                    "description": {"type": "string"},
                    "action_date": {"type": "string"},
                    "amount": {"type": "number"},
                    "recipient_name": {"type": "string"},
                },
            },
        },
        "page_metadata": {
            "type": "object",
            "required": ["page", "next", "previous", "hasNext", "hasPrevious"],
            "additionalProperties": False,
            "properties": {
                "page": {"type": "number"},
                "next": {"type": ["number", "null"]},
                "previous": {"type": ["number", "null"]},
                "hasNext": {"type": "boolean"},
                "hasPrevious": {"type": "boolean"},
            },
        },
    },
}
