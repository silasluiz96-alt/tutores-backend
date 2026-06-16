import httpx
import logging
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)


def _criar_agente(instrucoes_sistema: str) -> Agent:
    model = OpenAIModel(
        os.getenv("LLM_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("LLM_API_KEY"),
    )
    return Agent(model=model, system_prompt=instrucoes_sistema)


async def buscar_conteudo_fonte(url: str) -> str:
    """Faz fetch simples de uma URL e retorna o texto (primeiros 3000 caracteres)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resposta = await client.get(url)
            resposta.raise_for_status()
            return resposta.text[:3000]
    except Exception as e:
        logger.warning(f"Não foi possível buscar a fonte {url}: {e}")
        return ""


async def compilar_contexto_fontes(fontes: str | None) -> str:
    """Busca todas as URLs das fontes e compila o conteúdo em um bloco de texto."""
    if not fontes:
        return ""

    urls = [url.strip() for url in fontes.split(",") if url.strip()]
    blocos = []

    for url in urls:
        conteudo = await buscar_conteudo_fonte(url)
        if conteudo:
            blocos.append(f"--- Fonte: {url} ---\n{conteudo}")

    return "\n\n".join(blocos)


async def responder(
    instrucoes: str,
    fontes: str | None,
    historico: list[dict],
    mensagem_usuario: str,
) -> str:
    """
    Orquestra o agente: compila contexto das fontes, monta o prompt
    com histórico e retorna a resposta do tutor.
    """
    contexto_fontes = await compilar_contexto_fontes(fontes)

    system_prompt = instrucoes
    if contexto_fontes:
        system_prompt += f"\n\nUse as informações abaixo como base de conhecimento:\n\n{contexto_fontes}"

    agente = _criar_agente(system_prompt)

    # Monta o histórico como texto para incluir no prompt
    historico_texto = ""
    for msg in historico[-10:]:  # Últimas 10 mensagens para não estourar o contexto
        papel = "Usuário" if msg["papel"] == "usuario" else "Tutor"
        historico_texto += f"{papel}: {msg['conteudo']}\n"

    prompt_final = mensagem_usuario
    if historico_texto:
        prompt_final = f"Histórico da conversa:\n{historico_texto}\nUsuário: {mensagem_usuario}"

    try:
        resultado = await agente.run(prompt_final)
        return resultado.output
    except Exception as e:
        logger.error(f"Erro ao chamar o agente: {e}")
        raise
