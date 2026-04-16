from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_demo.prompts import register_prompts
from mcp_demo.resources import register_resources
from mcp_demo.tools import register_tools

INSTRUCTIONS = """
This MCP server is designed for a course demo. It exposes a small but complete set of
capabilities over streamable HTTP so students can inspect and call tools, read resources,
and render reusable prompts end-to-end.
""".strip()


def create_mcp_server() -> FastMCP:
    mcp = FastMCP(
        name="HTTP MCP Course Demo",
        instructions=INSTRUCTIONS,
        streamable_http_path="/",
    )
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    return mcp
