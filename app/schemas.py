# app\schemas.py
from typing import Literal

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
    will_come: Literal["yes", "no"]
    comment_will_come: str | None = ""
    allergies: bool | None = None
    allergies_details: str | None = ""
    alcohol: bool | None = None
    additional_info: str | None = ""


class ResponseOut(BaseModel):
    id: int
    invitation_id: int
    will_come: Literal["yes", "no"] | None = None
    comment_will_come: str | None = ""
    allergies: bool | None = None
    allergies_details: str | None = ""
    alcohol: bool | None = None
    additional_info: str | None = ""
    answered_at: str


class StatsOut(BaseModel):
    total_invitations: int
    confirmed: int
    declined: int
    unanswered: int
