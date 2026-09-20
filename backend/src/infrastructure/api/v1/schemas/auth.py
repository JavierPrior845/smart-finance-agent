from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario o administrador")
    email: str = Field(..., min_length=5, max_length=255, description="Correo electrónico único")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña de acceso")


class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Correo electrónico")
    password: str = Field(..., description="Contraseña de acceso")


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserResponse


class SetupStatusResponse(BaseModel):
    is_configured: bool
    user_count: int
