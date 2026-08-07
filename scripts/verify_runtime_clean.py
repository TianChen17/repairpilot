#!/usr/bin/env python3
"""Fail unless RepairPilot left no temporary database schemas or worktrees."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    worktrees = repo_root / "runtime/worktrees"
    residual_worktrees = list(worktrees.iterdir()) if worktrees.exists() else []
    with psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        dbname=os.getenv("POSTGRES_DB", "repairpilot"),
        user=os.getenv("POSTGRES_USER", "repairpilot"),
        password=os.getenv("POSTGRES_PASSWORD", "repairpilot-local-only"),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "select schema_name from information_schema.schemata "
                "where schema_name like 'rp\\_%' escape '\\' order by schema_name"
            )
            schemas = [row[0] for row in cursor.fetchall()]
    if schemas or residual_worktrees:
        raise SystemExit(
            f"Residual runtime state: schemas={schemas}, worktrees={residual_worktrees}"
        )
    print("runtime_cleanup=pass schemas=0 worktrees=0")


if __name__ == "__main__":
    main()
