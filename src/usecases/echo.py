"""Shared business logic (service layer) — Echo use case."""

from src.core.logging import logger


class EchoUseCase:
    """Echo service (used by gRPC and HTTP)."""

    def process(self, message: str) -> str:
        logger.info("Echo message: {}", message)
        return message


echo_use_case = EchoUseCase()


def echo_message(message: str) -> str:
    """Backward-compatible: echo message."""
    return echo_use_case.process(message)
