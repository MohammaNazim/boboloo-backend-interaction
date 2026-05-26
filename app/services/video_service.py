import uuid
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

_MAGIC_HEADER_BYTES = 2048

# Each S3 multipart part (except the last) must be >= 5 MB.
# 8 MB gives comfortable headroom and good throughput.
_PART_SIZE = 8 * 1024 * 1024  # 8 MB


# ─────────────────────────────────────────────
# Internal exceptions
# ─────────────────────────────────────────────
class _UploadTooLarge(Exception):
    """Raised when the byte counter exceeds the configured limit."""


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _safe_filename(filename: str) -> str:
    name = filename.split("/")[-1].split("\\")[-1]
    name = re.sub(r"[^\w.\-]", "_", name)
    return name[:200] or "upload"


def _s3_key(video_id: uuid.UUID, filename: str) -> str:
    return f"bobotv/videos/{video_id}/{_safe_filename(filename)}"


def _s3_kwargs() -> dict:
    kwargs: dict = {"region_name": settings.AWS_REGION}
    if settings.AWS_ACCESS_KEY_ID:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
    if settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return kwargs


# ─────────────────────────────────────────────
# MIME validation
# ─────────────────────────────────────────────
async def _validate_mime(file: UploadFile) -> str:
    """
    Read only the magic header bytes to identify MIME type.
    Seeks back to position 0 so the full file can be streamed afterward.
    Never loads the full file into memory.
    """
    header = await file.read(_MAGIC_HEADER_BYTES)
    if len(header) < 8:
        raise HTTPException(status_code=400, detail="File too small to be a valid video.")

    mime = magic.from_buffer(header, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{mime}'. Allowed: {sorted(ALLOWED_MIME_TYPES)}",
        )

    await file.seek(0)
    return mime


# ─────────────────────────────────────────────
# Streaming multipart upload to S3
# ─────────────────────────────────────────────
async def _multipart_upload(
    file: UploadFile,
    s3_key: str,
    mime: str,
    max_bytes: int,
) -> int:
    """
    Stream the upload file to S3 using multipart upload.

    Memory usage = one chunk at a time (_PART_SIZE = 8 MB).
    A 150 MB video uses ~8 MB RAM, not 150 MB.

    Returns total bytes uploaded.
    Aborts the multipart upload on any failure to avoid orphan S3 parts.
    """
    bucket = settings.AWS_S3_BUCKET_BOBOTV
    if not bucket:
        raise HTTPException(status_code=503, detail="BoboTV S3 bucket is not configured.")

    upload_id: str | None = None
    session = aioboto3.Session()

    async with session.client("s3", **_s3_kwargs()) as s3:
        try:
            mpu = await s3.create_multipart_upload(
                Bucket=bucket,
                Key=s3_key,
                ContentType=mime,
            )
            upload_id = mpu["UploadId"]

            parts: list[dict] = []
            total_bytes = 0
            part_num = 1

            while True:
                # Read one chunk — at most _PART_SIZE bytes stay in memory at once
                chunk = await file.read(_PART_SIZE)
                if not chunk:
                    break

                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise _UploadTooLarge()

                resp = await s3.upload_part(
                    Bucket=bucket,
                    Key=s3_key,
                    UploadId=upload_id,
                    PartNumber=part_num,
                    Body=chunk,
                )
                parts.append({"PartNumber": part_num, "ETag": resp["ETag"]})
                log.debug(
                    "BoboTV multipart | key=%s part=%d cumulative=%d bytes",
                    s3_key, part_num, total_bytes,
                )
                part_num += 1

            if not parts:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")

            await s3.complete_multipart_upload(
                Bucket=bucket,
                Key=s3_key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )

            log.info(
                "BoboTV S3 upload complete | key=%s parts=%d bytes=%d",
                s3_key, len(parts), total_bytes,
            )
            return total_bytes

        except _UploadTooLarge:
            # Abort before raising so S3 does not keep incomplete parts
            if upload_id:
                try:
                    await s3.abort_multipart_upload(
                        Bucket=bucket, Key=s3_key, UploadId=upload_id
                    )
                except Exception as abort_exc:
                    log.warning("Abort failed for %s: %s", s3_key, abort_exc)
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the {settings.BOBOTV_MAX_UPLOAD_SIZE_MB} MB limit.",
            )

        except HTTPException:
            if upload_id:
                try:
                    await s3.abort_multipart_upload(
                        Bucket=bucket, Key=s3_key, UploadId=upload_id
                    )
                except Exception as abort_exc:
                    log.warning("Abort failed for %s: %s", s3_key, abort_exc)
            raise

        except Exception as exc:
            log.error("S3 multipart upload failed for %s: %s", s3_key, exc)
            if upload_id:
                try:
                    await s3.abort_multipart_upload(
                        Bucket=bucket, Key=s3_key, UploadId=upload_id
                    )
                except Exception as abort_exc:
                    log.warning("Abort failed for %s: %s", s3_key, abort_exc)
            raise HTTPException(status_code=502, detail="Failed to upload video to storage.")


# ─────────────────────────────────────────────
# S3 Delete
# ─────────────────────────────────────────────
async def _delete_from_s3(s3_key: str) -> None:
    if not settings.AWS_S3_BUCKET_BOBOTV:
        return
    try:
        session = aioboto3.Session()
        async with session.client("s3", **_s3_kwargs()) as s3:
            await s3.delete_object(
                Bucket=settings.AWS_S3_BUCKET_BOBOTV,
                Key=s3_key,
            )
    except Exception as exc:
        log.error("S3 delete failed for %s: %s", s3_key, exc)


# ─────────────────────────────────────────────
# Presigned streaming URL
# ─────────────────────────────────────────────
async def generate_presigned_url(s3_key: str) -> str:
    if not settings.AWS_S3_BUCKET_BOBOTV:
        raise HTTPException(status_code=503, detail="BoboTV S3 bucket is not configured.")

    session = aioboto3.Session()
    async with session.client("s3", **_s3_kwargs()) as s3:
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
# Service: Upload (admin only)
# ─────────────────────────────────────────────
async def upload_video(
    db: AsyncSession,
    file: UploadFile,
    title: str,
    description: str | None,
    admin_uid: str,
) -> BoboTVVideo:
    max_bytes = settings.BOBOTV_MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # Validate MIME from magic header only — no full file load
    mime = await _validate_mime(file)

    video_id = uuid.uuid4()
    key = _s3_key(video_id, file.filename or "video.mp4")

    # Stream directly to S3; total_bytes is the exact uploaded size
    total_bytes = await _multipart_upload(file, key, mime, max_bytes)

    video = BoboTVVideo(
        id=video_id,
        title=title.strip(),
        description=description.strip() if description else None,
        s3_key=key,
        file_size=total_bytes,
        mime_type=mime,
        uploaded_by=admin_uid,
    )
    db.add(video)
    try:
        await db.commit()
        await db.refresh(video)
    except Exception as exc:
        log.error(
            "DB commit failed after S3 upload of %s: %s — rolling back and removing S3 object",
            key, exc,
        )
        await db.rollback()
        # Best-effort S3 cleanup to avoid orphaned objects
        await _delete_from_s3(key)
        raise HTTPException(status_code=500, detail="Failed to save video metadata.")

    log.info(
        "BoboTV video ready | id=%s key=%s bytes=%d mime=%s uploader=%s",
        video_id, key, total_bytes, mime, admin_uid,
    )
    return video


# ─────────────────────────────────────────────
# Service: List (parent)
# ─────────────────────────────────────────────
async def list_videos(
    db: AsyncSession,
    page: int,
    page_size: int,
) -> tuple[list[BoboTVVideo], int]:
    offset = (page - 1) * page_size

    count_result = await db.execute(
        select(func.count(BoboTVVideo.id)).where(BoboTVVideo.is_active == True)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(BoboTVVideo)
        .where(BoboTVVideo.is_active == True)
        .order_by(BoboTVVideo.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


# ─────────────────────────────────────────────
# Service: Stream URL (parent)
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
# Service: Soft-delete (admin)
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

    # Soft-delete the DB record first so the video disappears from listings
    # immediately even if S3 removal is slow or temporarily fails.
    video.is_active = False
    await db.commit()

    try:
        await _delete_from_s3(video.s3_key)
    except Exception as exc:
        log.error(
            "S3 cleanup failed for %s (DB already soft-deleted): %s",
            video.s3_key, exc,
        )

    log.info("BoboTV video deleted | id=%s key=%s", video_id, video.s3_key)
    return video
