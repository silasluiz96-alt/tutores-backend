from fastapi import Header, HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv()


def verificar_api_key(x_api_key: str = Header(...)):
    chave = os.getenv("ADMIN_API_KEY", "")
    if not chave:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_API_KEY não configurada no servidor"
        )
    if x_api_key != chave:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
