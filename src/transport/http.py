"""Starlette / REST implementation."""

import orjson
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from src.core import settings
from src.schemas.commands import ActionCreate
from src.schemas.entities import Action
from src.transport.producers import publish_kafka_event, publish_rabbit_task
from src.usecases.action import create_action
from src.usecases.echo import echo_use_case


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def root(request: Request) -> JSONResponse:
    return JSONResponse({"service": "fast_channels", "transport": "http"})


async def echo(request: Request) -> JSONResponse:
    body = await request.json()
    return JSONResponse(body)


async def echo_path(request: Request) -> JSONResponse:
    message = request.path_params["message"]
    return JSONResponse({"message": echo_use_case.process(message)})


async def actions_create(request: Request) -> JSONResponse:
    body = await request.json()
    cmd = ActionCreate.model_validate(body)
    result = create_action(cmd)
    return JSONResponse(result.model_dump(mode="json"))


async def tasks_publish(request: Request) -> JSONResponse:
    """Publish a message to the RabbitMQ `tasks` queue. Returns 202 Accepted."""
    body = await request.json()
    action = Action.model_validate(body)
    payload = orjson.dumps(action.model_dump(mode="json")).decode()
    await publish_rabbit_task(payload)
    return JSONResponse({"status": "accepted", "queue": "tasks"}, status_code=202)


async def events_publish(request: Request) -> JSONResponse:
    """Publish a message to the Kafka `events` topic. Returns 202 Accepted."""
    body = await request.json()
    action = Action.model_validate(body)
    payload = orjson.dumps(action.model_dump(mode="json")).decode()
    await publish_kafka_event(payload)
    return JSONResponse(
        {"status": "accepted", "topic": settings.kafka_topic}, status_code=202
    )


routes = [
    Route("/health", endpoint=health, methods=["GET"]),
    Route("/", endpoint=root, methods=["GET"]),
    Route("/echo", endpoint=echo, methods=["POST"]),
    Route("/echo/{message:path}", endpoint=echo_path, methods=["POST"]),
    Route("/actions", endpoint=actions_create, methods=["POST"]),
    Route("/tasks", endpoint=tasks_publish, methods=["POST"]),
    Route("/events", endpoint=events_publish, methods=["POST"]),
]

app = Starlette(debug=False, routes=routes)


def run():
    import uvicorn

    uvicorn.run(
        "src.transport.http:app",
        host=settings.http_host,
        port=settings.http_port,
        log_level="info",
    )
