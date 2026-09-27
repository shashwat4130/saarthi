from datetime import datetime
import uuid


def create_refund_action(
    customer_id,
    order_id,
    amount,
    evidence,
    agent_id="refund-agent-01"
):
    """
    Create an ActionManifest for a refund action.
    """

    return {
        "action_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "action": "issue_refund",
        "arguments": {
            "customer_id": customer_id,
            "order_id": order_id,
            "amount": amount
        },
        "evidence": evidence,
        "timestamp": datetime.now().isoformat()
    }


def create_valid_refund():
    """
    Scenario: Agent proposes a valid refund.
    """

    return create_refund_action(
        customer_id="C101",
        order_id="O1001",
        amount=3000,
        evidence={
            "customer_id": "C101",
            "balance": 10000,
            "eligible_refund": 10000,
            "order_status": "DELIVERED"
        }
    )


if __name__ == "__main__":

    action = create_valid_refund()

    print("=== REFUND AGENT ===")
    print("Generated ActionManifest:")
    print(action)