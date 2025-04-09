from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from faststream.kafka import KafkaBroker
from faststream.types import SendableMessage


@inject
async def broker_publish(
    message: SendableMessage,
    topic: str,
    broker: KafkaBroker = Depends(Provide["kafka_broker"]),
) -> None:
    return await broker.publish(
        message=message,
        topic=topic,
    )
