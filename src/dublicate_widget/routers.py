from fastapi import APIRouter, HTTPException

from src.dublicate_widget.schemas import (
    GetDuplicateSchema,
    CreateDuplicateSchema,
    GetDuplicateSchemaResponse,
)
from src.dublicate_widget.services import duplicate_leads

router = APIRouter(prefix="/duplicate_leads", tags=["Managers"])


@router.get("/get", response_model=list[GetDuplicateSchemaResponse])
async def get_leads_to_gluing(data: GetDuplicateSchema):
    """Получение сделок, которые являются дублями"""

    leds_to_gluing = await duplicate_leads()


@router.post("/post", response_model=CreateDuplicateSchema)
async def get_managers(subdomain: str):
    pass
