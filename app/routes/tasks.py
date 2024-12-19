from fastapi import APIRouter
from urllib.parse import quote
from app.utils.fetch import post_to_genieacs

router = APIRouter(tags=["Tarefas"])

@router.post("/devices/{device_id}/tasks", summary="Adicionar tarefa a um dispositivo")
def add_task_to_device(device_id: str, task: dict):
    """
    Enfileira uma tarefa para um dispositivo específico.
    """
    encoded_id = quote(device_id)
    endpoint = f"/devices/{encoded_id}/tasks"
    result = post_to_genieacs(endpoint, task)
    return {"result": result}
