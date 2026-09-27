def detect_tampered_evidence(action_manifest):
    """
    Detects when the evidence inside an ActionManifest
    contradicts the ground-truth values.
    """

    arguments = action_manifest.get("arguments", {})
    evidence = action_manifest.get("evidence", {})

    violations = []

    # Ground-truth balance from mock data
    ground_truth_balance = 10000

    # Evidence must match the real balance
    if "balance" in evidence:
        if evidence["balance"] != ground_truth_balance:
            violations.append("EVIDENCE_BALANCE_MISMATCH")

    # If arguments contain balance, it must also agree with evidence
    if "balance" in arguments and "balance" in evidence:
        if arguments["balance"] != evidence["balance"]:
            violations.append("EVIDENCE_BALANCE_MISMATCH")

    # Compare customer ID
    if "customer_id" in arguments and "customer_id" in evidence:
        if arguments["customer_id"] != evidence["customer_id"]:
            violations.append("EVIDENCE_CUSTOMER_MISMATCH")

    # Compare order status
    if "order_status" in arguments and "order_status" in evidence:
        if arguments["order_status"] != evidence["order_status"]:
            violations.append("EVIDENCE_STATUS_MISMATCH")

    if violations:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": violations
        }

    return {
        "decision": "ALLOW",
        "risk": "LOW",
        "violations": []
    }
      


if __name__ == "__main__":

    # Test attack: evidence claims balance is 15000
    # while the actual/expected balance is 10000.
    tampered_action = {
        "arguments": {
            "customer_id": "C101",
            "balance": 15000,
            "order_status": "DELIVERED"
        },
        "evidence": {
            "customer_id": "C101",
            "balance": 10000,
            "order_status": "DELIVERED"
        }
    }

    verdict = detect_tampered_evidence(tampered_action)

    print("=== TAMPERED EVIDENCE ATTACK ===")
    print("SAARTHI VERDICT:")
    print(verdict)