from datetime import datetime

from pydantic import BaseModel, Field

from mosaic_os.utils import datetime_now


class CompanyMetadata(BaseModel):
    merged: bool = False
    merged_at: datetime | None = None
    merged_from: list[str] = []
    merged_by: str


class Company(BaseModel):
    id: int | None
    name: str
    primary_domain: str
    domains: list[str]
    sp_id: str | None = None
    crm_id: str | None = None
    pb_id: str | None = None
    current: bool = True
    metadata: CompanyMetadata | None = None
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime | None = None
