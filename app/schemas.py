"""Pydantic request/response schemas for the API."""

import uuid
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Session ID for conversation continuity",
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID used")


class ResetRequest(BaseModel):
    session_id: str = Field(..., description="Session ID to reset")


class ResetResponse(BaseModel):
    message: str = "Conversation reset successfully"
    session_id: str
