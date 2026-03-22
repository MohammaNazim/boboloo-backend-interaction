# =====================================================
# VQ MODEL (DB BASED - FINAL CLEAN VERSION)
# =====================================================

def compute_vq(signals, age=None):

    signals = signals or {}

    # --------------------------------
    # Core signals
    # --------------------------------

    unique_words = signals.get("unique_words", 0)
    content_word_count = signals.get("content_word_count", 0)

    ttr = signals.get("ttr", 0)
    difficulty_score = signals.get("difficulty_score", 0)
    avg_turn_length = signals.get("avg_turn_length", 0)

    confidence = signals.get("confidence", 1)

    # --------------------------------
    # Expressive vs Receptive
    # --------------------------------

    spoken_words = unique_words
    understood_words = int(unique_words * 1.8)

    # --------------------------------
    # Category distribution (safe)
    # --------------------------------

    categories = signals.get("category_distribution") or {
        "noun": 0,
        "verb": 0,
        "social": 0,
    }

    # --------------------------------
    # Novelty (DB injected later)
    # --------------------------------

    new_words_introduced = signals.get("new_words_introduced", 0)
    new_words_reused = signals.get("new_words_reused", 0)

    # --------------------------------
    # Derived metrics (safe guards)
    # --------------------------------

    diversity_score = round((ttr or 0) * 100, 1)
    contextual_usage = round((avg_turn_length or 0) * 10, 1)

    # --------------------------------
    # FINAL RESPONSE
    # --------------------------------

    return {

        # ⚠️ score always comes from batch (DO NOT compute here)
        "score": 0,

        "breakdown": {

            "spoken_words": spoken_words,
            "understood_words": understood_words,

            "category_distribution": categories,

            "new_words_introduced": new_words_introduced,
            "new_words_reused": new_words_reused,

            "content_word_count": content_word_count,
            "unique_words": unique_words,

            "diversity_score": diversity_score,
            "difficulty_score": round(difficulty_score or 0, 2),
            "contextual_usage": contextual_usage,

            "confidence": confidence,
        }
    }