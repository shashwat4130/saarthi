
import importlib.util
import copy

from agent.agents.refund_agent import create_valid_refund
from agent.tools.mock_tools import get_account
from agent.agents.integration import record_agent_result

from agent.scenarios.attacks.tampered_evidence import detect_tampered_evidence
from agent.scenarios.attacks.replayed_action import detect_replayed_action
from agent.scenarios.attacks.unauthorized_action import detect_unauthorized_action

BASE_DIR = __file__.replace("\\run_demo.py", "")


def load_scenario(filename, module_name):
    path = f"{BASE_DIR}\\scenarios\\{filename}"

    spec = importlib.util.spec_from_file_location(
        module_name,
        path
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# Load scenario modules
valid_scenario = load_scenario(
    "01_valid_action.py",
    "valid_action"
)

hallucination_scenario = load_scenario(
    "02_hallucinated_balance.py",
    "hallucinated_balance"
)

threshold_scenario = load_scenario(
    "03_over_threshold_refund.py",
    "over_threshold_refund"
)


print("\n======================================")
print("       SAARTHI MEMBER-B DEMO")
print("======================================\n")


# -------------------------------------------------
# SCENARIO 1 — VALID ACTION
# -------------------------------------------------

action_1 = create_valid_refund()

account_1 = get_account(action_1["arguments"]["customer_id"])

print("Account:")
print(account_1)

if account_1 is None:
    verdict_1 = {
        "decision": "REJECT",
        "risk": "HIGH",
        "violations": ["ACCOUNT_NOT_FOUND"]
    }

elif account_1["account_status"] != "ACTIVE":
    verdict_1 = {
        "decision": "REJECT",
        "risk": "HIGH",
        "violations": ["ACCOUNT_INACTIVE"]
    }

elif account_1["authorization_status"] != "AUTHORIZED":
    verdict_1 = {
        "decision": "REJECT",
        "risk": "HIGH",
        "violations": ["ACCOUNT_NOT_AUTHORIZED"]
    }

else:
    verdict_1 = valid_scenario.validate_action(action_1)


print("Action:")
print(action_1)

print("\nVerdict:")
print(verdict_1)

record_agent_result(
    action_1,
    verdict_1
)



# -------------------------------------------------
# SCENARIO 2 — HALLUCINATED BALANCE
# -------------------------------------------------

print("\n===== SCENARIO 2: HALLUCINATED BALANCE =====")

action_2 = create_valid_refund()

verdict_2 = hallucination_scenario.validate_hallucinated_balance(
    action_2
)

print("Action:")
print(action_2)

print("\nVerdict:")
print(verdict_2)

record_agent_result(
    action_2,
    verdict_2
)


# -------------------------------------------------
# SCENARIO 3 — OVER-THRESHOLD REFUND
# -------------------------------------------------

print("\n===== SCENARIO 3: OVER-THRESHOLD REFUND =====")

action_3 = create_valid_refund()

action_3["arguments"]["amount"] = 15000

verdict_3 = threshold_scenario.validate_over_threshold_refund(
    action_3
)

print("Action:")
print(action_3)

print("\nVerdict:")
print(verdict_3)

record_agent_result(
    action_3,
    verdict_3
)
# --------------------------------------------------
# ATTACK SCENARIO 1 - TAMPERED EVIDENCE
# --------------------------------------------------

print("\n===== ATTACK 1: TAMPERED EVIDENCE =====")

tampered_action = copy.deepcopy(action_1)

tampered_action["evidence"]["balance"] = 15000

tampered_verdict = detect_tampered_evidence(tampered_action)

print("Action:")
print(tampered_action)

print("\nVerdict:")
print(tampered_verdict)

record_agent_result(
    tampered_action,
    tampered_verdict
)


# --------------------------------------------------
# ATTACK SCENARIO 2 - REPLAYED ACTION
# --------------------------------------------------

print("\n===== ATTACK 2: REPLAYED ACTION =====")

seen_actions = set()

replay_verdict_1 = detect_replayed_action(
    action_1,
    seen_actions
)

replay_verdict_2 = detect_replayed_action(
    action_1,
    seen_actions
)

print("First submission:")
print(replay_verdict_1)

print("\nSecond submission:")
print(replay_verdict_2)

record_agent_result(
    {
        **action_1,
        "action_id": action_1["action_id"] + "-REPLAY"
    },
    replay_verdict_2
)


# --------------------------------------------------
# ATTACK SCENARIO 3 - UNAUTHORIZED ACTION
# --------------------------------------------------

print("\n===== ATTACK 3: UNAUTHORIZED ACTION =====")

unauthorized_action = copy.deepcopy(action_1)

unauthorized_action["action"] = "delete_customer"

allowed_actions = {
    "issue_refund",
    "check_balance"
}

unauthorized_verdict = detect_unauthorized_action(
    unauthorized_action,
    allowed_actions
)

print("Requested action:")
print(unauthorized_action["action"])

print("\nAllowed actions:")
print(allowed_actions)

print("\nVerdict:")
print(unauthorized_verdict)

record_agent_result(
    {
        **unauthorized_action,
        "action_id": unauthorized_action["action_id"] + "-UNAUTHORIZED"
    },
    unauthorized_verdict
)


print("\n======================================")
print("       DEMO COMPLETE")
print("======================================")

from agent.audit.verify_chain import verify_chain

print("\n===== VERIFYING AUDIT LEDGER =====")

verify_chain()