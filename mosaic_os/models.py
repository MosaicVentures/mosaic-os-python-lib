from datetime import datetime

from pydantic import BaseModel, Field

from mosaic_os.utils import datetime_now


class CompanyMetadata(BaseModel):
    merged: bool = False
    merged_at: datetime | None = None
    merged_to: list[int] = []
    merged_from: list[int] = []
    merged_by: str | None = None
    creator_source: str
    creator_event_type: str


class Company(BaseModel):
    id: int | None
    name: str
    primary_domain: str
    domains: list[str]
    sp_id: str | None = None
    crm_id: str | None = None
    pb_id: str | None = None
    crunchbase_id: str | None = None
    crunchbase_url: str | None = None
    pitchbook_url: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    stackoverflow_url: str | None = None
    angellist_url: str | None = None
    current: bool = True
    metadata: CompanyMetadata | None = None
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime | None = None
