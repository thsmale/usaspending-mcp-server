# USA Spending MCP Server

This is a stateless streamable HTTP MCP server for interacting with [USASPENDING.gov](https://www.usaspending.gov/), the official source of government spending data.
You can track government spending over time, search government spending by agency, explore government spending to communities, and much more.
USASPENDING.gov provides this neat [dashboard](https://modelcontextprotocol.io/docs/tools/inspector) which shows some of the powers of the API should you want a high level overview of what you can achieve with this API.
The API docs can be viewed at this [URL](https://api.usaspending.gov/docs/).

## Running Locally
```sh
uv run server.py
```

## Running from PyPi
```sh
uvx --from usaspending-mcp-server@latest usaspending-mcp-server
```

## Running from Docker
```sh
docker build -t usaspending-mcp-server .
docker run -p 8000:8000 usaspending-mcp-server
```

## Using with Claude Desktop
Update your claude_desktop_config.json with the following configuration.
Ensure the MCP server is running by using one of the methods mentioned above.
```json
{
  "mcpServers": {
    "usaspending": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

## Configuration Options
The following env or .env variables are accepted to customize what host and port the MCP server runs on.
```
MCP_SERVER_HOST
MCP_SERVER_PORT
```

## Tools
| Name | Description | Example prompts |
| :--- | :--- | :--- |
| federal_accounts | This returns a list of federal accounts, their number, name, managing agency, and budgetary resources | - How many federal accounts are there? |
| list_budget_functions | This retrieves a list of all Budget Functions ordered by their title | - What are the budget functions? |
| major_object_class | This data can be used to better understand the different ways that a specific agency spends money | - What are the various ways the Department of Education spends money? |
| recipient | This can be used to visualize the government spending that pertains to a specific recipient. This returns a list of recipients, their level, DUNS, UEI, and amount. | - What are some companies that received funding from the NSA? |
| spending | This data can be used to drill down into specific subsets of data by level of detail. This data represents all government spending in the specified time period, grouped by the data type of your choice. | - What was some spending related to International Affairs? |
| spending_by_award | This allows for complex filtering for specific subsets of spending data. This accepts filters and fields, and returns the fields of the filtered awards. | - What was the largest award in 2025? <br> - What are some companies that received major federal contracts in Lindsey Graham's district? |
| spending_over_time | This returns a list of aggregated award amounts grouped by time period in ascending order (earliest to most recent). | - How has spending changed to California over the last 5 years? |
| subawards | This returns a filtered set of subawards | - Describe some of the subawards for CONT_AWD_FA870221C0001_9700_-NONE-_-NONE- and provide a rationale for them. |
| total_budgetary_resources | This is used to provide information on the federal budgetary resources of the government | - What was the government budget in 2025 vs 2024? <br> - How much money does the federal government provide in total to various government agencies? |
| toptier_agencies | This data can be used to better understand the different ways that a specific agency spends money | - Which federal agency receives the most money? |

### tools directory explained
This is a big API with a lot of routes so all tools are organized in the tools directory.
There is a md file for each tool so it is convenient to reference the documentation used to create the tool.
Currently, all contracts (aka API documentation) are referenced from commit [dv551d0](https://github.com/fedspendingtransparency/usaspending-api/commit/db551d0ab224cfde5a22a99cada44b7746c689b1) of the usaspending-api.
At the moment, each tool is manually created using the contract documentation as a reference.
The current plan is to make all API routes available to this MCP server.
In the future, the process of copying a contract over and using it to create a new tool will be automated.

## Testing
[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) is a good way to test the input and output schema without connecting to a LLM.
There is also a sample [MCP Client](test/README.md) to test the application using OpenAI.

## Contributing
Please see the [testing](#testing) section as a starting point to test your changes before submitting a PR.
If you are adding a new tool, please also add a copy of the respective contract used as a reference to create the `inputSchema` and `outputSchema`.
Please add the tool to the same path that it exists in the usaspending_api [contacts](https://github.com/fedspendingtransparency/usaspending-api/tree/master/usaspending_api/api_contracts/contracts) directory. 
For file naming convention refer to the contract file name and name the tool this as well.
For example, if you are creating a tool for the [v2/disaster/spending_by_geography.md](https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/disaster/spending_by_geography.md) API route this tool should be added with under the path tools/v2/disaster/spending_by_geography.py and the tool should be named disaster_spending_by_geography.
Should there be any objections to this please explain why in the PR as it is not bullet proof!

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/thsmale/usaspending-mcp-server/blob/main/LICENSE) file for details.