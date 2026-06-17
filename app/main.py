# app\main.py
from pathlib import Path
from secrets import compare_digest

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from . import crud, email_utils
from .config import settings
from .db import init_db
from .schemas import InvitationCreate, ResponseCreate
from .seed import seed_data

app = FastAPI(title="Wedding Invitation")
security = HTTPBasic()
static_dir = Path(__file__).resolve().parent / "static"
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


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    try:
        seed_data()
    except Exception:
        pass


@app.get("/", response_class=HTMLResponse)
def homepage() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/invite/{code}", response_class=HTMLResponse)
def invite_page(code: str) -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/admin", response_class=HTMLResponse)
def admin_page(_: str = Depends(get_admin_user)) -> FileResponse:
    return FileResponse(static_dir / "admin.html")


@app.get("/api/site")
def site_info() -> dict:
    return {
        "wedding_date": settings.wedding_date,
        "venue_name": settings.venue_name,
        "venue_address": settings.venue_address,
        "venue_time": settings.venue_time,
        "map_point": settings.map_point,
        "base_url": settings.base_url,
    }


@app.get("/api/invite/{code}")
def invite_info(code: str) -> dict:
    invitation = crud.get_invitation_by_code(code)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    response = crud.get_response_for_invitation(invitation["id"])
    return {
        "invitation": invitation,
        "response": response,
        "photos": [
            {**photo, "url": f"/static/photos/{photo['filename']}"}
            for photo in crud.list_photos()
        ],
        "program": crud.list_program_items(),
    }


@app.get("/api/program")
def program_list() -> dict:
    return {"program": crud.list_program_items()}


@app.get("/api/photos")
def photos_list() -> dict:
    return {
        "photos": [
            {**photo, "url": f"/static/photos/{photo['filename']}"}
            for photo in crud.list_photos()
        ]
    }


@app.post("/api/respond/{code}")
def submit_response(code: str, payload: ResponseCreate) -> dict:
    invitation = crud.get_invitation_by_code(code)
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if crud.get_response_for_invitation(invitation["id"]):
        raise HTTPException(status_code=409, detail="Response already received")
    if payload.attendance and (payload.guest_count is None or payload.guest_count < 1):
        raise HTTPException(
            status_code=400, detail="Guest count must be specified for attendance"
        )
    response = crud.create_response(
        invitation_id=invitation["id"],
        attendance=payload.attendance,
        guest_count=payload.guest_count,
        children=payload.children,
        vegetarian=payload.vegetarian,
        allergies=payload.allergies,
        phone=payload.phone,
        telegram=payload.telegram,
        comment=payload.comment,
    )
    try:
        email_utils.send_response_email(invitation, response)
    except Exception:
        pass
    return response


@app.get("/api/admin/invitations")
def admin_invitations(_: str = Depends(get_admin_user)) -> dict:
    return {"invitations": crud.list_invitations()}


@app.post("/api/admin/invitations")
def admin_create_invitation(
    payload: InvitationCreate, _: str = Depends(get_admin_user)
) -> dict:
    invitation = crud.create_invitation(
        payload.guest_name, payload.invitation_text, payload.invite_code
    )
    return invitation


@app.put("/api/admin/invitations/{invitation_id}")
def admin_update_invitation(
    invitation_id: int, payload: InvitationCreate, _: str = Depends(get_admin_user)
) -> dict:
    invitation = crud.update_invitation(
        invitation_id, payload.guest_name, payload.invitation_text
    )
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return invitation


@app.delete("/api/admin/invitations/{invitation_id}")
def admin_delete_invitation(
    invitation_id: int, _: str = Depends(get_admin_user)
) -> dict:
    crud.delete_invitation(invitation_id)
    return {"status": "deleted"}


@app.get("/api/admin/responses")
def admin_responses(_: str = Depends(get_admin_user)) -> dict:
    return {"responses": crud.list_responses()}


@app.get("/api/admin/stats")
def admin_stats(_: str = Depends(get_admin_user)) -> dict:
    return crud.count_stats()


@app.get("/api/admin/photos")
def admin_photos(_: str = Depends(get_admin_user)) -> dict:
    return {
        "photos": [
            {**photo, "url": f"/static/photos/{photo['filename']}"}
            for photo in crud.list_photos()
        ]
    }


@app.post("/api/admin/photos")
def admin_upload_photo(
    file: UploadFile = File(...), _: str = Depends(get_admin_user)
) -> dict:
    photo_dir = settings.photo_dir
    photo_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{crud.generate_code(10)}_{Path(str(file.filename)).name}"
    save_path = photo_dir / filename
    with save_path.open("wb") as stream:
        stream.write(file.file.read())
    existing = crud.list_photos()
    sort_order = max((photo["sort_order"] for photo in existing), default=0) + 1
    photo = crud.add_photo(filename, str(file.filename), sort_order)
    return {**photo, "url": f"/static/photos/{photo['filename']}"}


@app.delete("/api/admin/photos/{photo_id}")
def admin_delete_photo(photo_id: int, _: str = Depends(get_admin_user)) -> dict:
    crud.delete_photo(photo_id)
    return {"status": "deleted"}


@app.get("/api/admin/program")
def admin_program(_: str = Depends(get_admin_user)) -> dict:
    return {"program": crud.list_program_items()}


@app.post("/api/admin/program")
def admin_add_program(payload: dict, _: str = Depends(get_admin_user)) -> dict:
    program_item = crud.add_program_item(
        payload["event_time"], payload["title"], payload.get("sort_order", 100)
    )
    return program_item


@app.put("/api/admin/program/{item_id}")
def admin_update_program(
    item_id: int, payload: dict, _: str = Depends(get_admin_user)
) -> dict:
    program_item = crud.update_program_item(
        item_id, payload["event_time"], payload["title"], payload.get("sort_order", 100)
    )
    if program_item is None:
        raise HTTPException(status_code=404, detail="Program item not found")
    return program_item


@app.delete("/api/admin/program/{item_id}")
def admin_delete_program(item_id: int, _: str = Depends(get_admin_user)) -> dict:
    crud.delete_program_item(item_id)
    return {"status": "deleted"}
