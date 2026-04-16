from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# llm
import os
from dotenv import load_dotenv
import json
from openai import OpenAI
# Load environment variables from .env file
load_dotenv()

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv",  # Use uv to run the server
    args=["run", "python", "servers/calculator/main.py"],  # Path to your actual server
    env=None,  # Optional environment variables
)

def call_llm(prompt, functions):
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]  # Make sure to set this environment variable
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
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"]
            }
        }
    }

    return tool_schema

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available resources
            resources = await session.list_resources()
            print("LISTING RESOURCES")
            for resource in resources:
                print("Resource: ", resource)

            # List available tools
            tools = await session.list_tools()
            print("LISTING TOOLS")

            functions = []

            for tool in tools.tools:
                print("Tool: ", tool.name)
                print("Tool", tool.inputSchema["properties"])
                functions.append(convert_to_llm_tool(tool))
            
            prompt = "Add 2 to 20"

            # ask LLM what tools to all, if any
            functions_to_call = call_llm(prompt, functions)

            # call suggested functions
            for f in functions_to_call:
                result = await session.call_tool(f["name"], arguments=f["args"])
                print("TOOLS result: ", result.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
