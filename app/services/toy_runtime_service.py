from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.database.models import (
    ToyStatus,
    Toy,
    Child,
    Conversation,
    Message,
    InteractionSettings,
)

from app.services.ai.ai_service import AIService


class ToyRuntimeService:

    MAX_QUESTION_LENGTH = 500
    HEARTBEAT_WRITE_INTERVAL = 60

    # =====================================================
    # LOAD INTERACTION SETTINGS
    # =====================================================
    @staticmethod
    async def load_settings(db: AsyncSession, child_id):

        result = await db.execute(
            select(InteractionSettings).where(
                InteractionSettings.child_id == child_id
            )
        )

        settings = result.scalar_one_or_none()

        if not settings:
            return {
                "word_complexity": 3,
                "speech_speed": 2,
                "question_frequency": "balanced",
            }

        return {
            "word_complexity": settings.word_complexity,
            "speech_speed": settings.speech_speed,
            "question_frequency": settings.question_frequency,
        }

    # =====================================================
    # TOY ASK QUESTION
    # =====================================================
    @staticmethod
    async def handle_question(
        *,
        db: AsyncSession,
        toy: Toy,
        question: str,
        battery_level: int | None = None,
        wifi_signal: int | None = None,
    ):

        if toy.status != ToyStatus.ACTIVE:
            raise HTTPException(403, "Toy not active")

        if not question:
            raise HTTPException(400, "Question required")

        question = question.strip()

        if not question or len(question) > ToyRuntimeService.MAX_QUESTION_LENGTH:
            raise HTTPException(400, "Invalid question")

        if not toy.active_child_id:
            raise HTTPException(400, "No active child set")

        # =========================
        # FETCH CHILD
        # =========================
        result = await db.execute(
            select(Child).where(
                Child.id == toy.active_child_id
            )
        )

        child = result.scalar_one_or_none()

        if not child:
            raise HTTPException(404, "Child not found")

        if not child.onboarding_completed:
            raise HTTPException(
                403,
                "Complete onboarding before using toy"
            )

        # =========================
        # LOAD INTERACTION SETTINGS
        # =========================
        settings = await ToyRuntimeService.load_settings(
            db,
            child.id
        )

        today = date.today()
        now = datetime.now(timezone.utc)

        try:

            # =========================
            # UPDATE TOY TELEMETRY
            # =========================
            toy.last_seen = now

            if battery_level is not None:
                toy.battery_level = battery_level

            if wifi_signal is not None:
                toy.wifi_signal = wifi_signal

            # =========================
            # DAILY CONVERSATION
            # =========================
            result = await db.execute(
                select(Conversation).where(
                    Conversation.child_id == child.id,
                    Conversation.conversation_date == today,
                )
            )

            conversation = result.scalar_one_or_none()

            if not conversation:
                conversation = Conversation(
                    child_id=child.id,
                    conversation_date=today,
                    started_at=now,
                    last_activity=now,
                )

                db.add(conversation)
                await db.flush()

            else:
                conversation.last_activity = now

            # =========================
            # USER MESSAGE
            # =========================
            db.add(
                Message(
                    conversation_id=conversation.id,
                    role="user",
                    content=question,
                )
            )

            # =========================
            # LOAD LAST MESSAGES (MEMORY)
            # =========================

            msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(5)
            )

            history = msg_result.scalars().all()

            history_messages = [
            {"role": m.role, "content": m.content}
            for m in reversed(history)
            ]

            # =========================
            # AI RESPONSE
            # =========================
            answer = await AIService.generate_child_reply(
                question=question,
                child_age=child.age,
                interests=child.interests or [],
                settings=settings,
                history=history_messages
            )
    
            # =========================
            # ASSISTANT MESSAGE
            # =========================
            db.add(
                Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=answer,
                )
            )

            await db.commit()

        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to process toy request"
            )

        return {
            "conversation_id": conversation.id,
            "answer": answer,
        }

    # =====================================================
    # HEARTBEAT
    # =====================================================
    @staticmethod
    async def heartbeat(
        *,
        db: AsyncSession,
        toy: Toy,
    ):

        if toy.status != ToyStatus.ACTIVE:
            raise HTTPException(403, "Toy not active")

        now = datetime.now(timezone.utc)

        try:

            if (
                not toy.last_seen
                or (now - toy.last_seen).total_seconds()
                > ToyRuntimeService.HEARTBEAT_WRITE_INTERVAL
            ):
                toy.last_seen = now
                await db.commit()

        except Exception:
            await db.rollback()
            raise HTTPException(
                500,
                "Heartbeat update failed"
            )

        return {"status": "alive"}