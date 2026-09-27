from fastapi import APIRouter, Query

from app.audit.ledger import AuditLedger
from app.models.verdict import AuditRecord


router = APIRouter(
    prefix="/v1/audit",
    tags=["Audit"],
)


@router.get(
    "",
    response_model=list[AuditRecord],
    summary="Get recent audit events",
)
def get_audit_events(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    )
) -> list[AuditRecord]:
    """
    Return the most recent SAARTHI audit events.
    """

    ledger = AuditLedger()

    return ledger.get_recent(limit=limit)


@router.get(
    "/verify",
    summary="Verify audit chain",
)
def verify_audit_chain() -> dict:
    """
    Verify the cryptographic audit chain.
    """

    ledger = AuditLedger()

    return ledger.verify_chain()