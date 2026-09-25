# SaúdeDados — Backend

Implementação do backend conforme a documentação técnica de referência (`SaúdeDados — Especificação de Backend, v1.0`).

## Stack

FastAPI · PostgreSQL (SQLAlchemy 2.0 + Alembic) · Redis · JWT/RBAC

## Estrutura

```
app/
  api/v1/        rotas por módulo (dashboard, beneficiarios, atendimentos, prestadores, financeiro, relatorios, auth)
  core/          config, segurança (JWT), dependências (RBAC), paginação
  db/            sessão SQLAlchemy
  models/        entidades ORM (seção 2 da documentação)
  schemas/       schemas Pydantic (contratos de request/response)
alembic/
  versions/0001  schema transacional inicial (inclui particionamento de atendimentos)
  versions/0002  materialized views que alimentam o painel (seção 3 da documentação)
```

## Como rodar localmente

1. Copiar variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```

2. Subir banco de dados e Redis:
   ```bash
   docker compose up -d db redis
   ```

3. Instalar dependências:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```

4. Rodar as migrations:
   ```bash
   alembic upgrade head
   ```

5. Subir a API:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Documentação interativa (Swagger): `http://localhost:8000/docs`

7. (Opcional) Popular com dados de exemplo:
   ```bash
   python -m scripts.seed
   ```
   Cria beneficiários, prestadores, atendimentos, faturas e contratos fictícios, além de um usuário `admin@saudedados.local` (senha `trocar123`) para testar o login.

## Testes

```bash
pytest
```

A suíte roda sem dependência de banco (testes de unidade das regras de negócio, segurança e fumaça da API). Testes de integração que tocam o Postgres são pulados automaticamente a menos que `TEST_DATABASE_URL` esteja definida no ambiente.

## Pendências para produção (fora do escopo deste esqueleto)

- Job de refresh das materialized views (pg_cron ou worker agendado) — ver comentário em `alembic/versions/0002_materialized_views.py`.
- Automação de criação de novas partições mensais em `atendimentos` (ex.: pg_partman).
- Worker real de geração de relatórios (fila SQS) substituindo o `BackgroundTasks` de exemplo em `app/api/v1/relatorios.py`.
- Cache Redis nos endpoints de `/dashboard/*` (TTL já previsto em `KPI_CACHE_TTL_SECONDS`).
- Rotina de rotação/expiração de refresh tokens.
- Ampliar a suíte de testes com casos de integração (endpoints tocando banco real) via `TEST_DATABASE_URL`.
