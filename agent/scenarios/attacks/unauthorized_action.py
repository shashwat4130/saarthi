def detect_unauthorized_action(action_manifest, allowed_actions):
    """
    Detects whether an agent is attempting an action
    that is not present in its allowed action list.
    """

    action = action_manifest.get("action")

    if not action:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": ["MISSING_ACTION"]
        }

    if action not in allowed_actions:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": ["UNAUTHORIZED_ACTION"]
        }

    return {
        "decision": "ALLOW",
        "risk": "LOW",
        "violations": []
    }


if __name__ == "__main__":

    allowed_actions = {
        "issue_refund",
        "check_balance"
    }

    unauthorized_manifest = {
        "action_id": "ACTION-UNAUTHORIZED-001",
        "agent_id": "refund-agent-01",
        "action": "delete_customer",
        "arguments": {
            "customer_id": "C101"
        }
    }

    verdict = detect_unauthorized_action(
        unauthorized_manifest,
        allowed_actions
    )

    print("=== UNAUTHORIZED ACTION ATTACK ===")

    print("\nRequested action:")
    print(unauthorized_manifest["action"])

    print("\nAllowed actions:")
    print(allowed_actions)

    print("\nSAARTHI VERDICT:")
    print(verdict)