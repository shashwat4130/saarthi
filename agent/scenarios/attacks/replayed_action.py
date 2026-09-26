def detect_replayed_action(action_manifest, seen_actions):
    """
    Detects whether the same action_id has already been processed.
    """

    action_id = action_manifest.get("action_id")

    if not action_id:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": ["MISSING_ACTION_ID"]
        }

    if action_id in seen_actions:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": ["REPLAYED_ACTION"]
        }

    seen_actions.add(action_id)

    return {
        "decision": "ALLOW",
        "risk": "LOW",
        "violations": []
    }


if __name__ == "__main__":

    seen_actions = set()

    action = {
        "action_id": "ACTION-REPLAY-001",
        "agent_id": "refund-agent-01",
        "action": "issue_refund",
        "arguments": {
            "customer_id": "C101",
            "order_id": "O1001",
            "amount": 3000
        }
    }

    # First submission
    first_verdict = detect_replayed_action(
        action,
        seen_actions
    )

    # Same action submitted again
    second_verdict = detect_replayed_action(
        action,
        seen_actions
    )

    print("=== REPLAYED ACTION ATTACK ===")

    print("\nFirst submission:")
    print(first_verdict)

    print("\nSecond submission:")
    print(second_verdict)