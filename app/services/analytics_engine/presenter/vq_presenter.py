# =====================================================
# VQ PRESENTER (FINAL PRODUCTION READY)
# =====================================================

def build_vq_ui(quotients, breakdown, signals):

    quotients = quotients or {}
    breakdown = breakdown or {}
    signals = signals or {}

    # -----------------------------
    # Core values
    # -----------------------------

    vq = quotients.get("vq", 0)

    spoken = breakdown.get("spoken_words", 0)
    understood = breakdown.get("understood_words", 0)

    categories = breakdown.get("category_distribution") or {
        "noun": 0,
        "verb": 0,
        "social": 0
    }

    introduced = breakdown.get("new_words_introduced", 0)
    reused = breakdown.get("new_words_reused", 0)

    diversity = breakdown.get("diversity_score", 0)
    difficulty = breakdown.get("difficulty_score", 0)
    contextual = breakdown.get("contextual_usage", 0)
    confidence = breakdown.get("confidence", 1)

    content_words = breakdown.get("content_word_count", 0)

    # -----------------------------
    # Retention % (SAFE)
    # -----------------------------

    retention = round((reused / introduced) * 100, 1) if introduced > 0 else 0

    # -----------------------------
    # Expressive vs Receptive (SAFE)
    # -----------------------------

    expressive_ratio = round(spoken / understood, 2) if understood > 0 else 0

    expressive = {
        "spoken_words": spoken,
        "understood_words": understood,
        "ratio": expressive_ratio,
    }

    # -----------------------------
    # Doctor Insight
    # -----------------------------

    if understood > spoken * 2:
        doctor_note = "Child understands more words than they speak. Expression growth expected."
    elif spoken > 40:
        doctor_note = "Strong expressive vocabulary development."
    else:
        doctor_note = "Vocabulary is developing steadily."

    # -----------------------------
    # Category Insight (SAFE)
    # -----------------------------

    noun_usage = categories.get("noun", 0)
    verb_usage = categories.get("verb", 0)
    social_usage = categories.get("social", 0)

    if verb_usage < 15:
        category_insight = "Encourage more action words (verbs)."
    elif noun_usage > 70:
        category_insight = "Heavy noun usage. Encourage actions."
    elif social_usage < 5:
        category_insight = "Encourage social words like hello, thanks."
    else:
        category_insight = "Vocabulary categories are well balanced."

    # -----------------------------
    # Insights
    # -----------------------------

    diversity_note = (
        "High vocabulary diversity."
        if diversity > 60 else
        "Moderate vocabulary diversity."
        if diversity > 40 else
        "Repetition observed in vocabulary."
    )

    difficulty_note = (
        "Using advanced vocabulary."
        if difficulty > 2 else
        "Vocabulary level appropriate."
    )

    confidence_note = (
        "Low confidence (less data)."
        if confidence < 0.4 else
        "Moderate confidence."
        if confidence < 0.7 else
        "High confidence analysis."
    )

    # -----------------------------
    # Novelty
    # -----------------------------

    novelty = {
        "new_words": introduced,
        "reused_words": reused,
        "retention_rate": retention,
    }

    # -----------------------------
    # GRAPH + % (SAFE)
    # -----------------------------

    graph_data = signals.get("vq_graph") or []
    percent_change = signals.get("vq_percent_change", 0)
    insight_text = signals.get("vq_insight_text", "")

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------

    return {

        "vq_score": vq,

        # GRAPH SECTION (UI USE करेगा)
        "graph": {
            "data": graph_data,
            "percent_change": percent_change,
            "insight_text": insight_text,
        },

        # CARD 1
        "expressive_receptive": expressive,
        "doctor_note": doctor_note,

        # CARD 2
        "category_balance": categories,
        "category_insight": category_insight,

        # CARD 3
        "novelty_retention": novelty,

        # Metrics
        "vocabulary_metrics": {
            "content_words": content_words,
            "diversity_score": diversity,
            "difficulty_score": difficulty,
            "contextual_usage": contextual,
            "confidence": confidence,
        },

        # Insights
        "insights": {
            "diversity": diversity_note,
            "difficulty": difficulty_note,
            "confidence": confidence_note,
        }
    }