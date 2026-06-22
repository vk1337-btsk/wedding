# app\main.py
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from secrets import compare_digest

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from . import crud, email_utils
from .config import settings
from .db import init_db
from .schemas import InvitationCreate, ResponseCreate, ResponseOut


# === LIFESPAN (вместо @app.on_event) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP - код, который был в startup_event
    logging.info("🚀 Application starting up...")
    init_db()  # Инициализация базы данных
    logging.info("✅ Database initialized")

    yield  # Здесь приложение работает и обрабатывает запросы

    # SHUTDOWN - если нужно что-то закрыть
    logging.info("🛑 Application shutting down...")
    # Здесь можно добавить закрытие соединений, если нужно


# Создаем приложение с lifespan
app = FastAPI(title="Wedding Invitation", lifespan=lifespan)  # <-- Добавляем lifespan

security = HTTPBasic()

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/photos", StaticFiles(directory="app/static/photos"), name="photos")


def get_admin_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    valid_user = compare_digest(credentials.username, settings.admin_user)
    valid_pass = compare_digest(credentials.password, settings.admin_password)
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/", response_class=HTMLResponse)
def homepage() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/invite/{code}", response_class=HTMLResponse)
def invite_page(code: str) -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/admin", response_class=HTMLResponse)
def admin_page(_: str = Depends(get_admin_user)) -> FileResponse:
    return FileResponse(static_dir / "admin.html")


@app.get("/api/invite/{code}")
def invite_info(code: str) -> dict:
    invitation = crud.get_invitation_by_code(code)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    responses = crud.get_responses_for_invitation(invitation["id"])
    return {
        "invitation": invitation,
        "responses": responses,
    }


@app.post("/api/respond/{code}", response_model=ResponseOut)
def submit_response(code: str, payload: ResponseCreate) -> dict:
    invitation = crud.get_invitation_by_code(code)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    response = crud.create_response(
        invitation_id=invitation["id"],
        will_come=payload.will_come,
        comment_will_come=payload.comment_will_come,
        allergies=payload.allergies,
        allergies_details=payload.allergies_details,
        alcohol=payload.alcohol,
        additional_info=payload.additional_info,
    )
    try:
        email_utils.send_response_email(invitation, response)
    except Exception as error:
        logging.error(f"Failed to send email: {error}")
    return response


@app.get("/api/admin/invitations")
def admin_invitations(_: str = Depends(get_admin_user)) -> dict:
    return {"invitations": crud.list_invitations()}


@app.post("/api/admin/invitations")
def admin_create_invitation(payload: InvitationCreate, _: str = Depends(get_admin_user)) -> dict:
    invitation = crud.create_invitation(payload.guest_name, payload.invitation_text, payload.invite_code)
    return invitation


@app.put("/api/admin/invitations/{invitation_id}")
def admin_update_invitation(invitation_id: int, payload: InvitationCreate, _: str = Depends(get_admin_user)) -> dict:
    invitation = crud.update_invitation(invitation_id, payload.guest_name, payload.invitation_text)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return invitation


@app.delete("/api/admin/invitations/{invitation_id}")
def admin_delete_invitation(invitation_id: int, _: str = Depends(get_admin_user)) -> dict:
    crud.delete_invitation(invitation_id)
    return {"status": "deleted"}


@app.get("/api/admin/responses")
def admin_responses(_: str = Depends(get_admin_user)) -> dict:
    return {"responses": crud.list_responses()}


@app.get("/api/admin/stats")
def admin_stats(_: str = Depends(get_admin_user)) -> dict:
    return crud.count_stats()


@app.post("/api/admin/responses")
def admin_create_response(invitation_id: int, payload: ResponseCreate, _: str = Depends(get_admin_user)) -> dict:
    # Проверим, существует ли приглашение
    invitation = crud.get_invitation(invitation_id)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    response = crud.create_response(
        invitation_id=invitation_id,
        will_come=payload.will_come,
        comment_will_come=payload.comment_will_come,
        allergies=payload.allergies,
        allergies_details=payload.allergies_details,
        alcohol=payload.alcohol,
        additional_info=payload.additional_info,
    )
    return response


@app.put("/api/admin/responses/{response_id}")
def admin_update_response(response_id: int, payload: ResponseCreate, _: str = Depends(get_admin_user)) -> dict:
    # В crud.py нужно добавить функцию update_response
    response = crud.update_response(
        response_id=response_id,
        will_come=payload.will_come,
        comment_will_come=payload.comment_will_come,
        allergies=payload.allergies,
        allergies_details=payload.allergies_details,
        alcohol=payload.alcohol,
        additional_info=payload.additional_info,
    )
    if response is None:
        raise HTTPException(status_code=404, detail="Response not found")
    return response


@app.delete("/api/admin/responses/{response_id}")
def admin_delete_response(response_id: int, _: str = Depends(get_admin_user)) -> dict:
    crud.delete_response(response_id)
    return {"status": "deleted"}
