from app.audit.ledger import AuditLedger


def test_audit_ledger_append_and_verify(tmp_path):
    database_path = tmp_path / "audit_test.db"

    ledger = AuditLedger(
        database_path=str(database_path),
        secret="test-secret",
    )

    first = ledger.append(
        action_id="audit-test-001",
        agent_id="demo-agent",
        action="READ_ACCOUNT",
        decision="ALLOW",
        reason="Action verified successfully.",
        risk_score=10.0,
        payload={
            "customer_id": "C101",
            "amount": 0,
        },
    )

    second = ledger.append(
        action_id="audit-test-002",
        agent_id="demo-agent",
        action="REFUND",
        decision="HUMAN_REVIEW",
        reason="Refund requires human approval.",
        risk_score=65.0,
        payload={
            "customer_id": "C101",
            "amount": 5000,
        },
    )

    # Basic event checks
    assert first.event_id
    assert second.event_id

    assert first.current_hash
    assert second.current_hash

    # Second event must point to first event
    assert second.previous_hash == first.current_hash

    # Verify complete chain
    result = ledger.verify_chain()

    assert result["valid"] is True
    assert result["events_checked"] == 2

    print("\n=== SAARTHI AUDIT LEDGER ===")
    print("First Event:", first.event_id)
    print("First Hash:", first.current_hash)

    print("Second Event:", second.event_id)
    print("Second Previous Hash:", second.previous_hash)
    print("Second Hash:", second.current_hash)

    print("Chain:", result)


def test_audit_ledger_empty_chain(tmp_path):
    database_path = tmp_path / "empty_audit.db"

    ledger = AuditLedger(
        database_path=str(database_path),
        secret="test-secret",
    )

    result = ledger.verify_chain()

    assert result["valid"] is True
    assert result["events_checked"] == 0