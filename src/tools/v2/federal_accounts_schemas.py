input_schema = {
    "type": "object",
    "required": [],
    "additionalProperties": False,
    "properties": {
        "filters": {
            "type": "object",
            "required": [],
            "additionalProperties": False,
            "properties": {
                "fy": {
                    "type": "string",
                    "description": (
                        "Providing fy does not change the rows that are returned, "
                        "instead, it limits the budgetary_resources value to the "
                        "fiscal year indicated. Federal accounts with no submissions "
                        "for that fiscal year will return null."
                    ),
                    "default": "previous fiscal year",
                },
                "agency_identifier": {"type": "string"},
            },
            "description": (
                "The filter takes a fiscal year, but if one is not provided, "
                "it defaults to the last certified fiscal year."
            ),
        },
        "sort": {
            "type": "object",
            "required": [],
            "additionalProperties": False,
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "The direction results are sorted by.",
                    "default": "desc",
                },
                "field": {
                    "type": "string",
                    "enum": [
                        "budgetary_resources",
                        "account_name",
                        "account_number",
                        "managing_agency",
                    ],
                    "default": "budgetary_resources",
                    "description": "The field that you want to sort on.",
                },
            },
        },
        "limit": {
            "type": "number",
            "description": "The number of results to include per page.",
            "default": 5,
        },
        "page": {
            "type": "number",
            "description": "The page of results to return based on the limit.",
            "default": 1,
        },
        "keyword": {
            "type": "string",
            "description": (
                "They keyword that you want to search on. "
                "Can be used to search by name, number, managing agency, "
                "and budgetary resources"
            ),
        },
    },
}

output_schema = {
    "type": "object",
    "required": [
        "count",
        "limit",
        "hasNext",
        "page",
        "hasPrevious",
        "next",
        "fy",
        "results",
    ],
    "additionalProperties": False,
    "properties": {
        "previous": {"type": ["number", "null"]},
        "count": {"type": "number"},
        "limit": {"type": "number"},
        "hasNext": {"type": "boolean"},
        "page": {"type": "number"},
        "hasPrevious": {"type": "boolean"},
        "next": {"type": ["number", "null"]},
        "fy": {"type": "string"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "account_name",
                    "account_number",
                    "account_id",
                    "managing_agency_acronym",
                    "agency_identifier",
                    "budgetary_resources",
                    "managing_agency",
                ],
                "additionalProperties": False,
                "properties": {
                    "account_name": {
                        "type": ["string", "null"],
                        "description": (
                            "Name of the federal account. null when the name is not provided"
                        ),
                    },
                    "account_number": {
                        "type": ["string", "null"],
                        "description": (
                            "The number for the federal account. "
                            "null when no account number is provided"
                        ),
                    },
                    "account_id": {
                        "type": "number",
                        "description": "A unique identifier for the federal account",
                    },
                    "managing_agency_acronym": {"type": "string"},
                    "managing_agency": {"type": "string"},
                },
            },
        },
    },
}
