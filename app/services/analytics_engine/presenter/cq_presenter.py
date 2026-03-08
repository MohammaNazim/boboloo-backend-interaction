# =====================================================
# CQ PRESENTER (FINAL PRODUCTION SAFE)
# =====================================================

def build_cq_ui(quotients, breakdown, signals):

    # -------------------------------------------------
    # SAFETY GUARDS
    # -------------------------------------------------
    quotients = quotients or {}
    breakdown = breakdown or {}
    signals = signals or {}

    cq = quotients.get("cq", 0)

    response_time = breakdown.get("response_time", 2.5)
    curiosity = breakdown.get("curiosity_index", 0)
    topic_focus = breakdown.get("topic_focus", 0)

    questions = signals.get("questions", 0)

    # -------------------------------------------------
    # Turn Taking Analysis
    # -------------------------------------------------
    if response_time < 1.5:
        benchmark = "Perfect Social Rhythm"
        insight = "Fast conversational response detected."
    elif response_time < 3:
        benchmark = "Thoughtful Response"
        insight = "Child responds with processing time."
    else:
        benchmark = "Slow Engagement"
        insight = "Encourage conversational prompting."

    turn_taking = {
        "avg_response_time": response_time,
        "benchmark": benchmark,
        "insight": insight,
    }

    # -------------------------------------------------
    # Curiosity Index
    # -------------------------------------------------
    curiosity_block = {
        "questions_asked": questions,
        "curiosity_score": curiosity,
        "top_type": "Why" if questions > 0 else "Exploration",
        "insight":
            "Shows curiosity-driven interaction."
            if questions > 0
            else "More exploratory dialogue recommended.",
    }

    # -------------------------------------------------
    # Topic Focus
    # -------------------------------------------------
    topic_block = {
        "focus_turns": topic_focus,
        "explanation":
            f"Child maintains topic for "
            f"{topic_focus} conversational exchanges."
            if topic_focus > 0
            else "Topic stability still developing.",
    }

    # -------------------------------------------------
    # FINAL RESPONSE
    # -------------------------------------------------
    return {
        "cq_score": cq,
        "turn_taking": turn_taking,
        "curiosity_index": curiosity_block,
        "topic_focus": topic_block,
    }