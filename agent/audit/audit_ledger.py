import hashlib
import json
from datetime import datetime
from pathlib import Path


LEDGER_FILE = Path(__file__).resolve().parent / "audit_ledger.json"


def calculate_hash(block):
    """
    Calculate SHA-256 hash of a ledger block.
    """

    block_data = json.dumps(
        block,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        block_data.encode("utf-8")
    ).hexdigest()


def create_genesis_block():
    """
    Create the first block of the audit ledger.
    """

    block = {
        "index": 0,
        "timestamp": datetime.now().isoformat(),
        "action_id": "GENESIS",
        "agent_id": "SYSTEM",
        "verdict": {
            "decision": "GENESIS",
            "risk": "NONE",
            "violations": []
        },
        "previous_hash": "0"
    }

    block["current_hash"] = calculate_hash(block)

    return block


def load_ledger():
    """
    Load the existing audit ledger.
    """

    if not LEDGER_FILE.exists():
        return []

    with open(LEDGER_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_ledger(ledger):
    """
    Save the audit ledger.
    """

    with open(LEDGER_FILE, "w", encoding="utf-8") as file:
        json.dump(
            ledger,
            file,
            indent=2
        )


def append_audit_record(
    action_id,
    agent_id,
    verdict
):
    """
    Append a new immutable audit record
    to the hash chain.
    """

    ledger = load_ledger()

    if not ledger:
        genesis = create_genesis_block()
        ledger.append(genesis)

    previous_block = ledger[-1]

    block = {
        "index": len(ledger),
        "timestamp": datetime.now().isoformat(),
        "action_id": action_id,
        "agent_id": agent_id,
        "verdict": verdict,
        "previous_hash": previous_block["current_hash"]
    }

    block["current_hash"] = calculate_hash(block)

    ledger.append(block)

    save_ledger(ledger)

    return block


if __name__ == "__main__":

    test_verdict = {
        "decision": "ALLOW",
        "risk": "LOW",
        "violations": []
    }

    block = append_audit_record(
        action_id="TEST-ACTION-001",
        agent_id="refund-agent-01",
        verdict=test_verdict
    )

    print("=== AUDIT LEDGER ===")
    print(json.dumps(block, indent=2))