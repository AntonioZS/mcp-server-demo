"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Comment out the dynamic resource temporarily
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "rude") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "You are my friend.",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
        "rude": "Hey bro, do you want a slap in the face?",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


# Run the server
if __name__ == "__main__":
    mcp.run()
