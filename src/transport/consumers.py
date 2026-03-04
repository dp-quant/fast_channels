"""FastStream (Kafka / RabbitMQ) consumer logic."""

import grpc
import asyncio
import random
import orjson
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream.kafka import KafkaBroker
from src.core.logging import logger

from src.core import settings
from src.schemas.proto.transforms.action import action_to_reseed_proto, proto_to_action
from src.transport.producers import publish_rabbit_task
from src.usecases.action import reseed_action_use_case
from src.schemas.commands import ReseedCommand
from src.schemas.entities import Action, ActionContext
from src.schemas.proto import action_pb2_grpc

# ----- RabbitMQ (simple queue) -----
rabbit_broker = RabbitBroker(settings.rabbit_url, logger=logger)
rabbit_app = FastStream(rabbit_broker, logger=logger)


@rabbit_broker.subscriber("tasks")
async def on_rabbit_task(msg: str):
    logger.info("RabbitMQ received: {}", msg)
    action = Action(**orjson.loads(msg))
    req = action_to_reseed_proto(action)
    with grpc.insecure_channel(
        f"{settings.grpc_host_internal}:{settings.grpc_port}"
    ) as channel:
        stub = action_pb2_grpc.ActionServiceStub(channel)
        resp = stub.Reseed(req)
        logger.info("gRPC response: {}", resp)
        action = proto_to_action(resp)
        logger.info("gRPC action: {}", action)
    logger.info("RabbitMQ action: {}", action)


@rabbit_app.after_startup
async def rabbit_on_startup():
    logger.info("RabbitMQ consumer started, queue=tasks")


def run_rabbit():
    asyncio.run(rabbit_app.run())


# ----- Kafka (stream) -----
kafka_broker = KafkaBroker(settings.kafka_bootstrap_servers, logger=logger)
kafka_app = FastStream(kafka_broker, logger=logger)


@kafka_broker.subscriber(settings.kafka_topic, group_id=settings.kafka_consumer_group)
async def on_kafka_event(msg: str):
    logger.info("Kafka received: {}", msg)
    action = Action(**orjson.loads(msg))
    action = reseed_action_use_case.process(
        ReseedCommand(action=action, context=ActionContext(seed=random.randint(1, 1000000)))
    )
    payload = orjson.dumps(action.model_dump(mode="json")).decode()
    await publish_rabbit_task(payload)
    logger.info("Kafka reseeded: {}", action)


@kafka_app.after_startup
async def kafka_on_startup():
    logger.info("Kafka consumer started, topic={}", settings.kafka_topic)


def run_kafka():
    asyncio.run(kafka_app.run())
