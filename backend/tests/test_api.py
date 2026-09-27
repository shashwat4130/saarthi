from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "SAARTHI API"


def test_governance_intercept_endpoint():
    payload = {
        "action_id": "api-test-001",
        "agent_id": "demo-agent",
        "action": "READ_ACCOUNT",
        "arguments": {
            "customer_id": "C101"
        },
        "evidence": {
            "customer_id": "C101"
        },
        "intent_summary": "Read customer account information",
    }

    response = client.post(
        "/v1/governance/intercept",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action_id"] == "api-test-001"
    assert data["agent_id"] == "demo-agent"
    assert data["action"] == "READ_ACCOUNT"

    assert data["decision"]
    assert data["reason"]

    assert data["verification"]
    assert data["policy"]
    assert data["risk"]

    assert data["audit_event_id"]
    assert data["audit_event_id"] != "PENDING_AUDIT"

    print("\n=== API GOVERNANCE RESULT ===")
    print("Decision:", data["decision"])
    print("Reason:", data["reason"])
    print("Audit Event:", data["audit_event_id"])


def test_audit_endpoint():
    response = client.get("/v1/audit")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_audit_verify_endpoint():
    response = client.get("/v1/audit/verify")

    assert response.status_code == 200

    data = response.json()

    assert "valid" in data
    assert "events_checked" in data


# ==============================================================
# DEMO SCENARIOS
# ==============================================================


def test_demo_valid_action():
    response = client.post(
        "/v1/demo/run/valid_action"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scenario"] == "valid_action"
    assert data["action"]["action_id"] == "demo-valid-001"

    assert "verdict" in data
    assert data["verdict"]["decision"]

    print("\n=== VALID ACTION ===")
    print("Decision:", data["verdict"]["decision"])
    print("Reason:", data["verdict"]["reason"])


def test_demo_hallucinated_claim():
    response = client.post(
        "/v1/demo/run/hallucinated_claim"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scenario"] == "hallucinated_claim"

    assert "verdict" in data
    assert data["verdict"]["decision"]

    print("\n=== HALLUCINATED CLAIM ===")
    print("Decision:", data["verdict"]["decision"])
    print("Reason:", data["verdict"]["reason"])


def test_demo_risky_refund():
    response = client.post(
        "/v1/demo/run/risky_refund"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scenario"] == "risky_refund"

    assert "verdict" in data
    assert data["verdict"]["decision"]

    print("\n=== RISKY REFUND ===")
    print("Decision:", data["verdict"]["decision"])
    print("Reason:", data["verdict"]["reason"])


def test_demo_critical_block():
    response = client.post(
        "/v1/demo/run/critical_block"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scenario"] == "critical_block"

    assert "verdict" in data
    assert data["verdict"]["decision"]

    print("\n=== CRITICAL BLOCK ===")
    print("Decision:", data["verdict"]["decision"])
    print("Reason:", data["verdict"]["reason"])