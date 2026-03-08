# =====================================================
# VQ PRESENTER (FINAL PRODUCTION SAFE)
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
        {"noun":0,"verb":0,"social":0}
    )

    introduced = breakdown.get(
        "new_words_introduced",
        0
    )

    reused = breakdown.get(
        "new_words_reused",
        0
    )

    # -------------------------------------------------
    # Retention %
    # -------------------------------------------------
    retention = round(
        (reused / max(introduced, 1)) * 100,
        1
    )

    # -------------------------------------------------
    # Expressive vs Receptive
    # -------------------------------------------------
    expressive = {
        "spoken_words": spoken,
        "understood_words": understood,
        "ratio": round(
            spoken / max(understood, 1),
            2
        ),
    }

    # -------------------------------------------------
    # Doctor Insight
    # -------------------------------------------------
    if understood > spoken * 2:
        doctor_note = (
            "Strong receptive vocabulary detected. "
            "Speech expansion likely soon."
        )
    else:
        doctor_note = (
            "Expressive vocabulary developing steadily."
        )

    # -------------------------------------------------
    # Category Insight
    # -------------------------------------------------
    verb_usage = categories.get("verb", 0)

    if verb_usage < 20:
        category_insight = (
            "Introduce more action-based words "
            "during conversations."
        )
    else:
        category_insight = (
            "Vocabulary categories appear balanced."
        )

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

        "expressive_receptive": expressive,

        "doctor_note": doctor_note,

        "category_balance": categories,

        "category_insight": category_insight,

        "novelty_retention": novelty,
    }