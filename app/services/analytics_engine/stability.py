from .constants import (
    BASELINE_SCORE,
    MIN_SCORE,
    MAX_SCORE,
)


def apply_stability_control(
    raw_scores,
    signals,
    previous_scores=None,
):

    # --------------------------------
    # Safe signal extraction
    # --------------------------------

    turns = signals.get("turns", 0)
    unique_words = signals.get("unique_words", 0)
    avg_turn_length = signals.get("avg_turn_length", 0)

    # --------------------------------
    # Confidence calculation
    # Bound signals to avoid inflation
    # --------------------------------

    volume_score = min(20, turns) * 0.5
    vocab_score = min(30, unique_words) * 0.3
    length_score = min(10, avg_turn_length) * 0.2

    confidence = min(
        1.0,
        (volume_score + vocab_score + length_score) / 60
    )

    # --------------------------------
    # Pull scores toward baseline
    # when confidence is low
    # --------------------------------

    adjusted = {}

    for metric, value in raw_scores.items():

        adjusted_value = (
            BASELINE_SCORE
            + (value - BASELINE_SCORE) * confidence
        )

        adjusted[metric] = adjusted_value

    # --------------------------------
    # Smooth changes vs previous scores
    # --------------------------------

    if previous_scores:

        MAX_STEP = 4

        for metric in adjusted:

            prev = previous_scores.get(metric, BASELINE_SCORE)

            delta = adjusted[metric] - prev

            if delta > MAX_STEP:
                adjusted[metric] = prev + MAX_STEP

            elif delta < -MAX_STEP:
                adjusted[metric] = prev - MAX_STEP

    # --------------------------------
    # Clamp final values
    # --------------------------------

    final_scores = {}

    for metric, value in adjusted.items():

        final_scores[metric] = round(
            max(MIN_SCORE, min(MAX_SCORE, value)),
            1,
        )

    return final_scores, round(confidence, 2)