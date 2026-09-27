from app.models.manifest import ActionManifest
from app.models.policy import (
    PolicyDecisionTarget,
    PolicyResult,
)
from app.models.risk import RiskReport
from app.models.verification import (
    VerificationReport,
    VerificationStatus,
)
from app.services.decision_gate import DecisionGate
from app.models.verdict import DecisionEnum


def make_manifest() -> ActionManifest:
    return ActionManifest(
        action_id="ACT-001",
        agent_id="agent-demo",
        action="refund",
        arguments={
            "customer_id": "C101",
            "amount": 1000,
        },
        evidence={},
        intent_summary="Process refund",
    )


def make_verification(
    status: VerificationStatus,
) -> VerificationReport:
    return VerificationReport(
        verified=status == VerificationStatus.MATCH,
        status=status,
        checked_fields=[],
        discrepancies=[],
        execution_time_ms=1.0,
    )


def make_policy(
    recommended_decision=None,
) -> PolicyResult:
    return PolicyResult(
        passed=recommended_decision is None,
        triggered_rules=[],
        recommended_decision=recommended_decision,
    )


def make_risk(score: float) -> RiskReport:
    return RiskReport(
        total_score=score,
        risk_level=(
            "LOW"
            if score < 30
            else "MEDIUM"
            if score < 60
            else "HIGH"
        ),
        factors={},
    )


def test_valid_low_risk_action_is_allowed():
    gate = DecisionGate()

    result = gate.decide(
        manifest=make_manifest(),
        verification=make_verification(
            VerificationStatus.MATCH
        ),
        policy=make_policy(),
        risk=make_risk(20),
    )

    assert result.decision == DecisionEnum.ALLOW
    assert result.action_id == "ACT-001"
    assert result.agent_id == "agent-demo"
    assert result.audit_event_id
    assert result.timestamp


def test_verification_mismatch_causes_retry():
    gate = DecisionGate()

    result = gate.decide(
        manifest=make_manifest(),
        verification=make_verification(
            VerificationStatus.MISMATCH
        ),
        policy=make_policy(),
        risk=make_risk(40),
    )

    assert result.decision == DecisionEnum.RETRY
    assert "disagrees" in result.reason


def test_blocking_policy_causes_block():
    gate = DecisionGate()

    result = gate.decide(
        manifest=make_manifest(),
        verification=make_verification(
            VerificationStatus.MATCH
        ),
        policy=make_policy(
            PolicyDecisionTarget.BLOCK
        ),
        risk=make_risk(20),
    )

    assert result.decision == DecisionEnum.BLOCK


def test_high_risk_causes_human_review():
    gate = DecisionGate()

    result = gate.decide(
        manifest=make_manifest(),
        verification=make_verification(
            VerificationStatus.MATCH
        ),
        policy=make_policy(),
        risk=make_risk(60),
    )

    assert result.decision == DecisionEnum.HUMAN_REVIEW


def test_policy_review_beats_allow():
    gate = DecisionGate()

    result = gate.decide(
        manifest=make_manifest(),
        verification=make_verification(
            VerificationStatus.MATCH
        ),
        policy=make_policy(
            PolicyDecisionTarget.HUMAN_REVIEW
        ),
        risk=make_risk(20),
    )

    assert result.decision == DecisionEnum.HUMAN_REVIEW