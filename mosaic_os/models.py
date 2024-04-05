from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from mosaic_os.crm import AffinityReminderResetType
from mosaic_os.utils import datetime_now


class CompanyMetadata(BaseModel):
    merged: bool = False
    merged_at: datetime | None = None
    merged_to: list[int] = []
    merged_from: list[int] = []
    merged_by: str | None = None
    creator_source: str
    creator_event_type: str


class CompanyBase(BaseModel):
    id: int | None
    name: str
    primary_domain: str
    domains: list[str]
    sp_id: str | None = None
    crm_id: str | None = None


class Company(CompanyBase):
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


class ActionItemStatus(Enum):
    COMPLETED = 0
    ACTIVE = 1
    OVERDUE = 2


class ActionItemMetadata(BaseModel):
    source: str
    event_type: str
    source_id: str
    crm_reset_type: AffinityReminderResetType | None = None

    class Config:
        extra = "allow"


class User(BaseModel):
    email: str
    name: str
    crm_id: int | None = None


class Score(BaseModel):
    total_score: float
    weighting_vector: list[float]
    company_score: float
    people_score: float
    internal_score: float
    company_searches: list[str]
    people_searches: list[str]
    internal_searches: list[str]


class ActionItem(BaseModel):
    id: int | None
    content: str
    status: ActionItemStatus = ActionItemStatus.ACTIVE
    due_date: datetime | None
    creator: User
    completer: User | None = None
    owner: User
    tagged_persons: list[User] = []
    tagged_crm_opportunity_id: int | None = None
    company: CompanyBase | None = None
    last_delivery_id: str | None = None
    delivery_ids: list[str] = []
    score: Score | None = None
    metadata: ActionItemMetadata | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime | None = None
