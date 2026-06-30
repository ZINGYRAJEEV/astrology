"""Local persistence (Step 9 of the build plan).

A tiny SQLite store so users can save birth data, reload charts and compare
them later. We persist only the raw birth inputs; charts are recomputed on
load so results always reflect the latest engine logic.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime
from typing import List, Optional

from .chart_engine import BirthData

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "charts.db")


def _connect():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birth_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_chart(birth: BirthData) -> int:
    init_db()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO charts (name, birth_json, created_at) VALUES (?, ?, ?)",
            (birth.name or "Unnamed", json.dumps(asdict(birth)), datetime.now().isoformat()),
        )
        return cur.lastrowid


def list_charts() -> List[dict]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, name, birth_json, created_at FROM charts ORDER BY created_at DESC"
        ).fetchall()
    out = []
    for r in rows:
        b = json.loads(r["birth_json"])
        out.append({
            "id": r["id"],
            "name": r["name"],
            "created_at": r["created_at"],
            "summary": f"{b['day']:02d}/{b['month']:02d}/{b['year']} {b['hour']:02d}:{b['minute']:02d} - {b.get('place','')}",
            "birth": b,
        })
    return out


def load_birth(chart_id: int) -> Optional[BirthData]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT birth_json FROM charts WHERE id = ?", (chart_id,)
        ).fetchone()
    if not row:
        return None
    return BirthData(**json.loads(row["birth_json"]))


def delete_chart(chart_id: int) -> None:
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM charts WHERE id = ?", (chart_id,))
