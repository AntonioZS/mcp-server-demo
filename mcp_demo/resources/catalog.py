from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

COURSE_OUTLINE = {
    "title": "MCP Server End-to-End Demo",
    "modules": [
        "Host application vs MCP client",
        "Transport over streamable HTTP",
        "Tools, resources, and prompts",
        "Security and bearer-token protection",
    ],
}

PROJECT_STATUS = {
    "demo": {"status": "green", "summary": "Ready for live walkthrough", "next_step": "Open Inspector and call a tool"},
    "payments": {"status": "yellow", "summary": "Waiting on dependency alignment", "next_step": "Review integration contracts"},
}


def register_resources(mcp: FastMCP) -> None:
    @mcp.resource("course://outline")
    def course_outline() -> str:
        return json.dumps(COURSE_OUTLINE, indent=2)

    @mcp.resource("project://{project_name}/status")
    def project_status(project_name: str) -> str:
        selected = PROJECT_STATUS.get(
            project_name,
            {
                "status": "unknown",
                "summary": f"No demo status found for {project_name}",
                "next_step": "Create a project-specific resource entry",
            },
        )
        return json.dumps({"project": project_name, **selected}, indent=2)
