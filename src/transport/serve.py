"""Fire runner for transport entrypoints: api, rpc, rabbit, kafka."""

import subprocess
import sys
from pathlib import Path

import fire


def http():
    """Run HTTP API (FastAPI)."""
    from src.transport.http import run
    run()


def rpc():
    """Run gRPC server."""
    from src.transport.grpc import run
    run()


def rabbit():
    """Run RabbitMQ consumer."""
    from src.transport.consumers import run_rabbit
    run_rabbit()


def kafka():
    """Run Kafka consumer."""
    from src.transport.consumers import run_kafka
    run_kafka()


def rabbit_producer(message: str = "hello from producer"):
    """Publish one message to RabbitMQ `tasks` queue (producer only)."""
    import asyncio
    from src.transport.producers import publish_rabbit_task
    asyncio.run(publish_rabbit_task(message))


def kafka_producer(message: str = "hello from producer"):
    """Publish one message to Kafka `events` topic (producer only)."""
    import asyncio
    from src.transport.producers import publish_kafka_event
    asyncio.run(publish_kafka_event(message))


def run_all():
    """Run http, rpc, rabbit, kafka under supervisord."""
    conf = Path(__file__).resolve().parent.parent.parent / "supervisord.conf"
    if not conf.exists():
        print("supervisord.conf not found", file=sys.stderr)
        sys.exit(1)
    subprocess.run(["supervisord", "-c", str(conf)], check=True)


def main():
    fire.Fire({
        "http": http,
        "rpc": rpc,
        "rabbit": rabbit,
        "kafka": kafka,
        "rabbit-producer": rabbit_producer,
        "kafka-producer": kafka_producer,
        "run-all": run_all,
    })


if __name__ == "__main__":
    main()
