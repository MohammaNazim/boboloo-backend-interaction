from .signal_extractor import extract_signals
from .stability import apply_stability_control
from .constants import ALGORITHM_VERSION

# Metric models
from .models.fq_model import compute_fq
from .models.vq_model import compute_vq
from .models.cq_model import compute_cq
from .models.mq_model import compute_mq
from .models.gq_model import compute_gq


def generate_analytics(
    messages,
    age,
    previous_scores=None,
):

    # --------------------------------
    # Extract signals
    # --------------------------------

    signals = extract_signals(messages)

    # --------------------------------
    # Compute metric models
    # --------------------------------

    fq_data = compute_fq(signals, age)
    vq_data = compute_vq(signals, age)
    cq_data = compute_cq(signals, age)
    mq_data = compute_mq(signals, age)

    gq_data = compute_gq(
        fq_data["score"],
        vq_data["score"],
        cq_data["score"],
        mq_data["score"],
    )

    # --------------------------------
    # Raw scores
    # --------------------------------

    raw_scores = {
        "fq": fq_data["score"],
        "vq": vq_data["score"],
        "cq": cq_data["score"],
        "mq": mq_data["score"],
        "gq": gq_data["score"],
    }

    # --------------------------------
    # Breakdown structure
    # --------------------------------

    breakdown = {
        "fq": fq_data.get("breakdown", {}),
        "vq": vq_data.get("breakdown", {}),
        "cq": cq_data.get("breakdown", {}),
        "mq": mq_data.get("breakdown", {}),
        "gq": gq_data.get("breakdown", {}),
    }

    # --------------------------------
    # Apply stability smoothing
    # --------------------------------

    stable_scores, confidence = apply_stability_control(
        raw_scores,
        signals,
        previous_scores,
    )

    # --------------------------------
    # Prepare signal subset for DB
    # --------------------------------

    signal_summary = {

        # conversation volume
        "turns": signals.get("turns", 0),
        "total_words": signals.get("total_words", 0),
        "unique_words": signals.get("unique_words", 0),

        # fluency structure
        "avg_turn_length": signals.get("avg_turn_length", 0),
        "sentence_variance": signals.get("sentence_variance", 0),

        # vocabulary richness
        "ttr": signals.get("ttr", 0),

        # expressive conversation
        "long_turn_ratio": signals.get("long_turn_ratio", 0),

        # hesitation detection
        "disfluency_score": signals.get("disfluency_score", 0),

        # curiosity
        "curiosity_ratio": signals.get("curiosity_ratio", 0),

        # topics
        "top_topics": signals.get("top_topics", []),

        "content_words_list": signals.get("content_words_list", []),
    }

    # --------------------------------
    # Attach signals for presenters
    # --------------------------------

    breakdown["signals"] = signal_summary

    # --------------------------------
    # Final response
    # --------------------------------

    return {

        "algorithm_version": ALGORITHM_VERSION,

        "quotients": stable_scores,

        "breakdown": breakdown,

        "confidence": confidence,

        "signals": signal_summary,
    }