# app\config.py
import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = APP_ROOT / ".env"


def _load_env_file() -> None:
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file()


class Settings:
    admin_user: str = os.getenv("ADMIN_USER", "")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", ""))
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    email: str = os.getenv("EMAIL", "")

    data_dir: Path = APP_ROOT / "data"
    photo_dir: Path = APP_ROOT / "app" / "static" / "photos"

    @property
    def db_path(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir / "wedding.db"


settings = Settings()
