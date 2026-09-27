from fastapi import APIRouter

from app.models.manifest import ActionManifest
from app.models.verdict import GovernanceVerdict
from app.services.governance import GovernanceService


router = APIRouter(
    prefix="/v1/governance",
    tags=["Governance"],
)


@router.post(
    "/intercept",
    response_model=GovernanceVerdict,
    summary="Intercept and govern an AI action",
)
def intercept_action(manifest: ActionManifest) -> GovernanceVerdict:
    """
    Main SAARTHI runtime interception endpoint.

    Receives an AI agent's proposed action and sends it through:

        Verification
            ↓
        Policy
            ↓
        Risk
            ↓
        Decision Gate
            ↓
        Audit Ledger
    """

    service = GovernanceService()

    verdict = service.evaluate(manifest)

    return verdict