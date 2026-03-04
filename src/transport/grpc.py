"""gRPC servicers / server logic."""

import asyncio
import random
from concurrent import futures
from datetime import datetime, timezone

import grpc

from src.core import settings
from src.core.logging import logger
from src.schemas.commands import ActionCreate
from src.schemas.proto.transforms.action import action_to_proto, proto_reseed_to_action
from src.transport.producers import publish_kafka_event, publish_rabbit_task
from src.usecases.action import create_action_use_case, reseed_action_use_case
from src.schemas.commands import ReseedCommand
from src.schemas.entities import ActionContext
from src.usecases.echo import echo_use_case

try:
    from src.schemas.proto import action_pb2_grpc, echo_pb2, echo_pb2_grpc
except ImportError as e:
    raise ImportError(
        "gRPC code not generated. Run: uv run cli proto (or build Docker image)"
    ) from e


class EchoServicer(echo_pb2_grpc.EchoServiceServicer):
    def Echo(self, request, context):
        logger.info("gRPC Echo request: {}", request.message)
        reply_msg = echo_use_case.process(request.message)

        # Fan-out to messaging backends (fire-and-forget style)
        try:
            asyncio.run(publish_rabbit_task(f"grpc-echo: {request.message}"))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to publish RabbitMQ message from gRPC: {}", exc)

        try:
            asyncio.run(
                publish_kafka_event(
                    f'{{"source":"grpc","kind":"echo","message":"{request.message}"}}'
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to publish Kafka event from gRPC: {}", exc)

        return echo_pb2.EchoReply(message=reply_msg)


class ActionServicer(action_pb2_grpc.ActionServiceServicer):
    """gRPC ActionService backed by the existing usecases."""

    def Create(self, request, context):
        logger.info("gRPC Action.Create: name={}", request.name)

        # Map proto -> command model
        cmd = ActionCreate(
            name=request.name,
            description=request.description,
            tags=list(request.tags),
        )
        action = create_action_use_case.process(cmd)

        return action_to_proto(action)

    def Reseed(self, request, context):
        logger.info("gRPC Action.Reseed: id={}", request.id)

        # In a real app we'd load Action by id; here we rebuild from the request.
        action = proto_reseed_to_action(request)

        reseeded = reseed_action_use_case.process(
            ReseedCommand(
                action=action,
                context=ActionContext(
                    seed=random.randint(1, 1000000), updated_at=datetime.now(timezone.utc)
                ),
            )
        )
        return action_to_proto(reseeded)


def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    echo_pb2_grpc.add_EchoServiceServicer_to_server(EchoServicer(), server)
    action_pb2_grpc.add_ActionServiceServicer_to_server(ActionServicer(), server)
    listen_addr = f"{settings.grpc_host}:{settings.grpc_port}"
    server.add_insecure_port(listen_addr)
    server.start()
    logger.info("gRPC server listening on {}", listen_addr)
    server.wait_for_termination()
