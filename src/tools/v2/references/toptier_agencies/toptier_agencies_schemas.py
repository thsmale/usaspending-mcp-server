original_input_schema = {
    "type": "object",
    "required": [],
    "additionalProperties": False,
    "properties": {
        "sort": {
            "type": "string",
            "description": "A data field used to sort the response array",
            "enum": [
                "agency_id",
                "agency_name",
                "active_fy",
                "active_fq",
                "outlay_amount",
                "obligated_amount",
                "budget_authority_amount",
                "current_total_budget_authority_amount",
                "percentage_of_total_budget_authority",
            ],
            "default": "percentage_of_total_budget_authority",
        },
        "order": {
            "type": "string",
            "description": "The direction that the sort field will be sorted in",
            "enum": ["asc", "desc"],
            "default": "desc",
        },
    },
}

original_output_schema = {
    "type": "object",
    "required": ["results"],
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "abbreviation",
                    "active_fq",
                    "active_fy",
                    "agency_id",
                    "agency_name",
                    "budget_authority_amount",
                    "congressional_justification_url",
                    "current_total_budget_authority_amount",
                    "obligated_amount",
                    "outlay_amount",
                    "percentage_of_total_budget_authority",
                    "toptier_code",
                    "agency_slug",
                ],
                "additionalProperties": False,
                "properties": {
                    "abbreviation": {"type": "string"},
                    "active_fq": {"type": "string"},
                    "active_fy": {"type": "string"},
                    "agency_id": {
                        "type": "number",
                        "description": (
                            "The unique identifier for the agency. "
                            "This is used in other endpoints when requesting "
                            "detailed information about this specific agency"
                        ),
                    },
                    "agency_name": {"type": "string"},
                    "budget_authority_amount": {"type": "number"},
                    "congressional_justification_url": {"type": ["string", "null"]},
                    "current_total_budget_authority_amount": {"type": "number"},
                    "obligated_amount": {"type": "number"},
                    "outlay_amount": {"type": "number"},
                    "percentage_of_total_budget_authority": {
                        "type": "number",
                        "description": (
                            "This is the percentage of the agency's budget authority "
                            "compared to the total budget authority"
                        ),
                    },
                    "toptier_code": {"type": "string"},
                    "agency_slug": {
                        "type": "string",
                        "description": (
                            "The name of the agency in lowercase with dashed "
                            "to be used for profile link construction"
                        ),
                    },
                },
            },
        }
    },
}

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
