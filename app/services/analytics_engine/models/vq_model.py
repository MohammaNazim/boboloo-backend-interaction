from ..constants import MIN_SCORE, MAX_SCORE


def clamp(value):
    return max(MIN_SCORE, min(MAX_SCORE, round(value, 1)))


def compute_vq(signals):

    # --------------------------------
    # Extract signals safely
    # --------------------------------

    total_words = signals.get("total_words", 0)
    unique_words = signals.get("unique_words", 0)
    avg_turn_length = signals.get("avg_turn_length", 0)
    novelty_ratio = signals.get("novelty_ratio", 0)

    # --------------------------------
    # Lexical diversity
    # --------------------------------

    lexical_diversity = novelty_ratio * 100

    # --------------------------------
    # Expressive vocabulary range
    # Normalize by total words
    # --------------------------------

    if total_words == 0:
        expressive_range = 0
    else:
        vocab_density = unique_words / total_words
        expressive_range = min(100, vocab_density * 100)

    # --------------------------------
    # Contextual usage
    # Sentence richness
    # --------------------------------

    contextual_usage = min(100, avg_turn_length * 8)

    # --------------------------------
    # Final score
    # --------------------------------

    score = (
        lexical_diversity * 0.4
        + expressive_range * 0.35
        + contextual_usage * 0.25
    )

    # --------------------------------
    # Expressive vs Receptive
    # --------------------------------

    spoken_words = unique_words

    # more realistic receptive estimate
    understood_words = int(unique_words * 1.8)

    # --------------------------------
    # Novel words
    # --------------------------------

    new_words_introduced = int(unique_words * 0.2)
    new_words_reused = int(new_words_introduced * 0.7)

    # --------------------------------
    # Category distribution
    # --------------------------------

    categories = signals.get(
        "category_distribution",
        {"noun": 0, "verb": 0, "social": 0},
    )

    return {

        "score": clamp(score),

        "breakdown": {

            "spoken_words": spoken_words,

            "understood_words": understood_words,

            "category_distribution": categories,

            "new_words_introduced": new_words_introduced,

            "new_words_reused": new_words_reused,

            "total_words": total_words,

            "unique_words": unique_words,

            "lexical_diversity": round(lexical_diversity, 1),
        }
    }