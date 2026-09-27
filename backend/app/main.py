from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.db import init_db

from app.routes.health import router as health_router
from app.routes.governance import router as governance_router
from app.routes.audit import router as audit_router
from app.routes.demo import router as demo_router


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    init_db()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description=(
        "SAARTHI Runtime Governance API - "
        "verification, policy, risk and audit control "
        "for autonomous agent actions."
    ),
    lifespan=lifespan,
)


# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

app.include_router(health_router)
app.include_router(governance_router)
app.include_router(audit_router)
app.include_router(demo_router)