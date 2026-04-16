# Live demo walkthrough

Use this script as a presenter checklist for a 10 to 15 minute MCP walkthrough.

## 1. Explain the repo structure

Open these areas first:
- `mcp_demo/tools/`
- `mcp_demo/resources/`
- `mcp_demo/prompts/`
- `servers/http_mcp/server.py`
- `servers/http_mcp/client.py`

Talking point:
- the MCP server owns tools, resources, and prompts
- the host application connects through an MCP client
- transport is streamable HTTP because it matches production usage best

## 2. Start the server

```bash
python servers/http_mcp/server.py
```

Open:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/auth/demo-tokens`

Talking point:
- Swagger documents the normal REST support routes
- Inspector is the right tool to explore the MCP endpoint

## 3. Show auth and roles

Call these REST endpoints in Swagger or curl:
- `GET /auth/demo-tokens`
- `GET /demo/whoami` with the viewer token
- `GET /demo/admin-checklist` with the presenter token

Suggested curl examples:

```bash
curl -H "Authorization: Bearer course-viewer-token" http://127.0.0.1:8000/demo/whoami
curl -H "Authorization: Bearer course-demo-token" http://127.0.0.1:8000/demo/admin-checklist
```

Talking point:
- authentication answers “who are you?”
- authorization answers “what are you allowed to do?”
- the demo keeps auth simple with bearer tokens but still illustrates roles and scopes

## 4. Open MCP Inspector

Connect Inspector to:
- URL: `http://127.0.0.1:8000/mcp/`
- Header: `Authorization: Bearer course-demo-token`

Recommended sequence:
1. list tools
2. call `process_project_files`
3. list resources
4. read `course://outline`
5. list prompts
6. render `architecture_review_prompt`

Talking point:
- tools are executable actions
- resources are retrievable context
- prompts are reusable prompt templates

## 5. Run the host application example

```bash
python servers/http_mcp/client.py
```

Talking point:
- this script represents the host application in the MCP diagram
- it initializes a session, discovers capabilities, and invokes them programmatically

## 6. Wrap up with the architecture diagram

Map the code back to the conceptual flow:
- host app → `servers/http_mcp/client.py`
- MCP client → `ClientSession` + streamable HTTP transport
- MCP server → `mcp_demo/mcp_server.py`
- tools/resources/prompts → `mcp_demo/*/catalog.py`

## Quick recovery tips

If port 8000 is busy:

```bash
PORT=8001 python servers/http_mcp/server.py
```

If Inspector calls fail:
- confirm the URL ends with `/mcp/`
- confirm the `Authorization` header is present
- verify the token from `/auth/demo-tokens`

## Local tool call via streamable curl
```bash
SESSION_ID=$(curl -s -D - \
  -X POST http://127.0.0.1:8000/mcp/ \
  -H "Authorization: Bearer course-demo-token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl-demo","version":"0.1"}}}' \
  | grep -i "mcp-session-id" | awk '{print $2}' | tr -d '\r')

echo "Session: $SESSION_ID"

curl -s \
  -X POST http://127.0.0.1:8000/mcp/ \
  -H "Authorization: Bearer course-demo-token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

curl -s \
  -X POST http://127.0.0.1:8000/mcp/ \
  -H "Authorization: Bearer course-demo-token" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"estimate_delivery_effort","arguments":{"complexity":"high","integration_points":2,"risk_level":"medium"}}}'
```

{"jsonrpc":"2.0","id":2,"method":"tools/list"}

{"jsonrpc":"2.0","id":2,"method":"resources/read","params":{"uri":"course://outline"}}