from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WorkerJobOut(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    source_url: str | None
    inputs: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class JobCompletePayload(BaseModel):
    output_rows: list[dict] = Field(default_factory=list)
    files: list[dict] = Field(default_factory=list)


class JobFailPayload(BaseModel):
    error_message: str
