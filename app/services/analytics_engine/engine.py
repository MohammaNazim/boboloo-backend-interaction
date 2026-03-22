from .signal_extractor import extract_signals
from .stability import apply_stability_control
from .constants import ALGORITHM_VERSION

# Metric models
from .models.fq_model import compute_fq
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

    # --------------------------------
    # VQ (STRUCTURE ONLY — DB WILL FILL REAL VALUES)
    # --------------------------------

    vq_data = {
        "score": 0,  # placeholder (REAL VALUE batch se ayega)
        "breakdown": {

            "spoken_words": signals.get("unique_words", 0),
            "understood_words": int(signals.get("unique_words", 0) * 1.8),

            "category_distribution": signals.get("category_distribution", {}),

            # 🔥 FIX: DB overwrite karega (no fake values here)
            "new_words_introduced": 0,
            "new_words_reused": 0,

            "content_word_count": signals.get("content_word_count", 0),
            "unique_words": signals.get("unique_words", 0),

            "diversity_score": round(signals.get("ttr", 0) * 100, 1),
            "difficulty_score": signals.get("difficulty_score", 0),
            "contextual_usage": round(signals.get("avg_turn_length", 0) * 10, 1),

            "confidence": signals.get("confidence", 1),
        }
    }

    cq_data = compute_cq(signals, age)
    mq_data = compute_mq(signals, age)

    # --------------------------------
    # GQ
    # --------------------------------

    gq_data = compute_gq(
        fq_data["score"],
        vq_data["score"],  # अभी 0 (override होगा)
        cq_data["score"],
        mq_data["score"],
    )

    # --------------------------------
    # Raw scores
    # --------------------------------

    raw_scores = {
        "fq": fq_data["score"],
        "vq": vq_data["score"],  # placeholder
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
    # Stability smoothing
    # --------------------------------

    stable_scores, confidence = apply_stability_control(
        raw_scores,
        signals,
        previous_scores,
    )

    # --------------------------------
    # Signal summary (DB store)
    # --------------------------------

    signal_summary = {

        # conversation volume
        "turns": signals.get("turns", 0),
        "total_words": signals.get("total_words", 0),
        "unique_words": signals.get("unique_words", 0),

        # fluency
        "avg_turn_length": signals.get("avg_turn_length", 0),
        "sentence_variance": signals.get("sentence_variance", 0),

        # vocabulary
        "ttr": signals.get("ttr", 0),

        # expressive
        "long_turn_ratio": signals.get("long_turn_ratio", 0),

        # disfluency
        "disfluency_score": signals.get("disfluency_score", 0),

        # curiosity
        "curiosity_ratio": signals.get("curiosity_ratio", 0),

        # pace + emotion
        "words_per_minute": signals.get("words_per_minute", 0),
        "pace_zone": signals.get("pace_zone", "neutral"),
        "pace_consistency": signals.get("pace_consistency", "stable"),
        "emotion": signals.get("emotion", "neutral"),
        "pace_text": signals.get("pace_text", ""),

        # vocabulary memory
        "content_words_list": signals.get("content_words_list", []),
    }

    # --------------------------------
    # Attach signals for presenters
    # --------------------------------

    breakdown["signals"] = signal_summary

    # --------------------------------
    # FINAL RESPONSE
    # --------------------------------

    return {

        "algorithm_version": ALGORITHM_VERSION,

        "quotients": stable_scores,

        "breakdown": breakdown,

        "confidence": confidence,

        "signals": signal_summary,
    }