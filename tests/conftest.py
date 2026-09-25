import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.main import app


@pytest.fixture(scope="session")
def db_disponivel() -> bool:
    """
    Testes de integração (que tocam o banco) só rodam se houver um Postgres
    acessível via TEST_DATABASE_URL. Sem isso, são pulados (skip) em vez de falhar —
    útil para rodar a suíte de unidade sem infraestrutura local.
    """
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        return False
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def db_session(db_disponivel):
    if not db_disponivel:
        pytest.skip("TEST_DATABASE_URL não configurada ou banco indisponível — pulando teste de integração")

    url = os.getenv("TEST_DATABASE_URL")
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
