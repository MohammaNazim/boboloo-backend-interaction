#!/usr/bin/env python3
"""
seed_bobotv.py — Insert 3 demo BoboTV video records into the database.

These are placeholder metadata records. Before running this script you must
upload the actual video files to your S3 bucket at the exact s3_key paths
listed in DEMO_VIDEOS below, OR replace the s3_key values with your real keys.

Usage:
    python seed_bobotv.py

The script is idempotent: it skips any record whose title already exists.

Requires the same .env that the FastAPI app uses (DATABASE_URL, etc.).
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.models import BoboTVVideo

# ─── Demo video definitions ──────────────────────────────────────────────────
#
# S3 key format mirrors what video_service.py produces:
#   bobotv/videos/<uuid>/<filename>
#
# Upload your actual video files to these S3 keys before streaming them.
# You can also run:
#   aws s3 cp my_video.mp4 s3://<bucket>/bobotv/videos/<uuid>/<filename>
#
# Public domain / CC-0 child-friendly sources you can download and upload:
#   • Big Buck Bunny clips  — https://peach.blender.org/download/
#   • Elephant Dream        — https://orange.blender.org/download/
#   • NASA educational vids — https://www.nasa.gov/multimedia/videogallery/
# ─────────────────────────────────────────────────────────────────────────────

_ID1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
_ID2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
_ID3 = uuid.UUID("33333333-3333-3333-3333-333333333333")

DEMO_VIDEOS = [
    {
        "id": _ID1,
        "title": "Counting to 10 with Animals",
        "description": (
            "A colourful 3-minute video that teaches numbers 1–10 "
            "using friendly jungle animals. Perfect for ages 2–5."
        ),
        "s3_key": f"bobotv/videos/{_ID1}/counting_animals.mp4",
        "file_size": 45_000_000,   # ~45 MB placeholder
        "mime_type": "video/mp4",
        "uploaded_by": "seed_script",
    },
    {
        "id": _ID2,
        "title": "The Solar System Adventure",
        "description": (
            "Join Bobo on a 3-minute tour of the planets. "
            "Kids learn the names and order of each planet with fun animations."
        ),
        "s3_key": f"bobotv/videos/{_ID2}/solar_system.mp4",
        "file_size": 62_000_000,   # ~62 MB placeholder
        "mime_type": "video/mp4",
        "uploaded_by": "seed_script",
    },
    {
        "id": _ID3,
        "title": "ABC Song — Letters and Sounds",
        "description": (
            "A 3-minute animated alphabet song. Each letter is shown "
            "with a matching picture and phonetic sound. Ages 3–6."
        ),
        "s3_key": f"bobotv/videos/{_ID3}/abc_song.mp4",
        "file_size": 38_000_000,   # ~38 MB placeholder
        "mime_type": "video/mp4",
        "uploaded_by": "seed_script",
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        inserted = 0
        skipped = 0

        for data in DEMO_VIDEOS:
            existing = await db.execute(
                select(BoboTVVideo).where(BoboTVVideo.title == data["title"])
            )
            if existing.scalar_one_or_none():
                print(f"  SKIP  — already exists: {data['title']!r}")
                skipped += 1
                continue

            video = BoboTVVideo(
                id=data["id"],
                title=data["title"],
                description=data["description"],
                s3_key=data["s3_key"],
                file_size=data["file_size"],
                mime_type=data["mime_type"],
                uploaded_by=data["uploaded_by"],
                is_active=True,
                created_at=datetime.now(timezone.utc),
            )
            db.add(video)
            print(f"  INSERT — {data['title']!r}  (id={data['id']})")
            inserted += 1

        await db.commit()
        print(f"\nDone. inserted={inserted}  skipped={skipped}")
        print("\nNext: upload the actual video files to S3 at these keys:")
        for d in DEMO_VIDEOS:
            print(f"  aws s3 cp <your_file.mp4> s3://{settings.AWS_S3_BUCKET_BOBOTV or '<bucket>'}/{d['s3_key']}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
