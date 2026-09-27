from fastapi import APIRouter
from pydantic import BaseModel

from app.db import get_db_connection

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    database_status = "error"

    try:
        conn = get_db_connection()
        try:
            conn.execute("SELECT 1").fetchone()
            database_status = "connected"
        finally:
            conn.close()
    except Exception:
        database_status = "error"

    return HealthResponse(
        status="ok",
        service="SAARTHI API",
        version="0.1.0",
        database=database_status,
    )