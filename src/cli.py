"""CLI entrypoint (Fire) — proto, JWT, and producer helpers."""

from datetime import datetime, timezone
import random
import string
import subprocess
import sys
import uuid
from pathlib import Path

import fire
import requests

from src.core.logging import logger
from src.schemas.commands import ActionCreate
from src.transport.producers import publish_kafka_event, publish_rabbit_task
from src.usecases.action import create_action


def proto():
    """Generate gRPC Python code from proto files."""
    script = Path(__file__).resolve().parent.parent / "scripts" / "generate_grpc.py"
    subprocess.run([sys.executable, str(script)], check=True)


def generate_jwt(
    subject: str = "user",
    secret: str = "change-me",
    expires_hours: int = 24,
):
    """Generate a JWT (for dev/testing)."""
    try:
        import jwt
        from datetime import datetime, timedelta, timezone
    except ImportError:
        logger.error("Install PyJWT: uv add pyjwt")
        sys.exit(1)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(hours=expires_hours),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    logger.info(token)


def send_task(base_url: str = "http://localhost:8000"):
    """POST random payload to localhost /tasks (RabbitMQ producer)."""
    url = f"{base_url.rstrip('/')}/tasks"
    payload = _generate_random_payload()
    session = _create_request_session()
    req = session.post(url, json=payload, timeout=5)
    logger.info(f"202 {url} -> {req.json()}")


def send_event(base_url: str = "http://localhost:8000"):
    """POST random payload to localhost /events (Kafka producer)."""
    url = f"{base_url.rstrip('/')}/events"
    payload = _generate_random_payload()
    session = _create_request_session()
    req = session.post(url, json=payload, timeout=5)
    logger.info(f"202 {url} -> {req.json()}")


def rabbit_producer(message: str = "hello from producer"):
    """Publish a single message directly to RabbitMQ `tasks` queue."""
    # TODO: try to communicate with rabbitmq directly
    import asyncio

    asyncio.run(publish_rabbit_task(message))


def kafka_producer(message: str = "hello from producer"):
    """Publish a single message directly to Kafka `events` topic."""
    # TODO: try to communicate with kafka directly
    import asyncio

    asyncio.run(publish_kafka_event(message))


def main():
    fire.Fire(
        {
            "proto": proto,
            "generate-jwt": generate_jwt,
            "send-task": send_task,
            "send-event": send_event,
            "rabbit-producer": rabbit_producer,
            "kafka-producer": kafka_producer,
        }
    )


def _generate_random_payload() -> dict:
    """Small random payload for send_task / send_event."""
    action_cmd = ActionCreate(
        name="".join(random.choices(string.ascii_lowercase, k=8)),
        description="".join(random.choices(string.ascii_lowercase, k=16)),
        tags=[
            "".join(random.choices(string.ascii_lowercase, k=8))
            for _ in range(random.randint(1, 5))
        ],
    )
    action = create_action(action_cmd)
    # Ensure all fields are JSON-serializable (e.g. datetimes -> ISO strings)
    return action.model_dump(mode="json")


def _create_request_session(generate_trace_id: bool = False) -> requests.Session:
    """Get a requests session with a timeout."""
    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )
    if generate_trace_id:
        session.headers["X-Request-Id"] = str(uuid.uuid4())
        session.headers["X-Request-Timestamp"] = datetime.now(timezone.utc).isoformat()
    return session
