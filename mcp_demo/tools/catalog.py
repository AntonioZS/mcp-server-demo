from __future__ import annotations

import asyncio
from textwrap import shorten

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(description="Estimate delivery effort for a feature in story points.")
    def estimate_delivery_effort(complexity: str, integration_points: int = 0, risk_level: str = "medium") -> dict[str, str | int]:
        weights = {"low": 1, "medium": 3, "high": 5}
        risk_weights = {"low": 0, "medium": 1, "high": 2}
        story_points = weights.get(complexity.lower(), 3) + integration_points + risk_weights.get(risk_level.lower(), 1)
        return {
            "complexity": complexity,
            "integration_points": integration_points,
            "risk_level": risk_level,
            "story_points": story_points,
        }

    @mcp.tool(description="Summarize raw project notes into a short release update.")
    def summarize_release_notes(title: str, notes: str) -> str:
        condensed = shorten(" ".join(notes.split()), width=220, placeholder="...")
        return f"Release update for {title}: {condensed}"

    @mcp.tool(description="Simulate a long-running tool and emit progress notifications for teaching demos.")
    async def process_project_files(message: str, ctx: Context) -> TextContent:
        files = ["architecture.md", "backlog.csv", "release-plan.md"]
        for index, file_name in enumerate(files, start=1):
            await ctx.info(f"Processing {file_name} ({index}/{len(files)})")
            await asyncio.sleep(0.4)
        await ctx.info("Finished processing all demo files")
        return TextContent(
            type="text",
            text=f"Processed {len(files)} files successfully. Input message: {message}",
        )
