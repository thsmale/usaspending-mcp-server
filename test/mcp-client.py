import asyncio
import os
import shutil
import subprocess
import time
from typing import Any
from datetime import datetime, timedelta

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions=f"You are a helpful assistant. The date today is {datetime.today().strftime('%Y-%m-%d')}",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    while True:
        try:
            message = input("Ask anything: ")
            print(f"Running: {message}")
            result = await Runner.run(starting_agent=agent, input=message)
            print(result.final_output)
        except Exception as e:
            print(e)


async def main():
    async with MCPServerStreamableHttp(
        name="USA Spending MCP Server",
        params={
            "url": "http://localhost:8000/mcp",
            "timeout": timedelta(seconds=60),
        },
        client_session_timeout_seconds=60,
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Streamable HTTP Example", trace_id=trace_id):
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
            )
            await run(server)


if __name__ == "__main__":
    # Let's make sure the user has uv installed
    if not shutil.which("uv"):
        raise RuntimeError(
            "uv is not installed. Please install it: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # Run the USA Spending MCP Server in a subprocess
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "../server.py")

        print("Starting USA Spending MCP Server at http://localhost:8000/mcp")

        process = subprocess.Popen(["uv", "run", server_file])
        # Git it 3 seconds to start
        time.sleep(3)

        print("USA Spending MCP server started.")
    except Exception as e:
        print(f"Error starting USA Spending MCP server: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
