from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db_connection


client = TestClient(app)


def test_health_check_returns_200():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "SAARTHI API"
    assert data["version"] == "0.1.0"
    assert data["database"] == "connected"


def test_seed_account_exists():
    conn = get_db_connection()

    try:
        row = conn.execute(
            "SELECT customer_id, name, balance "
            "FROM mock_accounts "
            "WHERE customer_id = ?",
            ("C101",),
        ).fetchone()

        assert row is not None
        assert row["customer_id"] == "C101"
        assert row["name"] == "Aarav"
        assert row["balance"] == 15400.0

    finally:
        conn.close()


def test_action_manifest_validation():
    from app.models.manifest import ActionManifest

    manifest = ActionManifest(
        action_id="ACT-001",
        agent_id="agent-demo",
        action="refund",
        arguments={
            "customer_id": "C101",
            "amount": 4999,
        },
        evidence={
            "customer_id": "C101",
            "balance": 15400,
        },
        intent_summary="Process a customer refund",
    )

    assert manifest.action_id == "ACT-001"
    assert manifest.agent_id == "agent-demo"
    assert manifest.action == "refund"
    assert manifest.arguments["customer_id"] == "C101"
    assert manifest.arguments["amount"] == 4999