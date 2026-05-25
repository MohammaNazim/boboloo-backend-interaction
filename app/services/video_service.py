import uuid
import math
import re
import logging

import magic
import aioboto3
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.models import BoboTVVideo
from app.core.config import settings

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
ALLOWED_MIME_TYPES = {"video/mp4", "video/quicktime"}

# Bytes read from the start of the file for MIME inspection
_MAGIC_READ_BYTES = 2048


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _safe_filename(filename: str) -> str:
    """Strip path traversal and keep only safe characters."""
    name = filename.split("/")[-1].split("\\")[-1]
    name = re.sub(r"[^\w.\-]", "_", name)
    return name[:200] or "upload"


def _s3_key(video_id: uuid.UUID, filename: str) -> str:
    return f"bobotv/videos/{video_id}/{_safe_filename(filename)}"


def _s3_client_kwargs() -> dict:
    kwargs: dict = {"region_name": settings.AWS_REGION}
    if settings.AWS_ACCESS_KEY_ID:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
    if settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return kwargs


# ─────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────
async def _validate_upload(file: UploadFile) -> tuple[bytes, str]:
    """
    Returns (full_content, mime_type).
    Raises HTTPException on validation failure.
    """
    max_bytes = settings.BOBOTV_MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # Read the magic header bytes first (no full load yet)
    header = await file.read(_MAGIC_READ_BYTES)
    if len(header) < 8:
        raise HTTPException(status_code=400, detail="File is too small to be a valid video.")

    mime_type = magic.from_buffer(header, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{mime_type}'. Allowed: {sorted(ALLOWED_MIME_TYPES)}",
        )

    # Seek back and read the complete file for size check + upload
    await file.seek(0)
    content = await file.read()

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.BOBOTV_MAX_UPLOAD_SIZE_MB} MB limit.",
        )

    return content, mime_type


# ─────────────────────────────────────────────
# S3 Upload
# ─────────────────────────────────────────────
async def _upload_to_s3(content: bytes, s3_key: str, mime_type: str) -> None:
    if not settings.AWS_S3_BUCKET_BOBOTV:
        raise HTTPException(
            status_code=503,
            detail="BoboTV S3 bucket is not configured.",
        )

    session = aioboto3.Session()
    async with session.client("s3", **_s3_client_kwargs()) as s3:
        await s3.put_object(
            Bucket=settings.AWS_S3_BUCKET_BOBOTV,
            Key=s3_key,
            Body=content,
            ContentType=mime_type,
            # Bucket-level block-public-access policy enforces private access;
            # explicit ACL is omitted to avoid BucketOwnerEnforced errors.
        )


# ─────────────────────────────────────────────
# S3 Delete
# ─────────────────────────────────────────────
async def _delete_from_s3(s3_key: str) -> None:
    if not settings.AWS_S3_BUCKET_BOBOTV:
        return

    session = aioboto3.Session()
    async with session.client("s3", **_s3_client_kwargs()) as s3:
        await s3.delete_object(
            Bucket=settings.AWS_S3_BUCKET_BOBOTV,
            Key=s3_key,
        )


# ─────────────────────────────────────────────
# Presigned URL
# ─────────────────────────────────────────────
async def generate_presigned_url(s3_key: str) -> str:
    if not settings.AWS_S3_BUCKET_BOBOTV:
        raise HTTPException(
            status_code=503,
            detail="BoboTV S3 bucket is not configured.",
        )

    session = aioboto3.Session()
    async with session.client("s3", **_s3_client_kwargs()) as s3:
        url = await s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_S3_BUCKET_BOBOTV,
                "Key": s3_key,
            },
            ExpiresIn=settings.BOBOTV_PRESIGNED_URL_EXPIRY,
        )
    return url


# ─────────────────────────────────────────────
# Service: Upload
# ─────────────────────────────────────────────
async def upload_video(
    db: AsyncSession,
    file: UploadFile,
    title: str,
    description: str | None,
    admin_uid: str,
) -> BoboTVVideo:
    content, mime_type = await _validate_upload(file)

    video_id = uuid.uuid4()
    filename = file.filename or "video.mp4"
    key = _s3_key(video_id, filename)

    await _upload_to_s3(content, key, mime_type)

    video = BoboTVVideo(
        id=video_id,
        title=title.strip(),
        description=description.strip() if description else None,
        s3_key=key,
        file_size=len(content),
        mime_type=mime_type,
        uploaded_by=admin_uid,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    log.info("BoboTV video uploaded: %s (%s bytes) by %s", key, len(content), admin_uid)
    return video


# ─────────────────────────────────────────────
# Service: List
# ─────────────────────────────────────────────
async def list_videos(
    db: AsyncSession,
    page: int,
    page_size: int,
) -> tuple[list[BoboTVVideo], int]:
    offset = (page - 1) * page_size

    count_result = await db.execute(
        select(func.count()).where(BoboTVVideo.is_active == True)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(BoboTVVideo)
        .where(BoboTVVideo.is_active == True)
        .order_by(BoboTVVideo.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    videos = list(result.scalars().all())

    return videos, total


# ─────────────────────────────────────────────
# Service: Stream URL
# ─────────────────────────────────────────────
async def get_stream_url(
    db: AsyncSession,
    video_id: uuid.UUID,
) -> tuple[BoboTVVideo, str]:
    result = await db.execute(
        select(BoboTVVideo).where(
            BoboTVVideo.id == video_id,
            BoboTVVideo.is_active == True,
        )
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")

    url = await generate_presigned_url(video.s3_key)
    return video, url


# ─────────────────────────────────────────────
# Service: Delete
# ─────────────────────────────────────────────
async def delete_video(
    db: AsyncSession,
    video_id: uuid.UUID,
) -> BoboTVVideo:
    result = await db.execute(
        select(BoboTVVideo).where(
            BoboTVVideo.id == video_id,
            BoboTVVideo.is_active == True,
        )
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")

    # Soft-delete first, then attempt S3 removal
    video.is_active = False
    await db.commit()

    try:
        await _delete_from_s3(video.s3_key)
    except Exception as exc:
        log.error("S3 delete failed for key %s: %s", video.s3_key, exc)
        # DB record is already soft-deleted; S3 cleanup can be retried manually

    log.info("BoboTV video deleted: %s", video.s3_key)
    return video
