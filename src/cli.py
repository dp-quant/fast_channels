"""CLI entrypoint (Fire) — real CLI actions only: proto, generate-jwt, etc."""

import subprocess
import sys
from pathlib import Path

import fire


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
        print("Install PyJWT: uv add pyjwt", file=sys.stderr)
        sys.exit(1)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(hours=expires_hours),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    print(token)


def main():
    fire.Fire({
        "proto": proto,
        "generate-jwt": generate_jwt,
    })
