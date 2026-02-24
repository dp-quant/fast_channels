"""FastAPI / REST implementation."""

from fastapi import Body, FastAPI

from src.core import settings
from src.schemas.commands import ActionCreate
from src.schemas.internal import ActionInternal 
from src.usecases.action import create_action
from src.usecases.echo import echo_message

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
    return {"message": echo_message(message)}


@app.post("/actions", response_model=ActionInternal)
async def actions_create(cmd: ActionCreate):
    result = create_action(cmd)
    return result


def run():
    import uvicorn
    uvicorn.run(
        "src.transport.http:app",
        host=settings.http_host,
        port=settings.http_port,
        log_level="info",
    )
