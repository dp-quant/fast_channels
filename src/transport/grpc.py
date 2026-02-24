"""gRPC servicers / server logic."""

import grpc
from concurrent import futures

from src.core import settings
from src.core.logging import logger
from src.usecases.echo import echo_message

try:
    from src.schemas.proto import echo_pb2, echo_pb2_grpc
except ImportError as e:
    raise ImportError(
        "gRPC code not generated. Run: python scripts/generate_grpc.py (or build Docker image)"
    ) from e


class EchoServicer(echo_pb2_grpc.EchoServiceServicer):
    def Echo(self, request, context):
        logger.info("gRPC Echo request: {}", request.message)
        return echo_pb2.EchoReply(message=echo_message(request.message))


def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoServicer(), server)
    listen_addr = f"{settings.grpc_host}:{settings.grpc_port}"
    server.add_insecure_port(listen_addr)
    server.start()
    logger.info("gRPC server listening on {}", listen_addr)
    server.wait_for_termination()
