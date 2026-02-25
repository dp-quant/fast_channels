# Multi-mode container: single CMD per service (compose) or supervisord (one-pod)
FROM python:3.12-slim

WORKDIR /app

# Install uv with pip (python:3.12-slim includes pip)
RUN pip install --no-cache-dir uv

# Copy project, sync deps and generate gRPC
COPY pyproject.toml uv.lock README.md supervisord.conf ./
COPY src ./src
COPY scripts ./scripts
RUN uv sync --frozen 
RUN uv run cli proto

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Default: supervisord (http + rpc + rabbit + kafka). Override in compose for single-service containers.
# TODO: need to find the way to properly handle .env files in project root
CMD ["uv", "run", "all"]
