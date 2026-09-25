import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import RolePerfil


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UsuarioMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    cargo: str | None
    email: EmailStr
    role: RolePerfil
