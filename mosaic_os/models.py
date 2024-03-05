from pydantic import BaseModel


class CompanyMetadata(BaseModel):
    merged_company: dict | None = None


class Company(BaseModel):
    id: int | None
    domains: list[str]
    sp_id: str | None = None
    crm_id: str | None = None
    metadata: CompanyMetadata | None = None
