import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.auth import verificar_api_key

API_KEY = "chave-de-teste"
HEADERS = {"x-api-key": API_KEY}


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_session():
        yield session

    def override_api_key():
        pass

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[verificar_api_key] = override_api_key
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_criar_tutor(client: TestClient):
    resposta = client.post("/api/v1/tutores/", json={
        "titulo": "Tutor de Python",
        "descricao": "Ensina Python do zero",
        "instrucoes": "Responda sempre em português e use exemplos simples.",
        "fontes": "https://docs.python.org"
    }, headers=HEADERS)
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["titulo"] == "Tutor de Python"
    assert dados["ativo"] is True


def test_listar_tutores(client: TestClient):
    client.post("/api/v1/tutores/", json={
        "titulo": "Tutor de FastAPI",
        "descricao": "Ensina FastAPI",
        "instrucoes": "Seja objetivo.",
    }, headers=HEADERS)
    resposta = client.get("/api/v1/tutores/", headers=HEADERS)
    assert resposta.status_code == 200
    assert len(resposta.json()) >= 1


def test_buscar_tutor(client: TestClient):
    criado = client.post("/api/v1/tutores/", json={
        "titulo": "Tutor de SQL",
        "descricao": "Ensina SQL",
        "instrucoes": "Use exemplos práticos.",
    }, headers=HEADERS).json()
    resposta = client.get(f"/api/v1/tutores/{criado['id']}", headers=HEADERS)
    assert resposta.status_code == 200
    assert resposta.json()["id"] == criado["id"]


def test_atualizar_tutor(client: TestClient):
    criado = client.post("/api/v1/tutores/", json={
        "titulo": "Tutor Antigo",
        "descricao": "Descrição antiga",
        "instrucoes": "Instrução antiga.",
    }, headers=HEADERS).json()
    resposta = client.patch(f"/api/v1/tutores/{criado['id']}", json={
        "titulo": "Tutor Atualizado"
    }, headers=HEADERS)
    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Tutor Atualizado"


def test_desativar_tutor(client: TestClient):
    criado = client.post("/api/v1/tutores/", json={
        "titulo": "Tutor para Desativar",
        "descricao": "Será desativado",
        "instrucoes": "Instrução.",
    }, headers=HEADERS).json()
    resposta = client.delete(f"/api/v1/tutores/{criado['id']}", headers=HEADERS)
    assert resposta.status_code == 200
    assert resposta.json()["ativo"] is False


def test_api_key_invalida(session: Session):
    import os
    os.environ["ADMIN_API_KEY"] = "chave-correta"

    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides.pop(verificar_api_key, None)

    with TestClient(app) as client:
        resposta = client.get("/api/v1/tutores/", headers={"x-api-key": "chave-errada"})
        assert resposta.status_code == 401

    app.dependency_overrides.clear()
