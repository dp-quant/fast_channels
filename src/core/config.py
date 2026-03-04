"""Pydantic Settings / ENV loading."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "fast_channels"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # service version
    version: str = "0.1.0"
    
    # RabbitMQ
    rabbit_url: str = "amqp://guest:guest@rabbitmq:5672/"

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic: str = "events"
    kafka_consumer_group: str = "fast_channels_events"

    # HTTP
    http_host: str = "0.0.0.0"
    http_host_internal: str = "http"
    http_port: int = 8000

    # gRPC
    grpc_host: str = "0.0.0.0"
    grpc_host_internal: str = "grpc"
    grpc_port: int = 50051

    # Logging
    log_level: str = "INFO"
    


settings = Settings()
