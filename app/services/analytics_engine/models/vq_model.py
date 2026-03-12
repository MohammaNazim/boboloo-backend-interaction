from ..constants import MIN_SCORE, MAX_SCORE


def clamp(value):
    return max(MIN_SCORE, min(MAX_SCORE, round(value, 1)))


def compute_vq(signals):

    # --------------------------------
    # Extract signals safely
    # --------------------------------

    total_words = signals.get("total_words", 0)
    content_word_count = signals.get("content_word_count", 0)
    unique_words = signals.get("unique_words", 0)

    ttr = signals.get("ttr", 0)
    difficulty_score = signals.get("difficulty_score", 0)

    avg_turn_length = signals.get("avg_turn_length", 0)
    novelty_ratio = signals.get("novelty_ratio", 0)

    repetition_rate = signals.get("repetition_rate", 0)

    confidence = signals.get("confidence", 1)

    # --------------------------------
    # Vocabulary Size Score
    # --------------------------------

    vocab_size_score = min(
        100,
        (unique_words / max(content_word_count, 1)) * 100
    )

    # --------------------------------
    # Vocabulary Diversity Score
    # --------------------------------

    diversity_score = max(0, ttr * 100)

    # --------------------------------
    # Contextual Vocabulary Usage
    # --------------------------------

    contextual_score = min(100, avg_turn_length * 10)

    # --------------------------------
    # Novel word usage
    # --------------------------------

    novelty_score = max(0, novelty_ratio * 100)

    # --------------------------------
    # Vocabulary difficulty
    # --------------------------------

    difficulty_component = min(100, difficulty_score * 15)

    # --------------------------------
    # Repetition penalty
    # --------------------------------

    repetition_penalty = min(30, repetition_rate * 40)

    # --------------------------------
    # Raw vocabulary score
    # --------------------------------

    raw_score = (

        vocab_size_score * 0.30
        + diversity_score * 0.25
        + contextual_score * 0.20
        + novelty_score * 0.15
        + difficulty_component * 0.10

    )

    raw_score -= repetition_penalty

    # --------------------------------
    # Confidence adjustment
    # --------------------------------

    score = raw_score * confidence

    score = clamp(score)

    # --------------------------------
    # Expressive vs Receptive vocabulary
    # --------------------------------

    spoken_words = unique_words
    understood_words = int(unique_words * 1.8)

    # --------------------------------
    # REAL novelty retention (from DB signals)
    # --------------------------------

    new_words_introduced = signals.get("new_words_introduced", 0)
    new_words_reused = signals.get("new_words_reused", 0)

    # --------------------------------
    # Category distribution
    # --------------------------------

    categories = signals.get(
        "category_distribution",
        {"noun": 0, "verb": 0, "social": 0},
    )

    # --------------------------------
    # Final response
    # --------------------------------

    return {

        "score": score,

        "breakdown": {

            "spoken_words": spoken_words,
            "understood_words": understood_words,

            "category_distribution": categories,

            "new_words_introduced": new_words_introduced,
            "new_words_reused": new_words_reused,

            "total_words": total_words,
            "content_word_count": content_word_count,
            "unique_words": unique_words,

            "diversity_score": round(diversity_score, 1),
            "novelty_score": round(novelty_score, 1),
            "difficulty_score": round(difficulty_score, 2),
            "contextual_usage": round(contextual_score, 1),

            "confidence": confidence,
        }
    }