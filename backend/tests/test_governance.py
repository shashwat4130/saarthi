from app.models.manifest import ActionManifest
from app.services.governance import GovernanceService


def test_governance_pipeline_valid_action():
    manifest = ActionManifest(
        action_id="test-valid-001",
        agent_id="demo-agent",
        action="READ_ACCOUNT",
        arguments={
            "customer_id": "C101"
        },
        evidence={
            "customer_id": "C101"
        },
        intent_summary="Read customer account information",
    )

    service = GovernanceService()

    verdict = service.evaluate(manifest)

    # ---------------------------------------------------------
    # Basic verdict checks
    # ---------------------------------------------------------
    assert verdict.action_id == "test-valid-001"
    assert verdict.agent_id == "demo-agent"
    assert verdict.action == "READ_ACCOUNT"

    # ---------------------------------------------------------
    # Pipeline stage checks
    # ---------------------------------------------------------
    assert verdict.verification is not None
    assert verdict.policy is not None
    assert verdict.risk is not None

    # ---------------------------------------------------------
    # Final decision checks
    # ---------------------------------------------------------
    assert verdict.decision is not None
    assert verdict.reason

    # ---------------------------------------------------------
    # Audit checks
    # ---------------------------------------------------------
    assert verdict.audit_event_id
    assert verdict.audit_event_id != "PENDING_AUDIT"

    assert verdict.timestamp

    # ---------------------------------------------------------
    # Display result
    # ---------------------------------------------------------
    print("\n=== SAARTHI GOVERNANCE RESULT ===")
    print("Decision:", verdict.decision)
    print("Reason:", verdict.reason)
    print("Risk:", verdict.risk.model_dump())
    print("Verification:", verdict.verification.status)
    print("Policy:", verdict.policy.model_dump())
    print("Audit Event ID:", verdict.audit_event_id)
    print("Timestamp:", verdict.timestamp)