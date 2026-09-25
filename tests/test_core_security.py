import pytest

from app.core.security import (
    criar_access_token,
    criar_refresh_token,
    decodificar_token,
    gerar_hash_senha,
    verificar_senha,
)


class TestHashSenha:
    def test_hash_e_verificacao_bem_sucedida(self):
        hash_gerado = gerar_hash_senha("minhaSenh@123")
        assert verificar_senha("minhaSenh@123", hash_gerado) is True

    def test_hash_rejeita_senha_incorreta(self):
        hash_gerado = gerar_hash_senha("minhaSenh@123")
        assert verificar_senha("senhaErrada", hash_gerado) is False

    def test_hash_nunca_armazena_texto_plano(self):
        senha = "minhaSenh@123"
        assert gerar_hash_senha(senha) != senha


class TestTokensJWT:
    def test_access_token_contem_subject_e_role(self):
        token = criar_access_token(subject="usuario-123", role="admin")
        payload = decodificar_token(token)
        assert payload["sub"] == "usuario-123"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_refresh_token_nao_contem_role(self):
        token = criar_refresh_token(subject="usuario-123")
        payload = decodificar_token(token)
        assert payload["sub"] == "usuario-123"
        assert payload["type"] == "refresh"
        assert "role" not in payload

    def test_token_invalido_levanta_erro(self):
        import jwt as pyjwt

        with pytest.raises(pyjwt.PyJWTError):
            decodificar_token("token.invalido.aqui")
