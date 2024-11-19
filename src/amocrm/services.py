from loguru import logger

from typing import AsyncGenerator, Dict, Any

from aiohttp import ClientSession
from fastapi import HTTPException

import json
from typing import List

import aiohttp


async def get_headers(subdomain: str, access_token: str) -> Dict:
    """Получение headers для запросов"""

    headers = {
        "Host": subdomain + ".amocrm.ru",
        "Content - Length": "0",
        "Content - Type": "application / json",
        "Authorization": "Bearer " + access_token,
    }

    return headers


async def get_client_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """Асинхронная ссесия для запросов к амо"""

    async with aiohttp.ClientSession() as session:
        yield session


async def get_leads_by_filter_async(
    client_session: ClientSession,
    subdomain: str,
    headers: dict,
    pipeline_id: int,
    statuses_ids: List[int] = None,
    responsible_user_id: int = None,
) -> List[dict]:
    """Асинхронное получение сделок с помощью фильтра"""

    """
    FILTERS:
        filter[responsible_user_id] - по ответственному
        filter[pipeline_id] - по воронке
        filter[status][] - по статусам
    """

    params = {"filter[pipeline_id]": pipeline_id}
    if statuses_ids:
        for i, status_id in enumerate(statuses_ids):
            params[f"filter[status][{i}]"] = status_id
    if responsible_user_id:
        params["filter[responsible_user_id]"] = responsible_user_id

    url = f"https://{subdomain}.amocrm.ru/api/v4/leads?with=contacts"

    try:
        # Выполняем запрос к API
        async with client_session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                # Пытаемся прочитать JSON-ответ
                response_json = await response.json()

                # Извлекаем список сделок из ответа JSON
                leads = response_json.get("_embedded", {}).get("leads", [])
                return leads

            elif response.status == 204:
                logger.warning(
                    f"No content returned (204) for pipeline {pipeline_id}. No leads available."
                )
                return []
            else:
                # Обрабатываем случаи, когда API вернул ошибочный статус
                error_message = await response.text()
                logger.error(
                    f"Error fetching leads (status {response.status}): {error_message}",
                    exception=True,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch leads: {error_message}",
                )

    except aiohttp.ClientError as client_err:
        # Обработка ошибок, связанных с сетью
        logger.error(f"Network or client error occurred: {client_err}", exception=True)
        raise HTTPException(
            status_code=502, detail="Bad Gateway - Error connecting to AmoCRM"
        )
    except Exception as e:
        # Обрабатываем любые другие ошибки
        logger.error(f"Unexpected error occurred while fetching leads", exception=True)
        raise HTTPException(
            status_code=500, detail="Unexpected error occurred while fetching leads"
        )


async def get_lead_by_id(
    lead_id: int, subdomain: str, headers: dict, client_session: ClientSession
) -> Dict[str, Any]:
    """Получение объекта сделки по id сделки."""

    url = f"https://{subdomain}.amocrm.ru/api/v4/leads/{lead_id}?with=contacts"

    try:
        async with client_session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data
                except Exception as json_err:
                    logger.error(
                        f"Failed to parse JSON from response: {json_err}",
                        exception=True,
                    )
                    raise HTTPException(
                        status_code=500, detail="Failed to parse server response"
                    )
            elif response.status == 404:
                logger.warning(f"Lead with id {lead_id} not found.")
                raise HTTPException(
                    status_code=404, detail=f"Lead with id {lead_id} not found"
                )
            else:
                error_message = await response.text()
                logger.error(
                    f"Error fetching lead (status {response.status}): {error_message}",
                    exception=True,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch lead with id {lead_id}. Error: {error_message}",
                )

    except aiohttp.ClientError as client_err:
        logger.error(
            f"Network error while fetching lead with id {lead_id}: {client_err}",
            exception=True,
        )
        raise HTTPException(
            status_code=502, detail="Bad Gateway - Error connecting to AmoCRM"
        )

    except Exception as e:
        logger.error(f"Unexpected error while fetching lead with id {lead_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while fetching lead with id {lead_id}",
        )


async def get_contact_by_id(
    contact_id: int, subdomain: str, headers: dict, client_session: ClientSession
) -> Dict[str, Any]:
    """Получение объекта контакта по id контакта"""

    url = f"https://{subdomain}.amocrm.ru/api/v4/contacts/{contact_id}"

    try:
        async with client_session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data
                except Exception as json_err:
                    logger.error(
                        f"Failed to parse JSON from response: {json_err}",
                        exception=True,
                    )
                    raise HTTPException(
                        status_code=500, detail="Failed to parse server response"
                    )
            else:
                error_message = await response.text()
                logger.error(
                    f"Error fetching contact (status {response.status}): {error_message}",
                    exception=True,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch contact with id {contact_id}. Error: {error_message}",
                )

    except aiohttp.ClientError as client_err:
        logger.error(
            f"Network error while fetching contact with id {contact_id}: {client_err}",
            exception=True,
        )
        raise HTTPException(
            status_code=502, detail="Bad Gateway - Error connecting to AmoCRM"
        )

    except Exception as e:
        logger.error(
            f"Unexpected error while fetching contact with id {contact_id}: {e}",
            exception=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_all_contacts(
    subdomain: str, headers: dict, client_session: ClientSession
) -> List[Dict[str, int]]:
    """Получение всех контактов"""

    url = f"https://{subdomain}.amocrm.ru/api/v4/contacts"

    try:
        # Выполняем запрос к API
        async with client_session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    contacts = [
                        {
                            "id": contact["id"],
                            "responsible_user_id": contact["responsible_user_id"],
                        }
                        for contact in data["_embedded"]["contacts"]
                    ]
                    return contacts
                except KeyError as key_err:
                    logger.error(
                        f"Missing expected key in response data: {key_err}",
                        exception=True,
                    )
                    raise HTTPException(
                        status_code=500, detail="Unexpected response format from server"
                    )
                except Exception as json_err:
                    logger.error(
                        f"Failed to parse JSON from response: {json_err}",
                        exception=True,
                    )
                    raise HTTPException(
                        status_code=500, detail="Failed to parse server response"
                    )
            else:
                error_message = await response.text()
                logger.error(
                    f"Error fetching contacts (status {response.status}): {error_message}",
                    exception=True,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch contacts. Error: {error_message}",
                )

    except aiohttp.ClientError as client_err:
        logger.error(
            f"Network error while fetching contacts: {client_err}", exception=True
        )
        raise HTTPException(
            status_code=502, detail="Bad Gateway - Error connecting to AmoCRM"
        )

    except Exception as e:
        logger.error(
            f"Unexpected error occurred while fetching contacts: {e}", exception=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_company_by_id(
    company_id: int, subdomain: str, headers: dict, client_session: ClientSession
) -> Dict[str, Any]:
    """Получение объкта компании по id"""

    url = f"https://{subdomain}.amocrm.ru/api/v4/companies/{company_id}"

    try:
        async with client_session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data
                except Exception as json_err:
                    logger.error(
                        f"Failed to parse JSON from response: {json_err}",
                        exception=True,
                    )
                    raise HTTPException(
                        status_code=500, detail="Failed to parse server response"
                    )
            else:
                error_message = await response.text()
                logger.error(
                    f"Error fetching company (status {response.status}): {error_message}",
                    exception=True,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch company with id {company_id}. Error: {error_message}",
                )

    except aiohttp.ClientError as client_err:
        logger.error(
            f"Network error while fetching company with id {company_id}: {client_err}",
            exception=True,
        )
        raise HTTPException(
            status_code=502, detail="Bad Gateway - Error connecting to AmoCRM"
        )

    except Exception as e:
        logger.error(
            f"Unexpected error while fetching company with id {company_id}: {e}",
            exception=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")
