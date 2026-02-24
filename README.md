# fast_channels experiments

Layered app: **core** (config, models, service), **schemas** (contracts + proto), **transport** (HTTP, gRPC, Kafka/Rabbit), **reconciliation** (auditor).

- **HTTP** – FastAPI (`/health`, `/echo`, `/orders`)
- **gRPC** – Echo service
- **RabbitMQ** – queue consumer (`tasks`)
- **Kafka** – stream consumer (`events`)

**Stack:** loguru, fire, orjson, pydantic-settings, uv (or pip).

## Layout

```
src/
  core/           # Config, models, service layer
  schemas/        # internal, commands, queries, proto
  transport/      # http, grpc, consumers
  reconciliation/# engine, partitions
```

## Local setup

```bash
uv sync
uv run proto   # generate gRPC code (or use Docker)
```

## Run locally (uv scripts)

```bash
uv run http    # HTTP :8000
uv run rpc     # gRPC :50051
uv run rabbit  # Rabbit consumer (needs RabbitMQ)
uv run kafka   # Kafka consumer (needs Kafka)
uv run run-all # supervisord (all 4 in one process group)
```

**CLI (Fire)** — real CLI actions only: `uv run app proto`, `uv run app generate-jwt --subject=alice`

## Docker

**Separate services (compose):**

```bash
docker compose up --build
```

- **HTTP:** http://localhost:8000  
- **gRPC:** localhost:50051  
- **RabbitMQ:** amqp://localhost:5672, management http://localhost:15672  
- **Kafka:** localhost:9092  

**One-pod (all in one container):** override CMD with `supervisord -c supervisord.conf`.
