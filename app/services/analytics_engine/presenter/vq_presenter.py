# =====================================================
# VQ PRESENTER (PRODUCTION SAFE + UI READY)
# =====================================================

def build_vq_ui(quotients, breakdown, signals):

    # -------------------------------------------------
    # SAFETY GUARDS
    # -------------------------------------------------

    quotients = quotients or {}
    breakdown = breakdown or {}
    signals = signals or {}

    vq = quotients.get("vq", 0)

    spoken = breakdown.get("spoken_words", 0)
    understood = breakdown.get("understood_words", 0)

    categories = breakdown.get(
        "category_distribution",
        {"noun": 0, "verb": 0, "social": 0}
    )

    introduced = breakdown.get("new_words_introduced", 0)
    reused = breakdown.get("new_words_reused", 0)

    diversity = breakdown.get("diversity_score", 0)
    difficulty = breakdown.get("difficulty_score", 0)
    contextual = breakdown.get("contextual_usage", 0)
    confidence = breakdown.get("confidence", 1)

    content_words = breakdown.get("content_word_count", 0)

    # -------------------------------------------------
    # Retention %
    # -------------------------------------------------

    retention = round((reused / max(introduced, 1)) * 100, 1)

    # -------------------------------------------------
    # Expressive vs Receptive
    # -------------------------------------------------

    expressive_ratio = round(spoken / max(understood, 1), 2)

    expressive = {
        "spoken_words": spoken,
        "understood_words": understood,
        "ratio": expressive_ratio,
    }

    # -------------------------------------------------
    # Doctor Insight
    # -------------------------------------------------

    if understood > spoken * 2:
        doctor_note = (
            "Child understands many more words than they speak. "
            "Expressive vocabulary may expand soon."
        )

    elif spoken > 40:
        doctor_note = (
            "Child demonstrates strong expressive vocabulary development."
        )

    else:
        doctor_note = (
            "Expressive vocabulary is developing steadily."
        )

    # -------------------------------------------------
    # Category Insight
    # -------------------------------------------------

    noun_usage = categories.get("noun", 0)
    verb_usage = categories.get("verb", 0)
    social_usage = categories.get("social", 0)

    if verb_usage < 15:
        category_insight = (
            "Encourage more action-based words (verbs) during play."
        )

    elif noun_usage > 70:
        category_insight = (
            "Conversation relies heavily on nouns. Encourage more actions and interactions."
        )

    elif social_usage < 5:
        category_insight = (
            "Introduce more social interaction words like greetings or thanks."
        )

    else:
        category_insight = (
            "Vocabulary categories appear well balanced."
        )

    # -------------------------------------------------
    # Vocabulary Insights
    # -------------------------------------------------

    if diversity > 60:
        diversity_note = "High vocabulary diversity detected."
    elif diversity > 40:
        diversity_note = "Moderate vocabulary diversity."
    else:
        diversity_note = "Frequent repetition detected in vocabulary."

    if difficulty > 2:
        difficulty_note = "Child is experimenting with advanced vocabulary."
    else:
        difficulty_note = "Vocabulary level appropriate for age and conversation."

    # -------------------------------------------------
    # Conversation Confidence Insight
    # -------------------------------------------------

    if confidence < 0.4:
        confidence_note = "Conversation sample small. Score reliability low."
    elif confidence < 0.7:
        confidence_note = "Moderate conversation sample size."
    else:
        confidence_note = "High confidence conversation analysis."

    # -------------------------------------------------
    # Novelty Retention
    # -------------------------------------------------

    novelty = {
        "new_words": introduced,
        "reused_words": reused,
        "retention_rate": retention,
    }

    # -------------------------------------------------
    # FINAL RESPONSE
    # -------------------------------------------------

    return {

        "vq_score": vq,

        # CARD 1
        "expressive_receptive": expressive,

        # Insight under score
        "doctor_note": doctor_note,

        # CARD 2
        "category_balance": categories,
        "category_insight": category_insight,

        # CARD 3
        "novelty_retention": novelty,

        # Additional metrics
        "vocabulary_metrics": {

            "content_words": content_words,
            "diversity_score": diversity,
            "difficulty_score": difficulty,
            "contextual_usage": contextual,
            "confidence": confidence,

        },

        # App insight section
        "insights": {

            "diversity": diversity_note,
            "difficulty": difficulty_note,
            "confidence": confidence_note,

        }

    }