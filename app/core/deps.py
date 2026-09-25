import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decodificar_token
from app.db.session import get_db
from app.models.enums import RolePerfil
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token)
        if payload.get("type") != "access":
            raise credenciais_invalidas
        usuario_id = payload.get("sub")
    except jwt.PyJWTError:
        raise credenciais_invalidas

    usuario = db.get(Usuario, uuid.UUID(usuario_id))
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas
    return usuario


def exigir_roles(*roles_permitidos: RolePerfil):
    """Factory de dependência para restringir endpoints por perfil de acesso (RBAC)."""

    def verificador(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.role not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não possui permissão para este recurso",
            )
        return usuario

    return verificador
