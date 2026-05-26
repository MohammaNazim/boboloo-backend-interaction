import math
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.auth.admin_auth import get_current_admin
from app.auth.firebase_auth import get_current_parent
from app.services.video_service import (
    delete_video,
    get_stream_url,
    list_videos,
    upload_video,
)
from app.schemas.bobotv_schema import (
    VideoDeleteResponse,
    VideoListResponse,
    VideoResponse,
    VideoStreamResponse,
)
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/bobotv",
    tags=["BoboTV"],
)


# ─────────────────────────────────────────────
# ADMIN: Upload video
# ─────────────────────────────────────────────
@router.post(
    "/videos",
    response_model=VideoResponse,
    summary="Upload a new video (admin only)",
)
async def upload_video_endpoint(
    title: str = Form(..., min_length=1, max_length=256),
    description: str | None = Form(default=None, max_length=2048),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    admin_uid: str = admin.get("uid", "unknown")
    video = await upload_video(
        db=db,
        file=file,
        title=title,
        description=description,
        admin_uid=admin_uid,
    )
    return video


# ─────────────────────────────────────────────
# PARENT: List videos (paginated)
# ─────────────────────────────────────────────
@router.get(
    "/videos",
    response_model=VideoListResponse,
    summary="List available videos",
)
async def list_videos_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    parent=Depends(get_current_parent),
):
    videos, total = await list_videos(db=db, page=page, page_size=page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return VideoListResponse(
        items=videos,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ─────────────────────────────────────────────
# PARENT: Get presigned stream URL
# ─────────────────────────────────────────────
@router.get(
    "/videos/{video_id}/stream",
    response_model=VideoStreamResponse,
    summary="Get a short-lived secure streaming URL",
)
async def stream_video_endpoint(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    parent=Depends(get_current_parent),
):
    video, url = await get_stream_url(db=db, video_id=video_id)
    return VideoStreamResponse(
        video_id=video.id,
        stream_url=url,
        expires_in=settings.BOBOTV_PRESIGNED_URL_EXPIRY,
    )


# ─────────────────────────────────────────────
# ADMIN: Delete video
# ─────────────────────────────────────────────
@router.delete(
    "/videos/{video_id}",
    response_model=VideoDeleteResponse,
    summary="Soft-delete a video and remove from S3 (admin only)",
)
async def delete_video_endpoint(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    video = await delete_video(db=db, video_id=video_id)
    return VideoDeleteResponse(video_id=video.id, deleted=True)
