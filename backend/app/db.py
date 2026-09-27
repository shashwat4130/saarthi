from pathlib import Path
import sqlite3

from app.config import settings


def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite connection for the SAARTHI database.
    """

    db_path = Path(settings.DATABASE_PATH)

    if not db_path.is_absolute():
        db_path = Path(__file__).resolve().parents[2] / db_path

    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,
    )

    conn.row_factory = sqlite3.Row

    # SQLite settings for reliable local development.
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    return conn


def init_db() -> None:
    """
    Initialize the SAARTHI SQLite database and seed deterministic demo data.
    """

    conn = get_db_connection()

    try:
        # Trusted account state used by the ground-truth verifier.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mock_accounts (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                balance REAL NOT NULL,
                credit_limit REAL NOT NULL,
                is_active INTEGER NOT NULL
            )
            """
        )

        # Audit ledger table.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                previous_hash TEXT,
                signature TEXT
            )
            """
        )

        # Deterministic demo accounts.
        accounts = [
            (
                "C101",
                "Aarav",
                "ACTIVE",
                15400.0,
                4999.0,
                1,
            ),
            (
                "C102",
                "Priya",
                "ACTIVE",
                5200.0,
                1200.0,
                1,
            ),
            (
                "C103",
                "Vikram",
                "SUSPENDED",
                50000.0,
                0.0,
                0,
            ),
        ]

        conn.executemany(
            """
            INSERT OR IGNORE INTO mock_accounts (
                customer_id,
                name,
                status,
                balance,
                credit_limit,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            accounts,
        )

        conn.commit()

    finally:
        conn.close()