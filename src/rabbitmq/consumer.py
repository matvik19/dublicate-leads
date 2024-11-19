import json

from loguru import logger

import aio_pika
from src.common.database import get_async_session
from src.rabbitmq.rmq_sender import send_response_message


async def process_message(
    message: aio_pika.IncomingMessage, process_func, connection_url: str
):
    """
    :param message: Сообщение из очереди RabbitMQ.
    :param process_func: Функция для обработки данных сообщения.
    :param connection_url: URL подключения к RabbitMQ для отправки ответов.
    """
    async with message.process():
        body = message.body.decode("utf-8")
        data = json.loads(body)
        logger.info("Get message from RMQ")
        session = get_async_session()

        try:
            # Вызов основной логики обработки
            result = await process_func(data, session)

            # Если присутствует reply_to, отправляем ответ
            if message.reply_to and message.correlation_id:
                response_body = json.dumps(result)
                await send_response_message(
                    connection_url,
                    response_body,
                    message.reply_to,
                    message.correlation_id,
                )
        except Exception as e:
            logger.info("Error processing message.", e)


async def start_consumer(queue_name: str, connection_url: str, process_func):
    """
    :param queue_name: Название очереди RabbitMQ.
    :param connection_url: URL подключения к RabbitMQ.
    :param process_func: Функция для обработки сообщений.
    """
    connection = await aio_pika.connect_robust(connection_url)
    channel = await connection.channel()

    queue = await channel.declare_queue(queue_name, durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await process_message(message, process_func, connection_url)
