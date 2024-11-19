from pydantic import BaseModel


class GetDuplicateSchemaResponse(BaseModel):
    pass


class GetDuplicateSchema(BaseModel):
    subdomain: str
    pipeline_id: int


class CreateDuplicateSchema(BaseModel):
    pass
