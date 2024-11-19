import aio_pika
import asyncio
import json
import uuid
from loguru import logger

from fastapi import HTTPException

from src.common.config import RMQ_USER, RMQ_HOST, RMQ_PORT, RMQ_VHOST, RMQ_PASSWORD

CONNECTION_URL = f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}:{RMQ_PORT}/{RMQ_VHOST}"


async def send_rpc_request_and_wait_for_reply(subdomain: str, client_id: str):
    """
    Отправка RPC запроса в очередь и ожидание ответа.
    """
    correlation_id = str(uuid.uuid4())  # Уникальный идентификатор запроса
    logger.info("СГЕНЕРИРОВАЛИ correlation_id", correlation_id)
    reply_queue_name = f"reply_queue_{correlation_id}"  # Уникальная очередь для ответа
    logger.info(f"Определили reply_queue_name {reply_queue_name}")

    connection = await aio_pika.connect_robust(CONNECTION_URL)
    async with connection:
        channel = await connection.channel()

        # Объявляем временную очередь для ответа
        reply_queue = await channel.declare_queue(reply_queue_name, exclusive=True)

        # Формируем тело сообщения
        message_body = json.dumps({
            "client_id": client_id,
            "subdomain": subdomain
        })

        message = aio_pika.Message(
            body=message_body.encode(),
            correlation_id=correlation_id,
            reply_to=reply_queue_name
        )

        # Отправляем запрос в очередь
        await channel.default_exchange.publish(
            message, routing_key="tokens_get_user"
        )

        # Ожидаем ответа в reply_queue
        async with reply_queue.iterator() as reply_queue_iter:
            async for incoming_message in reply_queue_iter:
                async with incoming_message.process():
                    logger.info(f"Сообщение с токенами упало в: {reply_queue_name}")
                    if incoming_message.correlation_id == correlation_id:
                        # Декодируем и возвращаем ответ с токенами
                        response = json.loads(incoming_message.body.decode())
                        return {
                            "access_token": response.get("access_token"),
                            "refresh_token": response.get("refresh_token"),
                        }

    # Если не получили ответ
    raise HTTPException(status_code=504, detail="No response received from token service")


