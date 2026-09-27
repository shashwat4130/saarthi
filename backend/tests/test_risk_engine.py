from app.models.manifest import ActionManifest
from app.models.policy import (
    PolicyDecisionTarget,
    PolicyResult,
    TriggeredPolicy,
    PolicyOperator,
)
from app.models.verification import (
    VerificationReport,
    VerificationStatus,
)
from app.services.risk_engine import RiskEngine


def make_manifest(
    amount: float = 1000,
    action: str = "refund",
) -> ActionManifest:
    return ActionManifest(
        action_id="ACT-001",
        agent_id="agent-demo",
        action=action,
        arguments={
            "customer_id": "C101",
            "amount": amount,
        },
        evidence={},
        intent_summary="Demo action",
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
    triggered_rules=None,
) -> PolicyResult:
    return PolicyResult(
        passed=not triggered_rules,
        triggered_rules=triggered_rules or [],
        recommended_decision=None,
    )


def test_low_risk_valid_read_action():
    engine = RiskEngine()

    manifest = make_manifest(
        amount=0,
        action="read",
    )

    verification = make_verification(
        VerificationStatus.MATCH
    )

    policy = make_policy()

    result = engine.evaluate(
        manifest,
        verification,
        policy,
    )

    assert result.total_score < 30
    assert result.risk_level == "LOW"
    assert result.factors["discrepancy"].score == 0


def test_large_financial_action_has_higher_risk():
    engine = RiskEngine()

    manifest = make_manifest(
        amount=50000,
        action="refund",
    )

    verification = make_verification(
        VerificationStatus.MATCH
    )

    policy = make_policy()

    result = engine.evaluate(
        manifest,
        verification,
        policy,
    )

    assert result.total_score > 40
    assert result.factors["financial"].score == 10.0
    assert result.factors["reversibility"].score == 8.0


def test_verification_mismatch_creates_high_risk():
    engine = RiskEngine()

    manifest = make_manifest(
        amount=5000,
        action="refund",
    )

    verification = make_verification(
        VerificationStatus.MISMATCH
    )

    policy = make_policy()

    result = engine.evaluate(
        manifest,
        verification,
        policy,
    )

    assert result.factors["discrepancy"].score == 10.0

    # 5,000 refund + irreversible-action factor +
    # verification mismatch produces 58.5 with the
    # defined deterministic weighting.
    assert result.total_score == 58.5
    assert result.risk_level == "MEDIUM"


def test_policy_severity_increases_risk():
    engine = RiskEngine()

    manifest = make_manifest(
        amount=5000,
        action="refund",
    )

    verification = make_verification(
        VerificationStatus.MATCH
    )

    triggered_rule = TriggeredPolicy(
        rule_id="TEST_POLICY",
        field="arguments.amount",
        actual_value=5000,
        expected_value=1000,
        operator=PolicyOperator.GREATER_THAN,
        severity=9,
        target_decision=PolicyDecisionTarget.HUMAN_REVIEW,
        explanation="Test policy violation",
    )

    policy = make_policy(
        triggered_rules=[triggered_rule]
    )

    result = engine.evaluate(
        manifest,
        verification,
        policy,
    )

    assert result.factors["policy"].score == 9.0
    assert result.total_score > 0