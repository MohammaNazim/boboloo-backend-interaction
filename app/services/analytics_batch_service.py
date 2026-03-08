import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select, func

from app.database.database import AsyncSessionLocal
from app.database.models import (
    Child,
    Conversation,
    Message,
    ChildAnalytics,
    AnalyticsHistory,
)

from app.services.analytics_engine.engine import generate_analytics
from app.services.analytics_engine.velocity import classify_velocity
from app.services.analytics_engine.constants import ROLLING_WINDOW_DAYS


# =====================================================
# PROCESS SINGLE CHILD
# =====================================================

async def process_child(child, window_start, now):

    async with AsyncSessionLocal() as db:

        try:

            # ------------------------------------------
            # Count messages
            # ------------------------------------------
            msg_result = await db.execute(
                select(func.count(Message.id))
                .join(
                    Conversation,
                    Message.conversation_id == Conversation.id
                )
                .where(
                    Conversation.child_id == child.id,
                    Message.created_at >= window_start,
                )
            )

            total_messages = msg_result.scalar() or 0

            if total_messages < 5:
                print(f"⚠️ Not enough messages for child {child.id}")
                return


            # ------------------------------------------
            # Fetch messages
            # ------------------------------------------
            messages_result = await db.execute(
                select(Message)
                .join(
                    Conversation,
                    Message.conversation_id == Conversation.id
                )
                .where(
                    Conversation.child_id == child.id,
                    Message.created_at >= window_start,
                )
                .order_by(Message.created_at)
            )

            raw_messages = messages_result.scalars().all()

            formatted_messages = [
                {"role": m.role, "content": m.content}
                for m in raw_messages
            ]


            # ------------------------------------------
            # Previous analytics
            # ------------------------------------------
            prev_result = await db.execute(
                select(ChildAnalytics).where(
                    ChildAnalytics.child_id == child.id
                )
            )

            analytics = prev_result.scalars().first()

            previous_scores = None
            previous_gq = None

            if analytics:
                previous_scores = {
                    "fq": analytics.fq,
                    "vq": analytics.vq,
                    "cq": analytics.cq,
                    "mq": analytics.mq,
                    "gq": analytics.gq,
                }
                previous_gq = analytics.gq


            # ------------------------------------------
            # Run analytics engine
            # ------------------------------------------
            result = generate_analytics(
                messages=formatted_messages,
                age=child.age,
                previous_scores=previous_scores,
            )

            result["signals"]["previous_gq"] = previous_gq

            scores = result["quotients"]
            breakdown = result["breakdown"]
            confidence = result["confidence"]

            trend_percent = 0.0

            if previous_gq is not None:
                trend_percent = round(
                    ((scores["gq"] - previous_gq) / previous_gq) * 100,
                    2,
                )

            velocity = classify_velocity(previous_gq, scores["gq"])


            # ------------------------------------------
            # Create analytics row if not exists
            # ------------------------------------------
            if not analytics:
                analytics = ChildAnalytics(child_id=child.id)
                db.add(analytics)

            analytics.fq = scores["fq"]
            analytics.vq = scores["vq"]
            analytics.cq = scores["cq"]
            analytics.mq = scores["mq"]
            analytics.gq = scores["gq"]

            analytics.velocity = velocity
            analytics.confidence = confidence
            analytics.trend_percent = trend_percent

            analytics.breakdown_json = {
                "breakdown": breakdown,
                "signals": result.get("signals", {}),
            }

            analytics.algorithm_version = result["algorithm_version"]
            analytics.updated_at = now


            # ------------------------------------------
            # Save analytics history
            # ------------------------------------------
            history = AnalyticsHistory(
                child_id=child.id,
                fq=scores["fq"],
                vq=scores["vq"],
                cq=scores["cq"],
                mq=scores["mq"],
                gq=scores["gq"],
            )

            db.add(history)

            await db.commit()

            print(f"✅ Analytics processed child {child.id}")

        except Exception as e:

            await db.rollback()

            print(f"❌ Analytics failed child {child.id}", str(e))


# =====================================================
# MAIN BATCH
# =====================================================

async def run_analytics_batch():

    now = datetime.utcnow()

    window_start = now - timedelta(days=ROLLING_WINDOW_DAYS)

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Child).where(Child.is_deleted == False)
        )

        children = result.scalars().all()

    print(f"🧠 Running analytics for {len(children)} children")

    tasks = [
        process_child(child, window_start, now)
        for child in children
    ]

    await asyncio.gather(*tasks)

    print("✅ Analytics batch completed")


if __name__ == "__main__":
    asyncio.run(run_analytics_batch())