# Multi-mode container: single CMD per service (compose) or supervisord (one-pod)
FROM python:3.12-slim

WORKDIR /app

# Install uv with pip (python:3.12-slim includes pip)
RUN pip install --no-cache-dir uv

# Copy project, sync deps and generate gRPC
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY scripts ./scripts
RUN uv sync --frozen 
RUN uv run cli proto

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Default: HTTP API via uv script (overridden by compose for rpc/rabbit/kafka)
CMD ["uv", "run", "http"]
