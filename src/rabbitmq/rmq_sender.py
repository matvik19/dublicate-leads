import aio_pika
from loguru import logger


async def send_response_message(connection_url: str, message_body: str, reply_to: str, correlation_id: str):
    """Отправка сообщения в указанную очередь RabbitMQ."""
    try:
        # Подключаемся к RabbitMQ
        connection = await aio_pika.connect_robust(connection_url)
        async with connection:
            channel = await connection.channel()

            # Создаем сообщение с указанными свойствами
            response_message = aio_pika.Message(
                body=message_body.encode("utf-8"),
                correlation_id=correlation_id
            )

            # Публикуем сообщение в очередь, указанную в reply_to
            await channel.default_exchange.publish(
                response_message,
                routing_key=reply_to
            )
            logger.info(f"Sent response to {reply_to} with Correlation ID: {correlation_id}")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
