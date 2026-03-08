from fastapi import APIRouter, Depends

from app.auth.analytics_guard import analytics_ready_guard

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
):

    child = data["child"]
    analytics = data["analytics"]

    signals = (analytics.breakdown_json or {}).get("signals", {})

    return build_gq_ui(
        quotients={
            "fq": analytics.fq,
            "vq": analytics.vq,
            "cq": analytics.cq,
            "mq": analytics.mq,
            "gq": analytics.gq,
        },
        signals=signals,
        age=child.age,
    )


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
    signals = breakdown.get("signals", {})

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