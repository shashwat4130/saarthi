from agent.agents.refund_agent import create_valid_refund
from agent.tools.mock_tools import get_customer


def validate_hallucinated_balance(action):
    """
    Detect whether the agent's claimed balance
    matches the ground-truth balance.
    """

    customer_id = action["arguments"]["customer_id"]

    customer = get_customer(customer_id)

    if customer is None:
        return {
            "decision": "REJECT",
            "risk": "HIGH",
            "violations": ["CUSTOMER_NOT_FOUND"]
        }

    ground_truth_balance = customer["balance"]

    # Simulated hallucination by the agent.
    agent_claimed_balance = 15000

    violations = []

    if agent_claimed_balance != ground_truth_balance:
        violations.append("BALANCE_CONTRADICTION")

    if violations:
        return {
            "decision": "RETRY",
            "risk": "MEDIUM",
            "violations": violations,
            "ground_truth_balance": ground_truth_balance,
            "agent_claimed_balance": agent_claimed_balance
        }

    return {
        "decision": "ALLOW",
        "risk": "LOW",
        "violations": []
    }


if __name__ == "__main__":

    action = create_valid_refund()

    print("=== HALLUCINATED BALANCE SCENARIO ===")

    print("\nAgent ActionManifest:")
    print(action)

    verdict = validate_hallucinated_balance(action)

    print("\nSAARTHI VERDICT:")
    print(verdict)