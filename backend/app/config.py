from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    repairpilot_mode: str = "live"
    repairpilot_runtime_dir: Path = Path("runtime")
    repairpilot_repo_root: Path = Path.cwd()
    repairpilot_public_url: str = "http://127.0.0.1:8766"

    datahub_frontend_url: str = "http://127.0.0.1:9002"
    datahub_gms_url: str = "http://127.0.0.1:8080"
    datahub_gms_token: str = ""
    datahub_mcp_command: str = "uvx"
    datahub_mcp_package: str = "mcp-server-datahub@0.6.0"

    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_api_key: str = Field(default="", repr=False)
    deepseek_api_key_file: Path | None = None

    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5433
    postgres_db: str = "repairpilot"
    postgres_user: str = "repairpilot"
    postgres_password: str = Field(default="repairpilot-local-only", repr=False)

    github_repository: str = "TianChen17/repairpilot"
    github_canonical_pr_url: str = ""

    def model_post_init(self, __context: object) -> None:
        if not self.deepseek_api_key and self.deepseek_api_key_file:
            self.deepseek_api_key = self.deepseek_api_key_file.read_text().strip()
        self.repairpilot_runtime_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
