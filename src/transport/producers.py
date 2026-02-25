"""RabbitMQ and Kafka stream producers (publish to queue/topic)."""

from faststream.kafka import KafkaBroker
from faststream.rabbit import RabbitBroker
from loguru import logger

from src.core import settings

# Queue and topic names (must match consumers)
RABBIT_QUEUE = "tasks"
KAFKA_TOPIC = settings.kafka_topic


async def publish_rabbit_task(message: str) -> None:
    """Publish a message to the RabbitMQ `tasks` queue."""
    logger.info("Publishing to RabbitMQ queue={}: {}", RABBIT_QUEUE, message[:80])
    logger.info("Message: {}", message)
    broker = RabbitBroker(settings.rabbit_url)
    async with broker:
        await broker.publish(message, queue=RABBIT_QUEUE)
    logger.debug("Published to RabbitMQ queue={}: {}", RABBIT_QUEUE, message[:80])


async def publish_kafka_event(message: str) -> None:
    """Publish a message to the Kafka `events` topic."""
    broker = KafkaBroker(settings.kafka_bootstrap_servers)
    async with broker:
        await broker.publish(message, topic=KAFKA_TOPIC)
    logger.debug("Published to Kafka topic={}: {}", KAFKA_TOPIC, message[:80])
