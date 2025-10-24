from typing import Any
from mcp.shared.exceptions import McpError 
from mcp.types import ErrorData, INVALID_PARAMS, Tool
from utils.http import GetClient

tool_federal_obligations = Tool(
    name='federal_obligations',
    description='This data can be used to better understand the different ways that a specific agency spends money. This returns the amount that the specific agency has obligated to various federal accounts in a given fiscal year.',
    inputSchema={
        'type': 'object',
        'required': ['fiscal_year', 'funding_agency_id'],
        'properties': {
            'fiscal_year': {
                'type': 'number',
                'description': 'The fiscal year that you are querying data for',
            },
            'funding_agency_id': {
                'type': 'number',
                'description': 'The unique USAspending.gov agency identifier. This ID is the agency_id value returned in the toptier_agencies tool',
            },
            'limit': {
                'type': 'number',
                'description': 'The maximum number of results to return in the response.'
            },
            'page': {
                'type': 'number',
                'description': 'The response page to return (the record offset is (page - 1) * limit)'
            }
        }
    }
)

response_schema = {
    'type': 'object',
    'required': ['results', 'page_metadata'],
    'properties': {
        'results': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['account_title', 'account_number', 'id', 'obligated_amount'],
                'properties': {
                    'account_title': { 'type': 'string' },
                    'account_number': { 'type': 'string' },
                    'id': {
                        'type': 'string',
                        'description': 'The USAspending.gov unique identifier for the federal account. You will need to use this ID when making API requests for details about specific federal accounts',
                    },
                    'obligated_amount': { 'type': 'string' }
                }
            }
        },
        'page_metadata': {
            'type': 'object',
            'required': ['count', 'page', 'has_next_page', 'has_previous_page', 'next', 'current', 'previous'], 
            'properties': {
                'count': { 'type': 'number' },
                'page': { 'type': 'number' },
                'has_next_page': { 'type': 'boolean' },
                'has_previous_page': { 'type': 'boolean' },
                'next': { 'type': ['string', 'null'] },
                'current': { 'type': 'string' },
                'previous': { 'type': ['string', 'null'] },
            }
        }
    }
}

def call_tool_federal_obligations(arguments: dict[str, Any]):
    endpoint = '/api/v2/federal_obligations/'
    fiscal_year = arguments.get('fiscal_year')
    funding_agency_id = arguments.get('funding_agency_id')
    limit = arguments.get('limit')
    page = arguments.get('page')

    if fiscal_year == None:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message='fiscal_year must be provided'
        ))
    
    if funding_agency_id == None:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message='funding_agency_id must be provided',
        ))
    
    params = {
        'fiscal_year': fiscal_year,
        'funding_agency_id': funding_agency_id,
    }

    if limit != None:
        params['limit'] = limit
    if page != None:
        params['page'] = page

    get_client = GetClient(endpoint, params, response_schema)
    return get_client.send()
    

