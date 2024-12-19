from fastapi import APIRouter, HTTPException
from urllib.parse import quote
import json
from app.utils.fetch import fetch_from_genieacs, delete_from_genieacs
from app.services.genieacs import genieacs

router = APIRouter(tags=["Dispositivos"])

@router.get("/devices", summary="Listar dispositivos")
def list_devices(query: str = None):
    """
    Lista dispositivos registrados no GenieACS com base em uma query opcional.
    """
    query_param = f"?query={quote(query)}" if query else ""
    devices = fetch_from_genieacs(f"/devices/{query_param}")
    return {"devices": devices}

@router.get("/devices/{device_id}", summary="Detalhes de um dispositivo")
def get_device(device_id: str):
    """
    Obtém detalhes de um dispositivo específico no GenieACS.
    """
    query = {"_id": device_id}
    query_param = f"?query={quote(json.dumps(query))}"
    devices = fetch_from_genieacs(f"/devices/{query_param}")
    if not devices:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")
    return {"device": devices[0]}

@router.get("/devices/{device_id}/all_parameters", summary="Obter todos os parâmetros traduzidos")
def get_all_parameters(device_id: str):
    """
    Retorna todos os parâmetros traduzidos de um dispositivo.
    """
    device_data = genieacs.get_device_by_id(device_id)
    if not device_data:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")
    parameters = genieacs.extract_mapped_parameters(device_data)
    return {"device_id": device_id, "parameters": parameters}

@router.delete("/devices/{device_id}", summary="Deletar um dispositivo")
def delete_device(device_id: str):
    """
    Remove um dispositivo específico do banco de dados do GenieACS.
    """
    query = {"_id": device_id}
    query_param = f"?query={quote(json.dumps(query))}"
    devices = fetch_from_genieacs(f"/devices/{query_param}")
    if not devices:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")
    device = devices[0]
    encoded_id = quote(device["_id"])
    result = delete_from_genieacs(f"/devices/{encoded_id}")
    return result
