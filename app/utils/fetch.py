import logging
import requests
from fastapi import HTTPException
from app.config import GENIEACS_URL

logger = logging.getLogger(__name__)

def fetch_from_genieacs(endpoint: str):
    """Função utilitária para buscar dados no GenieACS."""
    url = f"{GENIEACS_URL}{endpoint}"
    logger.info(f"GET {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout ao acessar GenieACS.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar GenieACS: {str(e)}")

def post_to_genieacs(endpoint: str, data: dict = None):
    """Função utilitária para enviar requisições POST ao GenieACS."""
    url = f"{GENIEACS_URL}{endpoint}"
    logger.info(f"POST {url} com dados {data}")
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar dados ao GenieACS: {str(e)}")

def delete_from_genieacs(endpoint: str):
    """Função utilitária para enviar requisições DELETE ao GenieACS."""
    url = f"{GENIEACS_URL}{endpoint}"
    logger.info(f"DELETE {url}")
    try:
        response = requests.delete(url)
        response.raise_for_status()
        return {"detail": "Recurso deletado com sucesso"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar recurso no GenieACS: {str(e)}")
