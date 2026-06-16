from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, UTC


class Tutor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descricao: str
    instrucoes: str
    fontes: Optional[str] = None  # URLs separadas por vírgula
    ativo: bool = True
    criado_em: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TutorCreate(SQLModel):
    titulo: str
    descricao: str
    instrucoes: str
    fontes: Optional[str] = None


class TutorUpdate(SQLModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    instrucoes: Optional[str] = None
    fontes: Optional[str] = None
    ativo: Optional[bool] = None
