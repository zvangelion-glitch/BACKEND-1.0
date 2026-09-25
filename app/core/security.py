from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

settings = get_settings()

_BCRYPT_MAX_BYTES = 72  # limite físico do algoritmo bcrypt


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha_plana.encode("utf-8")[:_BCRYPT_MAX_BYTES], senha_hash.encode("utf-8"))


def gerar_hash_senha(senha_plana: str) -> str:
    hash_bytes = bcrypt.hashpw(senha_plana.encode("utf-8")[:_BCRYPT_MAX_BYTES], bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def criar_access_token(subject: str, role: str) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expira_em, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def criar_refresh_token(subject: str) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {"sub": subject, "exp": expira_em, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
