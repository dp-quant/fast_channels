"""FastStream (Kafka / RabbitMQ) consumer logic."""

import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream.kafka import KafkaBroker
from src.core.logging import logger

from src.core import settings


# ----- RabbitMQ (simple queue) -----
rabbit_broker = RabbitBroker(settings.rabbit_url, logger=logger)
rabbit_app = FastStream(rabbit_broker, logger=logger)


@rabbit_broker.subscriber("tasks")
async def on_rabbit_task(msg: str):
    logger.info("RabbitMQ received: {}", msg)


@rabbit_app.after_startup
async def rabbit_on_startup():
    logger.info("RabbitMQ consumer started, queue=tasks")


def run_rabbit():
    asyncio.run(rabbit_app.run())


# ----- Kafka (stream) -----
kafka_broker = KafkaBroker(settings.kafka_bootstrap_servers, logger=logger)
kafka_app = FastStream(kafka_broker, logger=logger)


@kafka_broker.subscriber(settings.kafka_topic)
async def on_kafka_event(msg: str):
    logger.info("Kafka received: {}", msg)


@kafka_app.after_startup
async def kafka_on_startup():
    logger.info("Kafka consumer started, topic={}", settings.kafka_topic)


def run_kafka():
    asyncio.run(kafka_app.run())
