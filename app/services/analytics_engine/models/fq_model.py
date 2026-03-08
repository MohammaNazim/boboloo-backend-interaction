from ..constants import MIN_SCORE, MAX_SCORE


def clamp(value):
    return max(MIN_SCORE, min(MAX_SCORE, round(value, 1)))


def compute_fq(signals):

    # --------------------------------
    # Extract signals safely
    # --------------------------------

    avg_turn_length = signals.get("avg_turn_length", 0)
    turns = signals.get("turns", 0)
    unique_words = signals.get("unique_words", 0)

    # --------------------------------
    # Fluency component
    # Longer sentences → better fluency
    # --------------------------------

    fluency_component = min(100, avg_turn_length * 12)

    # --------------------------------
    # Conversational rhythm
    # More turns → better flow
    # --------------------------------

    rhythm_component = min(100, turns * 2)

    # --------------------------------
    # Vocabulary clarity
    # More unique words → richer speech
    # --------------------------------

    vocab_component = min(100, unique_words * 0.7)

    # --------------------------------
    # Final weighted score
    # --------------------------------

    score = (
        fluency_component * 0.4
        + rhythm_component * 0.3
        + vocab_component * 0.3
    )

    return {
        "score": clamp(score),

        "breakdown": {
            "fluency_component": round(fluency_component, 1),
            "rhythm_component": round(rhythm_component, 1),
            "vocab_component": round(vocab_component, 1),
        }
    }