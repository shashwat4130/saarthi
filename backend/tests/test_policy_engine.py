from app.models.manifest import ActionManifest
from app.models.policy import PolicyDecisionTarget
from app.services.policy_engine import PolicyEngine


def make_manifest(
    amount: float,
    account_status: str = "ACTIVE",
) -> ActionManifest:
    return ActionManifest(
        action_id="ACT-001",
        agent_id="agent-demo",
        action="refund",
        arguments={
            "customer_id": "C101",
            "amount": amount,
            "account_status": account_status,
        },
        evidence={},
        intent_summary="Process a refund",
    )


def test_small_refund_does_not_trigger_policy():
    engine = PolicyEngine()

    manifest = make_manifest(5000)

    result = engine.evaluate(manifest)

    assert result.passed is True
    assert result.triggered_rules == []
    assert result.recommended_decision is None


def test_large_refund_triggers_human_review():
    engine = PolicyEngine()

    manifest = make_manifest(15000)

    result = engine.evaluate(manifest)

    assert result.passed is False
    assert len(result.triggered_rules) >= 1
    assert result.recommended_decision == PolicyDecisionTarget.HUMAN_REVIEW


def test_extremely_large_transaction_is_blocked():
    engine = PolicyEngine()

    manifest = make_manifest(60000)

    result = engine.evaluate(manifest)

    assert result.passed is False
    assert len(result.triggered_rules) >= 1
    assert result.recommended_decision == PolicyDecisionTarget.BLOCK


def test_suspended_account_triggers_review():
    engine = PolicyEngine()

    manifest = make_manifest(
        amount=5000,
        account_status="SUSPENDED",
    )

    result = engine.evaluate(manifest)

    assert result.passed is False
    assert len(result.triggered_rules) >= 1
    assert result.recommended_decision == PolicyDecisionTarget.HUMAN_REVIEW