import importlib.util

from agent.agents.refund_agent import create_valid_refund
from agent.audit.audit_ledger import append_audit_record


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

print("===== SCENARIO 1: VALID ACTION =====")

action_1 = create_valid_refund()

verdict_1 = valid_scenario.validate_action(action_1)

print("Action:")
print(action_1)

print("\nVerdict:")
print(verdict_1)

append_audit_record(
    action_id=action_1["action_id"],
    agent_id=action_1["agent_id"],
    verdict=verdict_1
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

append_audit_record(
    action_id=action_2["action_id"],
    agent_id=action_2["agent_id"],
    verdict=verdict_2
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

append_audit_record(
    action_id=action_3["action_id"],
    agent_id=action_3["agent_id"],
    verdict=verdict_3
)


print("\n======================================")
print("       DEMO COMPLETE")
print("======================================")