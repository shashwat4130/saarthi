import hashlib
import hmac
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import Settings
from app.models.verdict import AuditRecord


class AuditLedger:
    """
    SAARTHI tamper-evident audit ledger.

    Every audit event contains:
        - event data
        - previous event hash
        - current event hash

    The current hash is calculated using HMAC-SHA256:

        HMAC(secret, payload + previous_hash)

    This creates a chained sequence of audit events.
    """

    def __init__(
        self,
        database_path: Optional[str] = None,
        secret: Optional[str] = None,
    ):
        settings = Settings()

        self.database_path = database_path or settings.DATABASE_PATH
        self.secret = (
            secret
            or settings.AUDIT_HMAC_SECRET
        ).encode("utf-8")

        self._ensure_table()

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _ensure_table(self) -> None:
        """
        Ensure the audit ledger table exists.

        The operation is idempotent and safe to call multiple times.
        """

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_ledger (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    payload_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL
                )
                """
            )

            connection.commit()

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def _calculate_hash(
        self,
        payload_json: str,
        previous_hash: str,
    ) -> str:
        """
        Calculate the HMAC-SHA256 hash for an audit event.
        """

        message = (
            payload_json
            + previous_hash
        ).encode("utf-8")

        return hmac.new(
            self.secret,
            message,
            hashlib.sha256,
        ).hexdigest()

    # ------------------------------------------------------------------
    # Previous hash
    # ------------------------------------------------------------------

    def _get_previous_hash(
        self,
        connection: sqlite3.Connection,
    ) -> str:
        """
        Get the hash of the latest audit event.

        The first event starts from a fixed genesis value.
        """

        row = connection.execute(
            """
            SELECT current_hash
            FROM audit_ledger
            ORDER BY rowid DESC
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            return "GENESIS"

        return row["current_hash"]

    # ------------------------------------------------------------------
    # Append event
    # ------------------------------------------------------------------

    def append(
        self,
        action_id: str,
        agent_id: str,
        action: str,
        decision: str,
        reason: str,
        risk_score: float,
        payload: Optional[Dict[str, Any]] = None,
    ) -> AuditRecord:
        """
        Append a new event to the audit chain.

        Returns:
            AuditRecord containing the generated event ID and hashes.
        """

        event_id = str(uuid.uuid4())

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        payload_data = payload or {}

        payload_json = json.dumps(
            payload_data,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

        with self._connect() as connection:

            previous_hash = self._get_previous_hash(
                connection
            )

            current_hash = self._calculate_hash(
                payload_json,
                previous_hash,
            )

            connection.execute(
                """
                INSERT INTO audit_ledger (
                    event_id,
                    timestamp,
                    action_id,
                    agent_id,
                    action,
                    decision,
                    reason,
                    risk_score,
                    payload_json,
                    previous_hash,
                    current_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    timestamp,
                    action_id,
                    agent_id,
                    action,
                    decision,
                    reason,
                    risk_score,
                    payload_json,
                    previous_hash,
                    current_hash,
                ),
            )

            connection.commit()

        return AuditRecord(
            event_id=event_id,
            timestamp=timestamp,
            action_id=action_id,
            agent_id=agent_id,
            action=action,
            decision=decision,
            reason=reason,
            risk_score=risk_score,
            payload_json=payload_json,
            previous_hash=previous_hash,
            current_hash=current_hash,
        )

    # ------------------------------------------------------------------
    # Read events
    # ------------------------------------------------------------------

    def get_recent(
        self,
        limit: int = 50,
    ) -> List[AuditRecord]:
        """
        Return the most recent audit events.

        Results are returned newest first.
        """

        limit = max(1, min(limit, 500))

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    event_id,
                    timestamp,
                    action_id,
                    agent_id,
                    action,
                    decision,
                    reason,
                    risk_score,
                    payload_json,
                    previous_hash,
                    current_hash
                FROM audit_ledger
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            AuditRecord(
                event_id=row["event_id"],
                timestamp=row["timestamp"],
                action_id=row["action_id"],
                agent_id=row["agent_id"],
                action=row["action"],
                decision=row["decision"],
                reason=row["reason"],
                risk_score=row["risk_score"],
                payload_json=row["payload_json"],
                previous_hash=row["previous_hash"],
                current_hash=row["current_hash"],
            )
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Verify chain
    # ------------------------------------------------------------------

    def verify_chain(self) -> Dict[str, Any]:
        """
        Verify the complete audit hash chain.

        Returns a structured verification result.
        """

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    event_id,
                    timestamp,
                    action_id,
                    agent_id,
                    action,
                    decision,
                    reason,
                    risk_score,
                    payload_json,
                    previous_hash,
                    current_hash
                FROM audit_ledger
                ORDER BY rowid ASC
                """
            ).fetchall()

        previous_hash = "GENESIS"

        for index, row in enumerate(rows):

            stored_previous_hash = row["previous_hash"]

            if stored_previous_hash != previous_hash:
                return {
                    "valid": False,
                    "events_checked": index,
                    "failed_event_id": row["event_id"],
                    "reason": "Previous hash mismatch",
                }

            expected_hash = self._calculate_hash(
                row["payload_json"],
                stored_previous_hash,
            )

            if not hmac.compare_digest(
                expected_hash,
                row["current_hash"],
            ):
                return {
                    "valid": False,
                    "events_checked": index + 1,
                    "failed_event_id": row["event_id"],
                    "reason": "Current hash mismatch",
                }

            previous_hash = row["current_hash"]

        return {
            "valid": True,
            "events_checked": len(rows),
            "failed_event_id": None,
            "reason": "Audit chain is valid",
        }