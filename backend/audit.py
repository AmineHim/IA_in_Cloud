"""Audit logging: stores every reasoning step in SQLite for traceability."""

import sqlite3
import json
import uuid
from datetime import datetime, timezone

from config import AUDIT_DB_PATH


def _get_conn():
    conn = sqlite3.connect(AUDIT_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            timestamp TEXT,
            agent TEXT,
            action TEXT,
            input_data TEXT,
            output_data TEXT,
            sources TEXT,
            reasoning TEXT
        )
    """)
    conn.commit()
    return conn


def log_step(session_id: str, agent: str, action: str,
             input_data: str, output_data: str,
             sources: list[str] = None, reasoning: str = ""):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO audit_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            session_id,
            datetime.now(timezone.utc).isoformat(),
            agent,
            action,
            input_data,
            output_data,
            json.dumps(sources or []),
            reasoning,
        ),
    )
    conn.commit()
    conn.close()


def get_session_logs(session_id: str) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM audit_log WHERE session_id = ? ORDER BY timestamp",
        (session_id,),
    ).fetchall()
    conn.close()
    columns = ["id", "session_id", "timestamp", "agent", "action",
               "input_data", "output_data", "sources", "reasoning"]
    return [dict(zip(columns, row)) for row in rows]


def get_all_logs(limit: int = 100) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    columns = ["id", "session_id", "timestamp", "agent", "action",
               "input_data", "output_data", "sources", "reasoning"]
    return [dict(zip(columns, row)) for row in rows]
