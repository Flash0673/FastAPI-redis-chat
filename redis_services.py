import asyncio

from fastapi.websockets import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

connection = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True,
)


async def redis_connector(websocket: WebSocket):
    async def consumer_handler(connection: redis, ws: WebSocket):
        try:
            while True:
                message = await ws.receive_text()
                if message:
                    await connection.publish("channel:1", message)
        except WebSocketDisconnect as exc:
            print(exc)

    async def producer_handler(
            pubsub: redis.client.PubSub,
            ws: WebSocket,
    ):
        try:
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True
                )
                if message:
                    await ws.send_text(message.get("data"))
        except Exception as exc:
            print(exc)

    async with connection.pubsub() as pubsub:
        await pubsub.psubscribe("channel:*")

        consumer_task = asyncio.create_task(consumer_handler(
            connection=connection,
            ws=websocket
        ))
        producer_task = asyncio.create_task(producer_handler(
            pubsub=pubsub,
            ws=websocket
        ))

        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
