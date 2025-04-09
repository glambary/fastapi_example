from schemas.order import OrderBrokerSchema


async def handle_new_order(
    data: OrderBrokerSchema,
) -> None:
    id_ = data.id
    print(f"Handle new order id={id_}")


BROKER_HANDLERS = {
    "new_order": handle_new_order,
}
