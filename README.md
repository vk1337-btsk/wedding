# Wedding Invitation Site

Свадебный сайт-приглашение с персональными ссылками и RSVP.

## Запуск проекта

1. Установите зависимости через Poetry:

```bash
poetry install
```

2. Запустите сервер:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Откройте:

- `http://localhost:8000/invite/A1B2C3` — пользовательская страница
- `http://localhost:8000/admin` — административная панель

## Конфигурация

Параметры управления в файле `.env`.

- `ADMIN_USER`
- `ADMIN_PASSWORD`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `NOTIFY_TO`

## Структура

- `app/main.py` — FastAPI приложение
- `app/db.py` — инициализация SQLite
- `app/crud.py` — операции с БД
- `app/config.py` — настройки
- `app/static/` — фронтенд
