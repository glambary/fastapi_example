from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from faststream.kafka import KafkaBroker
from faststream.kafka.fastapi import KafkaRouter
from starlette.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from broker.handlers import BROKER_HANDLERS
from common.application import App
from common.config import settings
from common.container import Container


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    print("The app is on")
    yield
    print("The app is off")


async def init_container() -> Container:
    """Инициализация контейнера DI."""

    router = KafkaRouter(
        settings.kafka.KAFKA_BROKER,
        lifespan=lifespan,
    )
    router.broker = KafkaBroker(settings.kafka.KAFKA_BROKER)

    container = Container(kafka_router=router, kafka_broker=router.broker)

    if resources := container.init_resources():
        await resources

    container.check_dependencies()

    return container


async def create_app() -> App:
    """Формирование app для запуска."""
    container = await init_container()

    app = App()
    app.container = container

    # Kafka
    kafka_router = container.kafka_router()
    kafka_broker = container.kafka_broker()
    # Регистрация обработчиков брокера
    for topic, func in BROKER_HANDLERS.items():
        kafka_broker.subscriber(topic)(func)

    app.include_router(kafka_router)
    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=settings.app.CORS_ALLOW_CREDENTIALS,
        allow_origins=settings.app.CORS_ALLOW_ORIGINS,
        allow_methods=settings.app.CORS_ALLOW_METHODS,
        allow_headers=settings.app.CORS_ALLOW_HEADERS,
    )

    return app
