from app.models.manifest import ActionManifest
from app.models.verification import VerificationStatus
from app.services.verifier import GroundTruthVerifier


def make_manifest(
    balance: float = 10000,
    eligible_refund: float = 10000,
    amount: float = 3000,
    order_status: str = "DELIVERED",
) -> ActionManifest:
    return ActionManifest(
        action_id="ACT-VERIFIER-001",
        agent_id="refund-agent-01",
        action="issue_refund",
        arguments={
            "customer_id": "C101",
            "order_id": "O1001",
            "amount": amount,
        },
        evidence={
            "customer_id": "C101",
            "balance": balance,
            "eligible_refund": eligible_refund,
            "order_status": order_status,
        },
        intent_summary="Process a customer refund",
    )


def test_valid_refund_matches_ground_truth():
    verifier = GroundTruthVerifier()

    result = verifier.verify(
        make_manifest()
    )

    assert result.verified is True
    assert result.status == VerificationStatus.MATCH
    assert result.discrepancies == []


def test_hallucinated_balance_is_detected():
    verifier = GroundTruthVerifier()

    result = verifier.verify(
        make_manifest(
            balance=15000,
        )
    )

    assert result.verified is False
    assert result.status == VerificationStatus.MISMATCH
    assert len(result.discrepancies) >= 1

    balance_discrepancy = next(
        item
        for item in result.discrepancies
        if item.field == "evidence.balance"
    )

    assert balance_discrepancy.agent_value == 15000
    assert balance_discrepancy.trusted_value == 10000


def test_over_eligible_refund_is_detected():
    verifier = GroundTruthVerifier()

    result = verifier.verify(
        make_manifest(
            amount=15000,
        )
    )

    assert result.verified is False
    assert result.status == VerificationStatus.MISMATCH

    amount_discrepancy = next(
        item
        for item in result.discrepancies
        if item.field == "arguments.amount"
    )

    assert amount_discrepancy.agent_value == 15000
    assert amount_discrepancy.trusted_value == 10000


def test_missing_evidence_is_detected():
    verifier = GroundTruthVerifier()

    manifest = make_manifest()

    manifest.evidence = {
        "customer_id": "C101",
    }

    result = verifier.verify(manifest)

    assert result.verified is False
    assert result.status == VerificationStatus.MISSING_EVIDENCE
    assert len(result.discrepancies) >= 1


def test_wrong_order_status_is_detected():
    verifier = GroundTruthVerifier()

    result = verifier.verify(
        make_manifest(
            order_status="CANCELLED",
        )
    )

    assert result.verified is False
    assert result.status == VerificationStatus.MISMATCH