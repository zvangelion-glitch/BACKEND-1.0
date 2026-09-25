from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_usuario_atual
from app.core.security import criar_access_token, criar_refresh_token, verificar_senha
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioMe

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    usuario = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if usuario is None or not verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    if not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")

    return TokenResponse(
        access_token=criar_access_token(str(usuario.id), usuario.role.value),
        refresh_token=criar_refresh_token(str(usuario.id)),
    )


@router.get("/me", response_model=UsuarioMe)
def me(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    return usuario
