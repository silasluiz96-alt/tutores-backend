from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.auth import verificar_api_key
from app.models.tutor import Tutor, TutorCreate, TutorUpdate
from app.services import tutor as servico

router = APIRouter(prefix="/tutores", tags=["Tutores"])


@router.get("/", response_model=list[Tutor])
def listar(
    session: Session = Depends(get_session),
    _: None = Depends(verificar_api_key)
):
    return servico.listar_tutores(session)


@router.get("/{tutor_id}", response_model=Tutor)
def buscar(
    tutor_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(verificar_api_key)
):
    return servico.buscar_tutor(tutor_id, session)


@router.post("/", response_model=Tutor, status_code=201)
def criar(
    dados: TutorCreate,
    session: Session = Depends(get_session),
    _: None = Depends(verificar_api_key)
):
    return servico.criar_tutor(dados, session)


@router.patch("/{tutor_id}", response_model=Tutor)
def atualizar(
    tutor_id: int,
    dados: TutorUpdate,
    session: Session = Depends(get_session),
    _: None = Depends(verificar_api_key)
):
    return servico.atualizar_tutor(tutor_id, dados, session)


@router.delete("/{tutor_id}", response_model=Tutor)
def desativar(
    tutor_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(verificar_api_key)
):
    return servico.desativar_tutor(tutor_id, session)
