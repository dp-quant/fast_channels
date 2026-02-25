"""Shared business logic (service layer)."""

from src.core.logging import logger


def echo_message(message: str) -> str:
    """Echo service (used by gRPC and HTTP)."""
    logger.info("Echo message: {}", message)
    return message
