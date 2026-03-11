from fastapi import APIRouter, Depends
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.analytics_guard import analytics_ready_guard
from app.database.database import get_db
from app.database.models import AnalyticsHistory

# Presenters
from app.services.analytics_engine.presenter.gq_presenter import build_gq_ui
from app.services.analytics_engine.presenter.fq_presenter import build_fq_ui
from app.services.analytics_engine.presenter.vq_presenter import build_vq_ui
from app.services.analytics_engine.presenter.cq_presenter import build_cq_ui
from app.services.analytics_engine.presenter.mq_presenter import build_mq_ui


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)


# =====================================================
# OVERVIEW
# =====================================================

@router.get("/overview")
async def analytics_overview(
    data: dict = Depends(analytics_ready_guard),
):

    analytics = data["analytics"]

    breakdown = analytics.breakdown_json or {}
    signals = breakdown.get("signals", {})

    # -----------------------------
    # Find weakest metric
    # -----------------------------

    scores = {
        "fq": analytics.fq,
        "vq": analytics.vq,
        "cq": analytics.cq,
        "mq": analytics.mq,
    }

    lowest = min(scores, key=scores.get)

    mapping = {
        "fq": ("PRONUNCIATION", "Unlock 'Sound Explorer' Game"),
        "vq": ("PREPOSITIONS", "Unlock 'Over & Under' Game"),
        "cq": ("QUESTION ASKING", "Unlock 'Curious Cat' Game"),
        "mq": ("MEMORY RECALL", "Unlock 'Story Builder' Game"),
    }

    focus_area, action = mapping.get(
        lowest,
        ("GENERAL DEVELOPMENT", "Play Learning Game"),
    )

    # -----------------------------
    # BOBOLOOP signals
    # -----------------------------

    unique_words = signals.get("unique_words", 0)

    play_quality_change = analytics.trend_percent or 0

    # prevent negative UI values
    play_quality_change = round(play_quality_change, 1)

    # -----------------------------
    # Response
    # -----------------------------

    return {

        "boboloop": {
            "new_words_this_week": unique_words,
            "play_quality_change_percent": play_quality_change,
        },

        "weekly_focus": {
            "focus_area": focus_area,
            "recommended_action": action,
        },

        "velocity": analytics.velocity,
    }

# =====================================================
# GQ DETAIL
# =====================================================

@router.get("/gq")
async def gq_detail(
    data: dict = Depends(analytics_ready_guard),
    db: AsyncSession = Depends(get_db),
    period: str = "3weeks",
):

    child = data["child"]
    analytics = data["analytics"]

    signals = (analytics.breakdown_json or {}).get("signals", {})

    now = datetime.utcnow()

    if period == "3days":
        start_date = now - timedelta(days=3)

    elif period == "week":
        start_date = now - timedelta(days=7)

    elif period == "2weeks":
        start_date = now - timedelta(days=14)

    elif period == "3weeks":
        start_date = now - timedelta(days=21)

    elif period == "month":
        start_date = now - timedelta(days=30)

    else:
        start_date = now - timedelta(days=21)

    result = await db.execute(
        select(AnalyticsHistory)
        .where(
            AnalyticsHistory.child_id == child.id,
            AnalyticsHistory.created_at >= start_date
        )
        .order_by(AnalyticsHistory.created_at.asc())
    )

    rows = list(reversed(result.scalars().all()))
    
    history = []

    for r in rows:

        fq = r.fq
        vq = r.vq
        cq = r.cq
        mq = r.mq

        whole_child_map = {
            "logic": round(mq, 1),
            "language": round((fq + vq) / 2, 1),
            "creativity": round(cq * 0.85, 1),
            "empathy": round(cq * 0.65, 1),
            "focus": round(mq * 1.05, 1),
        }

        history.append({
            "date": r.created_at.isoformat(),
            "whole_child_map": whole_child_map
        })

    response = build_gq_ui(
        quotients={
            "fq": analytics.fq or 0,
            "vq": analytics.vq or 0,
            "cq": analytics.cq or 0,
            "mq": analytics.mq or 0,
            "gq": analytics.gq or 0 ,
        },
        signals=signals,
        age=child.age,
        history=history
    )

    response["period"] = period

    return response



# =====================================================
# FQ DETAIL
# =====================================================

@router.get("/fq")
async def fq_detail(
    data: dict = Depends(analytics_ready_guard),
):

    child = data["child"]
    analytics = data["analytics"]

    breakdown = analytics.breakdown_json or {}

    signals = (breakdown.get("signals") or {})

    return build_fq_ui(
        {"fq": analytics.fq},
        breakdown,
        signals,
        child.age,
    )

# =====================================================
# VQ DETAIL
# =====================================================

@router.get("/vq")
async def vq_detail(
    data: dict = Depends(analytics_ready_guard),
):

    analytics = data["analytics"]

    breakdown = analytics.breakdown_json or {}
    signals = breakdown.get("signals", {})

    return build_vq_ui(
        {"vq": analytics.vq},
        breakdown,
        signals,
    )


# =====================================================
# CQ DETAIL
# =====================================================

@router.get("/cq")
async def cq_detail(
    data: dict = Depends(analytics_ready_guard),
):

    analytics = data["analytics"]

    breakdown = analytics.breakdown_json or {}
    signals = breakdown.get("signals", {})

    return build_cq_ui(
        {"cq": analytics.cq},
        breakdown,
        signals,
    )


# =====================================================
# MQ DETAIL
# =====================================================

@router.get("/mq")
async def mq_detail(
    data: dict = Depends(analytics_ready_guard),
):

    analytics = data["analytics"]

    breakdown = analytics.breakdown_json or {}
    signals = breakdown.get("signals", {})

    return build_mq_ui(
        {"mq": analytics.mq},
        breakdown,
        signals,
    )