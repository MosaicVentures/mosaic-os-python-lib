from datetime import datetime

from pydantic import BaseModel, Field

from mosaic_os.utils import datetime_now


class CompanyMetadata(BaseModel):
    merged_company: dict | None = None


class Company(BaseModel):
    id: int | None
    domains: list[str]
    sp_id: str | None = None
    crm_id: str | None = None
    metadata: CompanyMetadata | None = None
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime | None = None
