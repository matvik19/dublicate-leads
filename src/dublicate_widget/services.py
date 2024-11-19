from src.amocrm.services import get_leads_by_filter_async
from aiohttp import ClientSession


async def duplicate_leads(subdomain: str, client_session: ClientSession):
    leads = await get_leads_by_filter_async(client_session, subdomain)
