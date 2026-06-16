import logging
from sqlmodel import Session, select
from app.models.mensagem import Mensagem, ChatInput, ChatOutput
from app.models.tutor import Tutor
from app.agent import tutor_agent
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def _buscar_historico(tutor_id: int, sessao_id: str, session: Session) -> list[dict]:
    mensagens = session.exec(
        select(Mensagem)
        .where(Mensagem.tutor_id == tutor_id)
        .where(Mensagem.sessao_id == sessao_id)
        .order_by(Mensagem.criado_em)
    ).all()
    return [{"papel": m.papel, "conteudo": m.conteudo} for m in mensagens]


def _salvar_turno(tutor_id: int, sessao_id: str, msg_usuario: str, msg_assistente: str, session: Session):
    session.add(Mensagem(tutor_id=tutor_id, sessao_id=sessao_id, papel="usuario", conteudo=msg_usuario))
    session.add(Mensagem(tutor_id=tutor_id, sessao_id=sessao_id, papel="assistente", conteudo=msg_assistente))
    session.commit()


async def processar_chat(tutor_id: int, dados: ChatInput, session: Session) -> ChatOutput:
    tutor = session.get(Tutor, tutor_id)
    if not tutor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor não encontrado")
    if not tutor.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tutor inativo")

    historico = _buscar_historico(tutor_id, dados.sessao_id, session)

    logger.info(f"Chat tutor_id={tutor_id} sessao={dados.sessao_id} histórico={len(historico)} msgs")

    resposta = await tutor_agent.responder(
        instrucoes=tutor.instrucoes,
        fontes=tutor.fontes,
        historico=historico,
        mensagem_usuario=dados.mensagem,
    )

    _salvar_turno(tutor_id, dados.sessao_id, dados.mensagem, resposta, session)

    return ChatOutput(sessao_id=dados.sessao_id, resposta=resposta)
