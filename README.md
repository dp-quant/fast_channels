# fast_channels experiments

Layered app: **core** (config, models, service), **schemas** (contracts + proto), **transport** (HTTP, gRPC, Kafka/Rabbit), **reconciliation** (auditor).

- **HTTP** – FastAPI (`/health`, `/echo`, `/actions`, `/tasks`, `/events`)
- **gRPC** – Echo service
- **RabbitMQ** – queue consumer (`tasks`) and producer (POST `/tasks` or `uv run app rabbit-producer`)
- **Kafka** – stream consumer (`events`) and producer (POST `/events` or `uv run app kafka-producer`)

**Stack:** loguru, fire, orjson, pydantic-settings, uv (or pip).

## Layout

```
src/
  core/           # Config, models, service layer
  schemas/        # internal, commands, queries, proto
  transport/      # http, grpc, consumers, producers
```

## Local setup

```bash
uv sync
uv run proto   # generate gRPC code (or use Docker)
```

## Run locally (uv scripts) - Still in TODO

```bash
uv run http    # HTTP :8000
uv run rpc     # gRPC :50051
uv run rabbit  # Rabbit consumer (needs RabbitMQ)
uv run kafka   # Kafka consumer (needs Kafka)
uv run all    # supervisord (all 4 in one process group)
```

**Tooling (Fire)**

CLI tooling (`uv run cli`):
```bash
uv run cli proto                          # generate gRPC stubs
uv run cli generate-jwt --subject=alice   # JWT for dev/testing
uv run cli send-task                      # POST random action to /tasks (needs HTTP up)
uv run cli send-event                     # POST random action to /events (needs HTTP up)
uv run cli send-task --base_url=http://localhost:8000
```

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

---

# TODO:
1) Add and spread traceid
2) Use Diska as a DI
3) Consumers scalability
4) Try celery like task routing for rabbit consumer
5) Try to use different topics/queues for different tasks, retries, backoff, jitters
6) Try sync/async flow for fast stream
7) Add cli tooling to send messages to kafka or rabbit
8) Fix run all, fix local runs
