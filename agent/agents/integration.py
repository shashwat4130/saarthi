from agent.audit.audit_ledger import append_audit_record


def record_agent_result(action, verdict):
    """
    Connects an agent action and its verdict to the audit ledger.
    """

    return append_audit_record(
        action_id=action["action_id"],
        agent_id=action["agent_id"],
        verdict=verdict
    )


if __name__ == "__main__":
    print("SAARTHI integration module ready.")