from agent.agents.refund_agent import create_valid_refund
from agent.tools.mock_tools import get_customer, get_order


def validate_action(action):
    """
    Validate the refund action against ground truth.
    """

    arguments = action["arguments"]

    customer_id = arguments["customer_id"]
    order_id = arguments["order_id"]
    amount = arguments["amount"]

    customer = get_customer(customer_id)
    order = get_order(order_id)

    violations = []

    if customer is None:
        violations.append("CUSTOMER_NOT_FOUND")

    if order is None:
        violations.append("ORDER_NOT_FOUND")

    if customer and order:

        if order["customer_id"] != customer_id:
            violations.append("CUSTOMER_ORDER_MISMATCH")

        if amount > customer["eligible_refund"]:
            violations.append("REFUND_EXCEEDS_ELIGIBILITY")

        if order["order_status"] != "DELIVERED":
            violations.append("ORDER_NOT_ELIGIBLE")

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

    action = create_valid_refund()

    print("=== VALID ACTION SCENARIO ===")
    print("\nActionManifest:")
    print(action)

    verdict = validate_action(action)

    print("\nSAARTHI VERDICT:")
    print(verdict)