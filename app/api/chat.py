from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.models.mensagem import ChatInput, ChatOutput
from app.services import chat as servico

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{tutor_id}", response_model=ChatOutput)
async def conversar(
    tutor_id: int,
    dados: ChatInput,
    session: Session = Depends(get_session),
):
    return await servico.processar_chat(tutor_id, dados, session)
