from ..constants import MIN_SCORE, MAX_SCORE, BASELINE_SCORE


def clamp(value):
    return max(MIN_SCORE, min(MAX_SCORE, round(value, 1)))


# --------------------------------
# Expected sentence complexity by age
# --------------------------------

EXPECTED_MLU = {
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
}


def compute_fq(signals, age):

    # --------------------------------
    # Safe signal extraction
    # --------------------------------

    turns = signals.get("turns", 0)
    total_words = signals.get("total_words", 0)

    ttr = signals.get("ttr", 0)
    variance = signals.get("sentence_variance", 0)

    disfluency = signals.get("disfluency_score", 0)
    long_turn_ratio = signals.get("long_turn_ratio", 0)

    topic_consistency = signals.get("topic_consistency", 0)

    avg_turn_length = signals.get("avg_turn_length", 0)

    # --------------------------------
    # Minimum conversation threshold
    # --------------------------------

    if turns < 4 or total_words < 25:

        return {
            "score": clamp(BASELINE_SCORE),
            "breakdown": {
                "note": "Insufficient conversation data for reliable fluency analysis"
            }
        }

    # --------------------------------
    # Derived metrics
    # --------------------------------

    mlu = avg_turn_length

    speech_density = total_words / max(turns, 1)

    # --------------------------------
    # Age normalized complexity
    # --------------------------------

    expected = EXPECTED_MLU.get(age, 7)

    complexity_ratio = mlu / max(expected, 1)

    complexity_score = min(100, complexity_ratio * 50)

    # --------------------------------
    # Component scores
    # --------------------------------

    lexical_score = min(100, ttr * 200)

    rate_score = min(100, speech_density * 6)

    engagement_score = min(100, turns * 3)

    prosody_raw = signals.get("prosody_score", 0)
    prosody_score = min(100, prosody_raw * 80)
    
    expressive_score = min(100, long_turn_ratio * 100)

    coherence_score = min(100, topic_consistency * 100)

    disfluency_penalty = min(30, disfluency * 40)
    # --------------------------------
    # Raw weighted score
    # --------------------------------

    raw_score = (
        lexical_score * 0.22
        + complexity_score * 0.18
        + rate_score * 0.15
        + engagement_score * 0.15
        + prosody_score * 0.10
        + expressive_score * 0.10
        + coherence_score * 0.10
        - disfluency_penalty
    )

    # --------------------------------
    # Volume normalization
    # --------------------------------

    volume = total_words + turns

    volume_factor = min(1.0, volume / 120)

    score = (
        raw_score * volume_factor
        + BASELINE_SCORE * (1 - volume_factor)
    )

    return {

        "score": clamp(score),

        "breakdown": {

            "lexical_diversity": round(lexical_score, 1),

            "age_normalized_complexity": round(complexity_score, 1),

            "speech_density": round(rate_score, 1),

            "engagement": round(engagement_score, 1),

            "prosody": round(prosody_score, 1),

            "expressive_turns": round(expressive_score, 1),

            "conversation_coherence": round(coherence_score, 1),

            "disfluency_penalty": round(disfluency_penalty, 2),

            "volume_factor": round(volume_factor, 2),
        }
    }