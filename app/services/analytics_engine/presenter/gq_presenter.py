# app/services/analytics_engine/presenter/gq_presenter.py

def build_gq_ui(quotients, signals, age, history=None):

    quotients = quotients or {}
    signals = signals or {}
    history = history or []

    fq = quotients.get("fq", 0)
    vq = quotients.get("vq", 0)
    cq = quotients.get("cq", 0)
    mq = quotients.get("mq", 0)
    gq = quotients.get("gq", 0)

    # -------------------------------
    # Whole Child Map (Radar)
    # -------------------------------

    whole_child_map = {
        "logic": round(mq, 1),
        "language": round((fq + vq) / 2, 1),
        "creativity": round(cq * 0.85, 1),
        "empathy": round(cq * 0.65, 1),
        "focus": round(mq * 1.05, 1),
    }

    # -------------------------------
    # Development Age
    # -------------------------------

    current_age_months = age * 12

    developmental_age_months = max(
        0,
        current_age_months + int((gq - 50) / 4)
    )

    development = {
        "current_age_months": current_age_months,
        "developmental_age_months": developmental_age_months,
        "status": (
            "ahead"
            if developmental_age_months > current_age_months
            else "on_track"
        ),
    }

    # -------------------------------
    # Milestone pacing
    # -------------------------------

    if gq >= 60:
        milestone_pacing = "Tracking slightly ahead in language skills."
    elif gq >= 45:
        milestone_pacing = "Development progressing on track."
    else:
        milestone_pacing = "Additional guided interaction recommended."

    # -------------------------------
    # Velocity
    # -------------------------------

    previous_gq = signals.get("previous_gq")

    previous_growth_rate = None
    growth_rate = 0
    label = "Stable Growth"

    if previous_gq is not None:

        growth_rate = round(gq - previous_gq, 2)
        previous_growth_rate = previous_gq

        if growth_rate > 3:
            label = "Learning Spurt"
        elif growth_rate < -3:
            label = "Temporary Dip"

    velocity = {
        "growth_rate": growth_rate,
        "previous_growth_rate": previous_growth_rate,
        "label": label,
    }

    # -------------------------------
    # Curiosity + Topics
    # -------------------------------

    curiosity_ratio = signals.get("curiosity_ratio", 0)

    if curiosity_ratio > 0.6:
        curiosity_level = "High"
    elif curiosity_ratio > 0.3:
        curiosity_level = "Moderate"
    else:
        curiosity_level = "Emerging"

    learning_profile = {
        "curiosity_ratio": curiosity_ratio,
        "curiosity_level": curiosity_level,
        "top_topics": signals.get("top_topics", []),
    }

    # -------------------------------
    # Insight
    # -------------------------------

    if cq > fq:
        insight = "Your child leans towards Creativity and Empathy this month."
    else:
        insight = "Your child shows strong structured learning this month."

    # -------------------------------
    # Final Response
    # -------------------------------

    return {
        "gq_score": gq,
        "whole_child_map": whole_child_map,
        "child_map_insight": insight,
        "development": development,
        "milestone_pacing": milestone_pacing,
        "velocity": velocity,
        "learning_profile": learning_profile,
        "history": history,  # graph data
    }