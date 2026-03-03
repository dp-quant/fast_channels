"""FastAPI / REST implementation."""

import orjson
from fastapi import Body, FastAPI

from src.core import settings
from src.schemas.commands import ActionCreate
from src.schemas.entities import Action
from src.transport.producers import publish_kafka_event, publish_rabbit_task
from src.usecases.action import create_action
from src.usecases.echo import echo_use_case

app = FastAPI(title="fast_channels", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict:
    return {"service": "fast_channels", "transport": "http"}


@app.post("/echo")
async def echo(body: dict = Body(...)) -> dict:
    return body


@app.post("/echo/{message:path}")
async def echo_path(message: str) -> dict:
    return {"message": echo_use_case.process(message)}


@app.post("/actions", response_model=Action)
async def actions_create(cmd: ActionCreate):
    result = create_action(cmd)
    return result


@app.post("/tasks", status_code=202)
async def tasks_publish(action: Action):
    """Publish a message to the RabbitMQ `tasks` queue. Returns 202 Accepted."""
    payload = orjson.dumps(action.model_dump(mode="json")).decode()
    await publish_rabbit_task(payload)
    return {"status": "accepted", "queue": "tasks"}


@app.post("/events", status_code=202)
async def events_publish(action: Action):
    """Publish a message to the Kafka `events` topic. Returns 202 Accepted."""
    payload = orjson.dumps(action.model_dump(mode="json")).decode()
    await publish_kafka_event(payload)
    return {"status": "accepted", "topic": settings.kafka_topic}


def run():
    import uvicorn

    uvicorn.run(
        "src.transport.http:app",
        host=settings.http_host,
        port=settings.http_port,
        log_level="info",
    )
