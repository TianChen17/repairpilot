import os
from pathlib import Path

import psycopg
from app.config import Settings
from app.deepseek import DeepSeekRepairGenerator
from app.warehouse import WarehouseRunner


def test_real_breaking_change_and_repair_build(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
    settings = Settings(
        repairpilot_runtime_dir=tmp_path / "runtime",
        repairpilot_repo_root=repo_root,
        postgres_host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5433")),
        postgres_db=os.getenv("POSTGRES_DB", "repairpilot"),
        postgres_user=os.getenv("POSTGRES_USER", "repairpilot"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "repairpilot-local-only"),
    )
    runner = WarehouseRunner(settings)

    result = runner.validate_repair("integration1234", DeepSeekRepairGenerator.replay_proposal())

    assert result.breaking_change_reproduced is True
    assert result.repair_verified is True
    assert result.tests_passed == 14
    assert result.tests_failed == 0
    assert len(result.patch_sha256) == 64
    assert Path(result.patch_path).is_file()
    assert len(result.base_commit) == 40
    assert len(result.repair_commit) == 40
    assert not (settings.repairpilot_runtime_dir / "worktrees/integration1234").exists()

    runner.reset_demo_schemas()
    with psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "select count(*) from information_schema.schemata "
                "where schema_name like 'rp\\_integration1\\_%' escape '\\'"
            )
            assert cursor.fetchone() == (0,)


def test_warehouse_subprocess_environment_excludes_secrets(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY_FILE", "/run/credentials/secret")
    monkeypatch.setenv("GITHUB_PAT_TianChen_17", "must-not-propagate")

    safe = WarehouseRunner._safe_subprocess_env()

    assert "DEEPSEEK_API_KEY_FILE" not in safe
    assert "GITHUB_PAT_TianChen_17" not in safe
