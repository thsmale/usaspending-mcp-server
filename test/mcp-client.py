import asyncio
import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions=(
            "You are a helpful assistant. "
            f"The date today is {datetime.today().strftime('%Y-%m-%d')}"
        ),
        mcp_servers=[mcp_server],
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
            "url": f"http://{HOST}:{PORT}/mcp",
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

        print(f"Starting USA Spending MCP Server at http://{HOST}:{PORT}/mcp")

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
