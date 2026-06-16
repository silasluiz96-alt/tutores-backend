import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from unittest.mock import AsyncMock, patch
from app.main import app
from app.database import get_session
from app.auth import verificar_api_key
from app.models.tutor import Tutor

HEADERS = {"x-api-key": "chave-de-teste"}


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


@pytest.fixture(name="tutor_ativo")
def tutor_ativo_fixture(session: Session) -> Tutor:
    tutor = Tutor(
        titulo="Tutor de Testes",
        descricao="Usado nos testes automatizados",
        instrucoes="Responda sempre de forma curta e objetiva.",
        fontes=None,
        ativo=True,
    )
    session.add(tutor)
    session.commit()
    session.refresh(tutor)
    return tutor


@patch("app.services.chat.tutor_agent.responder", new_callable=AsyncMock)
def test_chat_responde(mock_responder, client: TestClient, tutor_ativo: Tutor):
    mock_responder.return_value = "Olá! Posso te ajudar."

    resposta = client.post(f"/api/v1/chat/{tutor_ativo.id}", json={
        "sessao_id": "sessao-001",
        "mensagem": "Olá, tudo bem?"
    })

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["resposta"] == "Olá! Posso te ajudar."
    assert dados["sessao_id"] == "sessao-001"


@patch("app.services.chat.tutor_agent.responder", new_callable=AsyncMock)
def test_chat_salva_historico(mock_responder, client: TestClient, tutor_ativo: Tutor):
    mock_responder.return_value = "Resposta do tutor."

    client.post(f"/api/v1/chat/{tutor_ativo.id}", json={
        "sessao_id": "sessao-002",
        "mensagem": "Primeira mensagem"
    })

    mock_responder.return_value = "Segunda resposta."

    resposta = client.post(f"/api/v1/chat/{tutor_ativo.id}", json={
        "sessao_id": "sessao-002",
        "mensagem": "Segunda mensagem"
    })

    assert resposta.status_code == 200
    # Verifica que o agente foi chamado duas vezes (histórico acumulando)
    assert mock_responder.call_count == 2
    # Na segunda chamada, o histórico deve conter 2 mensagens da primeira rodada
    segundo_historico = mock_responder.call_args_list[1].kwargs["historico"]
    assert len(segundo_historico) == 2


def test_chat_tutor_inexistente(client: TestClient):
    resposta = client.post("/api/v1/chat/9999", json={
        "sessao_id": "sessao-003",
        "mensagem": "Olá"
    })
    assert resposta.status_code == 404


def test_chat_tutor_inativo(client: TestClient, session: Session):
    tutor = Tutor(
        titulo="Tutor Inativo",
        descricao="Desativado",
        instrucoes="Não importa.",
        ativo=False,
    )
    session.add(tutor)
    session.commit()
    session.refresh(tutor)

    resposta = client.post(f"/api/v1/chat/{tutor.id}", json={
        "sessao_id": "sessao-004",
        "mensagem": "Olá"
    })
    assert resposta.status_code == 403
