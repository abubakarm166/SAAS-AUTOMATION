from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JobInputs(BaseModel):
    recipient_email: EmailStr | None = None
    addresses: list[str] = Field(default_factory=list)
    interest_rate: float = 0.06
    years: int = 30
    discount_percentage: float = 0.25
    closing_costs_input: float = 0.04
    money_down_input: float = 0.2
    operating_expenses_input: float = 0.02
    additional_annual_income_input: float = 0
    vacancy_allowance_percent_input: float = 0.05
    lender_ltv_input: float = 0.75
    rehab_costs_est_input: float = 0.25
    refi_loan_amount_input: float = 0.5
    refi_closing_costs_est_input: float = 0.04
    num_months_holding: int = 3


class JobCreate(BaseModel):
    source_url: str | None = None
    inputs: JobInputs


class JobOut(BaseModel):
    id: UUID
    status: str
    source_url: str | None
    inputs: dict
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobFileOut(BaseModel):
    id: UUID
    file_type: str
    filename: str
    s3_key: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FileDownloadOut(BaseModel):
    url: str
    expires_in: int
    filename: str


class SubscriptionOut(BaseModel):
    status: str
    plan_id: str | None
    current_period_end: datetime | None

    model_config = {"from_attributes": True}
