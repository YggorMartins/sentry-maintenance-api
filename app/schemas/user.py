"""
Schemas (contratos de entrada/saída da API) relacionados a usuário.

Regra importante: UserOut NUNCA inclui hashed_password. É comum ver
projetos iniciantes vazarem o hash da senha na resposta da API por
reutilizar o mesmo schema para entrada e saída — aqui separamos
explicitamente.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.roles import UserRole


class UserCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.CLIENTE


class UserOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
