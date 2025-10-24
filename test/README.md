# USA Spending MCP Client

This is a sample MCP client to test the USA Spending MCP server.

Run the example via:

```
uv run test/mcp-client.py
```

Ensure your `OPENAI_API_KEY` has been exported as an env variable.

## Details

The example uses the `MCPServerStreamableHttp` class from [openai-agents](https://github.com/openai/openai-agents-python). The server runs in a sub-process at `https://localhost:8000/mcp`.
When you are prompted "Ask anything:", begin typing in the CLI and type enter when you are ready to send the prompt.
Note this MCP client does not use sessions so the LLM will not be aware of any context from previous messages.
