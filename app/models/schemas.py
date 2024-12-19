from pydantic import BaseModel
from typing import Dict, Any

class Task(BaseModel):
    name: str
    args: Dict[str, Any]
