from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(description="Prompt template for explaining MCP architecture during the course.")
    def explain_mcp_flow(audience: str = "backend engineers") -> str:
        return (
            "Explain the MCP flow for "
            f"{audience}: start with the host application, show how the MCP client negotiates capabilities, "
            "then demonstrate how the MCP server exposes tools, resources, and prompts over streamable HTTP."
        )

    @mcp.prompt(description="Prompt template for analyzing a production-readiness decision.")
    def architecture_review_prompt(system_name: str, focus: str = "security") -> str:
        return (
            f"Review the architecture of {system_name}. Focus on {focus}, transport choices, auth boundaries, "
            "and operational concerns that matter for a production MCP deployment."
        )
