from sqlmodel import Session, select
from app.models.tutor import Tutor, TutorCreate, TutorUpdate
from fastapi import HTTPException, status


def listar_tutores(session: Session) -> list[Tutor]:
    return session.exec(select(Tutor)).all()


def buscar_tutor(tutor_id: int, session: Session) -> Tutor:
    tutor = session.get(Tutor, tutor_id)
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor não encontrado"
        )
    return tutor


def criar_tutor(dados: TutorCreate, session: Session) -> Tutor:
    tutor = Tutor(**dados.model_dump())
    session.add(tutor)
    session.commit()
    session.refresh(tutor)
    return tutor


def atualizar_tutor(tutor_id: int, dados: TutorUpdate, session: Session) -> Tutor:
    tutor = buscar_tutor(tutor_id, session)
    alteracoes = dados.model_dump(exclude_unset=True)
    for campo, valor in alteracoes.items():
        setattr(tutor, campo, valor)
    session.add(tutor)
    session.commit()
    session.refresh(tutor)
    return tutor


def desativar_tutor(tutor_id: int, session: Session) -> Tutor:
    tutor = buscar_tutor(tutor_id, session)
    tutor.ativo = False
    session.add(tutor)
    session.commit()
    session.refresh(tutor)
    return tutor
