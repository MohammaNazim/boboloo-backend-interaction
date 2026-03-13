from datetime import date
from dateutil.relativedelta import relativedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.database.models import Child, Parent
from app.schemas.child_schema import ChildCreate, ChildUpdate


# ---------------------------------------------------------
# Create Child (ONBOARDING - ONLY ONCE)
# ---------------------------------------------------------
async def create_child(
    db: AsyncSession,
    parent: Parent,
    child_data: ChildCreate,
):
    # Check if parent already has child
    result = await db.execute(
        select(Child).where(Child.parent_id == parent.id)
    )
    existing_child = result.scalars().first()

    if existing_child:
        raise HTTPException(
            status_code=400,
            detail="Parent already has a child",
        )
    birth_date = date.today() - relativedelta(years=child_data.age)

    child = Child(
        parent_id=parent.id,
        name=child_data.name,
        age=child_data.age,
        birth_date=birth_date,
        guardian_name=child_data.guardian_name,
        interests=child_data.interests,
        onboarding_completed=True,
    )

    db.add(child)
    await db.commit()
    await db.refresh(child)

    return child


# ---------------------------------------------------------
# Get Child Profile
# ---------------------------------------------------------
async def get_child(
    db: AsyncSession,
    parent: Parent,
):
    result = await db.execute(
        select(Child).where(Child.parent_id == parent.id)
    )

    child = result.scalars().first()

    if not child:
        raise HTTPException(
            status_code=404,
            detail="Child not found"
        )

    return child


# ---------------------------------------------------------
# Update Child Profile
# ---------------------------------------------------------
async def update_child(
    db: AsyncSession,
    parent: Parent,
    data: ChildUpdate,
):

    result = await db.execute(
        select(Child).where(Child.parent_id == parent.id)
    )
    child = result.scalars().first()

    if not child:
        raise HTTPException(
            status_code=404,
            detail="Child not found"
        )

    # ---- Basic Profile ----
    if data.name is not None:
        child.name = data.name

    if data.age is not None:
        child.age = data.age
        child.birth_date = date.today() - relativedelta(years=data.age)

    if data.guardian_name is not None:
        child.guardian_name = data.guardian_name

    # ---- Preferences ----
    if data.interests is not None:
        child.interests = data.interests

    if data.keywords_filter is not None:
        child.keywords_filter = data.keywords_filter

    if data.focus_topics is not None:
        child.focus_topics = data.focus_topics

    # onboarding complete after preferences
    if (
        data.interests is not None
        or data.keywords_filter is not None
        or data.focus_topics is not None
    ):
        child.onboarding_completed = True

    await db.commit()
    await db.refresh(child)

    return child