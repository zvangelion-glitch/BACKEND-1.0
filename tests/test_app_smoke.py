class TestHealthCheck:
    def test_health_retorna_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestOpenAPISchema:
    def test_openapi_carrega(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_todas_as_rotas_dos_modulos_estao_registradas(self, client):
        paths = client.get("/openapi.json").json()["paths"]

        rotas_esperadas = [
            "/api/v1/auth/login",
            "/api/v1/auth/me",
            "/api/v1/dashboard/kpis",
            "/api/v1/dashboard/evolucao-atendimentos",
            "/api/v1/dashboard/distribuicao-especialidade",
            "/api/v1/dashboard/top-prestadores",
            "/api/v1/dashboard/tempo-medio-atendimento",
            "/api/v1/dashboard/avisos",
            "/api/v1/beneficiarios",
            "/api/v1/beneficiarios/perfil-populacional",
            "/api/v1/atendimentos",
            "/api/v1/prestadores",
            "/api/v1/financeiro/faturas",
            "/api/v1/financeiro/contratos",
            "/api/v1/relatorios/gerar",
        ]
        for rota in rotas_esperadas:
            assert rota in paths, f"Rota ausente no schema: {rota}"

    def test_rotas_protegidas_exigem_autenticacao(self, client):
        # sem token, endpoints autenticados devem responder 401, nunca 200
        for rota in ["/api/v1/dashboard/kpis?periodo_inicio=2026-01-01&periodo_fim=2026-08-31", "/api/v1/beneficiarios", "/api/v1/auth/me"]:
            response = client.get(rota)
            assert response.status_code == 401, f"{rota} deveria exigir autenticação"
