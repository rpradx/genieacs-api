import logging
from fastapi import FastAPI
from app.routes import devices, tasks
from app.config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

app = FastAPI(
    title="GenieACS Wrapper API",
    description="API para interação com GenieACS",
    version="1.0.0"
)

# Incluir as rotas
app.include_router(devices.router)
app.include_router(tasks.router)
