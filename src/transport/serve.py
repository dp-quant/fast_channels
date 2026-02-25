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


def run_all():
    """Run http, rpc, rabbit, kafka under supervisord."""
    # TODO: need to find the way to properly handle .env files in project root
    # serve.py -> transport -> src -> project root
    root = Path(__file__).resolve().parent.parent.parent
    conf = root / "supervisord.conf"

    if not conf.exists():
        print("supervisord.conf not found", file=sys.stderr)
        sys.exit(1)
    subprocess.run(["supervisord", "-c", str(conf)], check=True)


def main():
    fire.Fire(
        {
            "http": http,
            "rpc": rpc,
            "rabbit": rabbit,
            "kafka": kafka,
            "all": run_all,
        }
    )


if __name__ == "__main__":
    main()
