FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# FastMCP stdio transport (voor Claude Code / Claude Desktop)
CMD ["python", "-m", "mcp_server"]
