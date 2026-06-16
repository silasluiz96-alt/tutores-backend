from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC


class Mensagem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tutor_id: int = Field(foreign_key="tutor.id")
    sessao_id: str
    papel: str  # "usuario" ou "assistente"
    conteudo: str
    criado_em: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ChatInput(SQLModel):
    sessao_id: str
    mensagem: str


class ChatOutput(SQLModel):
    sessao_id: str
    resposta: str
