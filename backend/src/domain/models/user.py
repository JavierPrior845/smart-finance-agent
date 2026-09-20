from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: str
    hashed_password: str
    current_token: str | None = None
    is_active: bool = True
    role: str = "admin"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
