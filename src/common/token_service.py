from src.common.config import CLIENT_ID
from src.rabbitmq.rpc_consumer import send_rpc_request_and_wait_for_reply
from loguru import logger
from fastapi import HTTPException


async def get_tokens_from_service(subdomain: str) -> dict:
    """Получение токенов через RabbitMQ."""
    try:
        # Отправляем RPC запрос и ждем ответа
        tokens = await send_rpc_request_and_wait_for_reply(
            subdomain=subdomain, client_id=CLIENT_ID
        )
        if not tokens["access_token"] or not tokens["refresh_token"]:
            logger.error(f"Invalid tokens received: {tokens}")
            raise HTTPException(status_code=500, detail="Invalid tokens received")
        return tokens

    except Exception as e:
        logger.exception(f"Error during token retrieval: {e}")
        raise HTTPException(status_code=500, detail="Error during token retrieval")
