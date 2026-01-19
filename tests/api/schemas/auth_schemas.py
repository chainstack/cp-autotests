from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserProfile(BaseModel):
    id: str
    username: str
    email: EmailStr
    tenant_id: str
    tenant_name: str
    tenant_role: str
    created_at: datetime
    last_login: Optional[datetime] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int = Field(gt=0)
    user: UserProfile


class RefreshTokenResponse(BaseModel):
    access_token: str
    expires_in: int = Field(gt=0)


class LogoutResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str


class ChangePasswordResponse(BaseModel):
    message: str


class AuditLogEntry(BaseModel):
    id: str
    user_id: str
    action: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[dict] = None


class AuditLogResponse(BaseModel):
    results: list[AuditLogEntry]
    total: int
    page: int
    page_size: int
