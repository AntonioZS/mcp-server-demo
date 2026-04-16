# MCP Server Demo

End-to-end HTTP MCP demo for a course walkthrough. The repo now contains a production-style `streamable-http` server with:

- modular MCP primitives in `mcp_demo/`
- HTTP transport under `servers/http_mcp/`
- bearer-token protection for the MCP endpoint
- normal FastAPI routes for health checks and Swagger docs
- a sample MCP client that behaves like the host application in the MCP diagram

## Repo layout

```text
mcp_demo/
  auth.py
  config.py
  mcp_server.py
  tools/
  resources/
  prompts/
servers/
  http_mcp/
    client.py
    server.py
  sse/
  stdio_calculator/
  streamble_http/
```

The folders `sse/`, `stdio_calculator/`, and `streamble_http/` remain as earlier experiments. The main demo to use in class is `servers/http_mcp/`.

## What the demo exposes

### Tools
- `estimate_delivery_effort`
- `summarize_release_notes`
- `process_project_files`

### Resources
- `course://outline`
- `project://{project_name}/status`

### Prompts
- `explain_mcp_flow`
- `architecture_review_prompt`

## Local run

1. Create or activate your virtual environment.
2. Install dependencies:

```bash
pip install -e .
```

3. Optionally copy `.env.example` to `.env` and customize values.
4. Start the server:

```bash
python servers/http_mcp/server.py
```

Server URLs:
- App root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- MCP endpoint: `http://127.0.0.1:8000/mcp/`
- Demo token helpers: `http://127.0.0.1:8000/auth/demo-token` and `http://127.0.0.1:8000/auth/demo-tokens`

## MCP auth model

This demo uses simple bearer tokens so you can illustrate auth without bringing in a full OAuth provider.

Presenter token:

```text
course-demo-token
```

Viewer token:

```text
course-viewer-token
```

Use it as:

```text
Authorization: Bearer course-demo-token
```

Role model:
- `presenter`: `mcp:read`, `mcp:execute`, `demo:admin`
- `viewer`: `mcp:read`

Protected routes:
- `/mcp`
- `/demo/*`

Public routes:
- `/`
- `/health`
- `/docs`
- `/auth/demo-token`
- `/auth/demo-tokens`

## Run the host/client demo

With the server running:

```bash
python servers/http_mcp/client.py
```

The client will:
- initialize an MCP session
- list tools, resources, and prompts
- call one tool
- read one resource
- fetch one prompt

## MCP Inspector

You can connect MCP Inspector to the streamable HTTP endpoint:

- URL: `http://127.0.0.1:8000/mcp/`
- Header: `Authorization: Bearer course-demo-token`

Recommended live demo flow:
1. list tools
2. call `process_project_files`
3. list resources
4. read `course://outline`
5. list prompts
6. render `architecture_review_prompt`

## Swagger / REST demo

Swagger is useful here for the non-MCP routes:
- `GET /health`
- `GET /auth/demo-token`
- `GET /auth/demo-tokens`
- `GET /demo/overview`
- `GET /demo/whoami`
- `GET /demo/security-matrix`
- `GET /demo/admin-checklist`

That gives you a clean way to explain the difference between:
- normal REST endpoints
- the MCP endpoint that exposes tools/resources/prompts

## Docker

Build the image:

```bash
docker build -t mcp-server-demo .
```

Run the container:

```bash
docker run --rm -p 8000:8000 mcp-server-demo
```

## Suggested classroom storyline

1. Open the repo structure and explain `tools`, `resources`, and `prompts`.
2. Start the server and open Swagger.
3. Show the token helper endpoints and compare presenter vs viewer behavior.
4. Open MCP Inspector against `/mcp`.
5. Demonstrate a tool call, a resource read, and a prompt render.
6. Run the sample client and connect it back to the host-app → MCP-client → MCP-server diagram.

For a presenter-ready script, see [docs/demo-walkthrough.md](docs/demo-walkthrough.md).
