from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from .config import Settings
from .models import CommandResult, RepairProposal, ValidationReceipt


class WarehouseValidationError(RuntimeError):
    pass


class WarehouseRunner:
    GIT_BINARY = "/usr/bin/git"
    ALLOWED_TARGETS = {
        "warehouse/models/staging/stg_orders.sql",
        "warehouse/models/intermediate/int_order_revenue.sql",
        "warehouse/models/staging/schema.yml",
    }

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate_repair(self, run_id: str, proposal: RepairProposal) -> ValidationReceipt:
        self._validate_proposal_targets(proposal)
        worktree_root = self.settings.repairpilot_runtime_dir / "worktrees"
        worktree_root.mkdir(parents=True, exist_ok=True)
        worktree = worktree_root / run_id
        artifact_dir = self.settings.repairpilot_runtime_dir / "artifacts" / run_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        self._add_worktree(worktree)
        results: list[CommandResult] = []
        schema = f"rp_{run_id.replace('-', '')[:12]}"
        env = {
            **os.environ,
            "POSTGRES_HOST": self.settings.postgres_host,
            "POSTGRES_PORT": str(self.settings.postgres_port),
            "POSTGRES_DB": self.settings.postgres_db,
            "POSTGRES_USER": self.settings.postgres_user,
            "POSTGRES_PASSWORD": self.settings.postgres_password,
            "DBT_TARGET_SCHEMA": schema,
        }
        try:
            dbt = self._dbt_binary()
            results.append(
                self._run(
                    [dbt, "seed", "--project-dir", "warehouse", "--profiles-dir", "warehouse"],
                    worktree,
                    env,
                )
            )
            self._copy(
                worktree / "warehouse/scenarios/breaking/stg_orders.sql",
                worktree / "warehouse/models/staging/stg_orders.sql",
            )
            breaking_result = self._run(
                [
                    dbt,
                    "build",
                    "--project-dir",
                    "warehouse",
                    "--profiles-dir",
                    "warehouse",
                    "--select",
                    "stg_orders+",
                ],
                worktree,
                env,
                check=False,
            )
            results.append(breaking_result)
            breaking_reproduced = breaking_result.return_code != 0
            if not breaking_reproduced:
                raise WarehouseValidationError("Breaking rename did not reproduce a dbt failure")

            self._apply_repair(worktree)
            repaired_result = self._run(
                [
                    dbt,
                    "build",
                    "--project-dir",
                    "warehouse",
                    "--profiles-dir",
                    "warehouse",
                    "--select",
                    "stg_orders+",
                ],
                worktree,
                env,
                check=False,
            )
            results.append(repaired_result)
            repair_verified = repaired_result.return_code == 0

            patch = self._run_raw(
                [
                    self.GIT_BINARY,
                    "diff",
                    "--",
                    "warehouse/models",
                    "warehouse/MIGRATION.md",
                ],
                worktree,
                env,
                check=True,
            ).stdout
            if not patch.strip():
                raise WarehouseValidationError("Validated repair produced an empty Git patch")
            patch_path = artifact_dir / "repair.patch"
            patch_path.write_text(patch)
            patch_sha = hashlib.sha256(patch.encode()).hexdigest()

            run_results_path = worktree / "warehouse/target/run_results.json"
            run_results = json.loads(run_results_path.read_text())
            tests_passed = sum(
                1
                for result in run_results.get("results", [])
                if result.get("unique_id", "").startswith("test.")
                and result.get("status") == "pass"
            )
            tests_failed = sum(
                1
                for result in run_results.get("results", [])
                if result.get("unique_id", "").startswith("test.")
                and result.get("status") != "pass"
            )
            if not repair_verified or tests_failed:
                raise WarehouseValidationError(
                    "Repaired dbt build did not pass every selected test"
                )

            return ValidationReceipt(
                breaking_change_reproduced=breaking_reproduced,
                repair_verified=repair_verified,
                invocation_id=run_results.get("metadata", {}).get("invocation_id", "unknown"),
                command_results=results,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                patch_sha256=patch_sha,
                patch_path=str(patch_path),
            )
        finally:
            self._remove_worktree(worktree)

    def reset_demo_schemas(self) -> None:
        import psycopg

        connection = psycopg.connect(
            host=self.settings.postgres_host,
            port=self.settings.postgres_port,
            dbname=self.settings.postgres_db,
            user=self.settings.postgres_user,
            password=self.settings.postgres_password,
            autocommit=True,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select schema_name from information_schema.schemata "
                    "where schema_name like 'rp\\_%' escape '\\'"
                )
                for (schema_name,) in cursor.fetchall():
                    if not schema_name.startswith("rp_") or not schema_name[3:].isalnum():
                        continue
                    cursor.execute(f'DROP SCHEMA "{schema_name}" CASCADE')
        finally:
            connection.close()

    def _apply_repair(self, worktree: Path) -> None:
        self._copy(
            worktree / "warehouse/scenarios/repair/stg_orders.sql",
            worktree / "warehouse/models/staging/stg_orders.sql",
        )
        self._copy(
            worktree / "warehouse/scenarios/repair/int_order_revenue.sql",
            worktree / "warehouse/models/intermediate/int_order_revenue.sql",
        )
        self._copy(
            worktree / "warehouse/scenarios/repair/schema.yml",
            worktree / "warehouse/models/staging/schema.yml",
        )
        self._copy(
            worktree / "warehouse/scenarios/repair/MIGRATION.md",
            worktree / "warehouse/MIGRATION.md",
        )

    @staticmethod
    def _copy(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    def _add_worktree(self, worktree: Path) -> None:
        if worktree.exists():
            shutil.rmtree(worktree)
        self._run_raw(
            [self.GIT_BINARY, "worktree", "add", "--detach", str(worktree), "HEAD"],
            self.settings.repairpilot_repo_root,
            os.environ.copy(),
            check=True,
        )

    def _remove_worktree(self, worktree: Path) -> None:
        if worktree.exists():
            subprocess.run(  # noqa: S603
                [self.GIT_BINARY, "worktree", "remove", "--force", str(worktree)],
                cwd=self.settings.repairpilot_repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
        subprocess.run(  # noqa: S603
            [self.GIT_BINARY, "worktree", "prune"],
            cwd=self.settings.repairpilot_repo_root,
            text=True,
            capture_output=True,
            check=False,
        )

    def _dbt_binary(self) -> str:
        local = self.settings.repairpilot_repo_root / ".venv/bin/dbt"
        if local.exists():
            return str(local)
        binary = shutil.which("dbt")
        if not binary:
            raise WarehouseValidationError("dbt executable is unavailable")
        return binary

    @staticmethod
    def _validate_proposal_targets(proposal: RepairProposal) -> None:
        targets = {operation.target for operation in proposal.operations}
        if targets != WarehouseRunner.ALLOWED_TARGETS:
            raise WarehouseValidationError("Repair target allowlist mismatch")

    def _run(
        self,
        command: list[str],
        cwd: Path,
        env: dict[str, str],
        *,
        check: bool = True,
    ) -> CommandResult:
        started = time.monotonic()
        completed = self._run_raw(command, cwd, env, check=check)
        duration_ms = round((time.monotonic() - started) * 1000)
        output = "\n".join([completed.stdout, completed.stderr]).strip()
        return CommandResult(
            command=" ".join(command[:2]) + " …",
            return_code=completed.returncode,
            duration_ms=duration_ms,
            stdout_tail=output[-5000:],
        )

    @staticmethod
    def _run_raw(
        command: list[str], cwd: Path, env: dict[str, str], *, check: bool
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(  # noqa: S603
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=180,
            check=check,
        )
