from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_serializer

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


class AisDelivery(BaseModel):
    delivery_destination: str
    delivery_id: str
    delivery_at: datetime = Field(default_factory=datetime_now)


class AisType(Enum):
    REMINDER = "reminder"
    COMPANY_REVIEW = "company_review"
    AUTOMATED_REMINDER = "automated_reminder"


class SignalSource(Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class SignalType(Enum):
    COMPANY = "company"
    PEOPLE = "people"


class ActionItemMetadata(BaseModel):
    source: str
    event_type: str
    source_id: str
    crm_reset_type: AffinityReminderResetType | None = None

    class Config:
        extra = "allow"


class ActionItemSfnMetadata(BaseModel):
    source: str
    event_type: str
    event_id: str
    received_at: datetime = Field(default_factory=datetime_now)
    user_approved: bool = False

    class Config:
        extra = "allow"


class User(BaseModel):
    email: str
    name: str
    crm_id: int | None = None


class Search(BaseModel):
    signal_source: SignalSource
    signal_type: SignalType
    search_id: str
    search_name: str
    applied_weight: float
    weights: dict[str, float]

    @field_serializer("signal_source")
    def serialize_signal_source(self, signal_source: SignalSource):
        return signal_source.value

    @field_serializer("signal_type")
    def serialize_signal_type(self, signal_type: SignalType):
        return signal_type.value


class Score(BaseModel):
    created_at: datetime
    searches: list[Search]


class ActionItem(BaseModel):
    id: int | None
    content: str | None = None
    status: ActionItemStatus = ActionItemStatus.ACTIVE
    due_date: datetime | None
    creator: User
    completer: User | None = None
    owner: User
    tagged_persons: list[User] = []
    tagged_crm_opportunity_id: int | None = None
    company: CompanyBase | None = None
    last_delivery: AisDelivery | None = None
    deliveries: list[AisDelivery] = []
    sfn_completed: bool = False
    sfn_completed_at: datetime | None = None
    sfn_metadata: list[ActionItemSfnMetadata] | None = None
    ais_type: AisType = AisType.REMINDER
    score: Score | None = None
    metadata: ActionItemMetadata | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime | None = None

    @field_serializer("status")
    def serialize_status(self, action_item_status: ActionItemStatus):
        return action_item_status.value

    @field_serializer("ais_type")
    def serialize_ais_type(self, ais_type: AisType):
        return ais_type.value
