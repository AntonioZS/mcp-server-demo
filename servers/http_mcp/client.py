from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp_demo.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("http_mcp_client")


async def main() -> None:
    settings = get_settings()
    endpoint = f"{settings.base_url}{settings.mcp_path.rstrip('/')}/"
    headers = {"Authorization": f"Bearer {settings.demo_presenter_token}"}

    async with streamablehttp_client(endpoint, headers=headers) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            init_result = await session.initialize()
            logger.info("Initialized against %s (%s)", init_result.serverInfo.name, init_result.protocolVersion)

            tools = await session.list_tools()
            logger.info("Tools: %s", [tool.name for tool in tools.tools])

            resources = await session.list_resources()
            logger.info("Resources: %s", [resource.uri for resource in resources.resources])

            prompts = await session.list_prompts()
            logger.info("Prompts: %s", [prompt.name for prompt in prompts.prompts])

            tool_result = await session.call_tool(
                "estimate_delivery_effort",
                {"complexity": "high", "integration_points": 2, "risk_level": "medium"},
            )
            logger.info("Tool result: %s", tool_result)

            resource_result = await session.read_resource("course://outline")
            logger.info("Resource result: %s", json.dumps(resource_result.model_dump(mode="json"), indent=2))

            prompt_result = await session.get_prompt("architecture_review_prompt", {"system_name": "demo-platform"})
            logger.info("Prompt result: %s", json.dumps(prompt_result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
