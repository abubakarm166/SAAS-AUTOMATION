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
    is_admin: bool = False

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    password: str = Field(min_length=8)


class MessageOut(BaseModel):
    message: str


class BillingConfigOut(BaseModel):
    stripe_configured: bool
    price_configured: bool
    webhook_configured: bool
    bypass_subscription_check: bool
    monthly_enabled: bool = False
    yearly_enabled: bool = False


class CheckoutRequest(BaseModel):
    plan: str = Field(default="monthly")


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


class ExtractAddressesRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)


class ExtractAddressesOut(BaseModel):
    url: str
    addresses: list[str]
    count: int


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


class DailyCount(BaseModel):
    date: str
    count: int


class JobStatsOut(BaseModel):
    total: int
    queued: int
    running: int
    completed: int
    failed: int
    canceled: int
    addresses_total: int
    addresses_completed: int
    success_rate: float
    this_month: int
    last_30_days: int
    daily: list[DailyCount]


class AdminStatsOut(JobStatsOut):
    users_total: int
    subscribers_active: int


class AdminUserOut(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime
    job_count: int
    subscription_status: str | None


class AdminJobOut(BaseModel):
    id: UUID
    user_id: UUID
    user_email: EmailStr
    status: str
    source_url: str | None
    inputs: dict
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
