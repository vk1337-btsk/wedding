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
    admin_user: str = os.getenv("ADMIN_USER", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "password")
    smtp_host: str = os.getenv("SMTP_HOST", "localhost")
    smtp_port: int = int(os.getenv("SMTP_PORT", "25"))
    smtp_user: str | None = os.getenv("SMTP_USER")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    email_from: str = os.getenv("EMAIL_FROM", "wedding@localhost")
    notify_to: str = os.getenv("NOTIFY_TO", "organizer@example.com")
    # По ТЗ: 29.08.2026 в 16:00, Алёна и Валерий, Ресторан Тургенев в Батайске
    wedding_date: str = os.getenv("WEDDING_DATE", "2026-08-29T16:00:00")
    venue_name: str = os.getenv("VENUE_NAME", "Ресторан Тургенев в Батайске")
    venue_address: str = os.getenv("VENUE_ADDRESS", "г. Батайск, ул. Центральная, 1")
    venue_time: str = os.getenv("VENUE_TIME", "16:00")
    map_point: str = os.getenv("MAP_POINT", "55.751244,37.618423")
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")
    data_dir: Path = APP_ROOT / "data"
    photo_dir: Path = APP_ROOT / "static" / "photos"

    @property
    def db_path(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir / "wedding.db"


settings = Settings()
