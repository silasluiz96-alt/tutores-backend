from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.database import criar_tabelas
from app.models import tutor, mensagem  # noqa: F401 — garante registro das tabelas
from app.api import tutors, chat
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    logger.info("Tabelas criadas. Servidor pronto.")
    yield


app = FastAPI(
    title="Plataforma de Tutores Personalizados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def erro_generico(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor"})


app.include_router(tutors.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
