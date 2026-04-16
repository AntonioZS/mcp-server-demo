import asyncio
import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

# Load environment variables
load_dotenv()

def call_llm(prompt, functions):
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]
    )

    print("CALLING LLM")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user", 
                "content": prompt,
            },
        ],
        tools=functions,
        temperature=1.0,
        max_tokens=1000,
        top_p=1.0
    )

    response_message = response.choices[0].message
    
    functions_to_call = []

    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            print("TOOL: ", tool_call)
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            functions_to_call.append({ "name": name, "args": args })

    return functions_to_call

def convert_to_llm_tool(tool):
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"]
            }
        }
    }
    return tool_schema

async def run():
    # Connect to SSE server
    async with sse_client("http://localhost:8000") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available resources
            try:
                resources = await session.list_resources()
                print("LISTING RESOURCES")
                for resource in resources.resources:
                    print("Resource: ", resource)
            except Exception as e:
                print(f"Error listing resources: {e}")

            # List available tools
            tools = await session.list_tools()
            print("LISTING TOOLS")

            functions = []

            for tool in tools.tools:
                print("Tool: ", tool.name)
                print("Tool schema:", tool.inputSchema["properties"])
                functions.append(convert_to_llm_tool(tool))
            
            prompt = "Add 15 to 25"

            # Ask LLM what tools to call
            functions_to_call = call_llm(prompt, functions)

            # Call suggested functions
            for f in functions_to_call:
                result = await session.call_tool(f["name"], arguments=f["args"])
                print("TOOL result: ", result.content)

if __name__ == "__main__":
    asyncio.run(run())
