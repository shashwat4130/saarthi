from agent.agents.refund_agent import create_valid_refund
from agent.tools.mock_tools import get_customer


def validate_over_threshold_refund(action):
    """
    Detect whether the requested refund exceeds
    the customer's eligible refund amount.
    """

    arguments = action["arguments"]

    customer_id = arguments["customer_id"]
    requested_amount = arguments["amount"]

    customer = get_customer(customer_id)

    if customer is None:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": ["CUSTOMER_NOT_FOUND"]
        }

    eligible_refund = customer["eligible_refund"]

    violations = []

    if requested_amount > eligible_refund:
        violations.append("REFUND_EXCEEDS_ELIGIBILITY")

    if violations:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": violations,
            "eligible_refund": eligible_refund,
            "requested_amount": requested_amount
        }

    return {
        "decision": "ALLOW",
        "risk": "LOW",
        "violations": []
    }


if __name__ == "__main__":

    action = create_valid_refund()

    # Simulate an agent requesting too much money.
    action["arguments"]["amount"] = 15000

    print("=== OVER-THRESHOLD REFUND SCENARIO ===")

    print("\nAgent ActionManifest:")
    print(action)

    verdict = validate_over_threshold_refund(action)

    print("\nSAARTHI VERDICT:")
    print(verdict)