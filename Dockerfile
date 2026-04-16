FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY mcp_demo ./mcp_demo
COPY servers ./servers
COPY main.py ./
COPY .env.example ./.env.example

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "servers/http_mcp/server.py"]
