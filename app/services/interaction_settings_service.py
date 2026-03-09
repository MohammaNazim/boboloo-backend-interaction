from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.models import InteractionSettings


# =========================
# GET SETTINGS
# =========================
async def get_interaction_settings(
    db: AsyncSession,
    child_id: UUID,
):

    result = await db.execute(
        select(InteractionSettings).where(
            InteractionSettings.child_id == child_id
        )
    )

    return result.scalar_one_or_none()


# =========================
# UPDATE SETTINGS
# =========================
async def update_interaction_settings(
    db: AsyncSession,
    child_id: UUID,
    payload,
):

    result = await db.execute(
        select(InteractionSettings).where(
            InteractionSettings.child_id == child_id
        )
    )

    settings = result.scalar_one_or_none()

    if not settings:
        settings = InteractionSettings(child_id=child_id)
        db.add(settings)

    for key, value in payload.model_dump().items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    return settings
