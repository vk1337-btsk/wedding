from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class InvitationBase(BaseModel):
    guest_name: str = Field(..., min_length=1)
    invitation_text: str = Field(..., min_length=1)


class InvitationCreate(InvitationBase):
    invite_code: str | None = None


class InvitationOut(InvitationBase):
    id: int
    invite_code: str
    created_at: str


class ResponseCreate(BaseModel):
    attendance: bool
    guest_count: int | None = None
    children: bool
    vegetarian: bool
    allergies: str | None = ""
    phone: str | None = ""
    telegram: str | None = ""
    comment: str | None = ""


class ResponseOut(BaseModel):
    id: int
    invitation_id: int
    attendance: bool
    guest_count: int | None = None
    children: bool
    vegetarian: bool
    allergies: str | None = ""
    phone: str | None = ""
    telegram: str | None = ""
    comment: str | None = ""
    answered_at: str


class PhotoOut(BaseModel):
    id: int
    filename: str
    original_filename: str
    sort_order: int
    uploaded_at: str


class ProgramItemBase(BaseModel):
    event_time: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)


class ProgramItemOut(ProgramItemBase):
    id: int
    sort_order: int


class StatsOut(BaseModel):
    total_invitations: int
    confirmed: int
    declined: int
    unanswered: int
