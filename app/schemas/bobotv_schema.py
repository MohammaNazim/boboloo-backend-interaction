from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# =========================
# VIDEO RESPONSE
# =========================
class VideoResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    file_size: int
    mime_type: str
    uploaded_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# VIDEO LIST RESPONSE
# =========================
class VideoListResponse(BaseModel):
    items: list[VideoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =========================
# STREAM URL RESPONSE
# =========================
class VideoStreamResponse(BaseModel):
    video_id: UUID
    stream_url: str
    expires_in: int = Field(description="Seconds until the URL expires")


# =========================
# DELETE RESPONSE
# =========================
class VideoDeleteResponse(BaseModel):
    video_id: UUID
    deleted: bool
