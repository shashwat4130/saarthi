import hashlib
import json
from pathlib import Path


LEDGER_FILE = Path(__file__).resolve().parent / "audit_ledger.json"


def calculate_hash(block):
    block_data = {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "action_id": block["action_id"],
        "agent_id": block["agent_id"],
        "verdict": block["verdict"],
        "previous_hash": block["previous_hash"]
    }

    serialized = json.dumps(
        block_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def verify_chain():

    if not LEDGER_FILE.exists():
        print("Ledger file not found.")
        return False

    with open(LEDGER_FILE, "r", encoding="utf-8") as file:
        ledger = json.load(file)

    if not ledger:
        print("Ledger is empty.")
        return False

    for i, block in enumerate(ledger):

        # Verify current block hash
        expected_hash = calculate_hash(block)

        if block["current_hash"] != expected_hash:
            print(f"❌ BLOCK {i} HASH INVALID")
            return False

        # Verify connection with previous block
        if i == 0:

            if block["previous_hash"] != "0":
                print("❌ GENESIS BLOCK INVALID")
                return False

        else:

            previous_block = ledger[i - 1]

            if block["previous_hash"] != previous_block["current_hash"]:
                print(f"❌ BLOCK {i} CHAIN LINK INVALID")
                return False

    print("✅ AUDIT LEDGER VERIFIED")
    print(f"Total blocks: {len(ledger)}")

    return True


if __name__ == "__main__":
    verify_chain()