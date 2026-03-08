# =====================================================
# MQ PRESENTER (FINAL PRODUCTION SAFE)
# =====================================================

def build_mq_ui(quotients, breakdown, signals):

    # -------------------------------------------------
    # SAFETY GUARDS
    # -------------------------------------------------
    quotients = quotients or {}
    breakdown = breakdown or {}
    signals = signals or {}

    mq = quotients.get("mq", 0)

    level = breakdown.get("instruction_level", 1)
    sequencing = breakdown.get("sequencing_accuracy", 0)
    retention = breakdown.get("retention_score", 50)
    decay = breakdown.get("recall_decay", 0.2)

    # -------------------------------------------------
    # Instruction Capacity
    # -------------------------------------------------
    label_map = {
        1: "Single-Step Commands",
        2: "2-Step Commands",
        3: "Multi-Step Reasoning",
    }

    instructional = {
        "level": level,
        "label": label_map.get(
            level,
            "Emerging Instruction Following"
        ),
        "insight":
            "Instruction-following ability developing through interaction.",
    }

    # -------------------------------------------------
    # Narrative Sequencing
    # -------------------------------------------------
    narrative = {
        "ordering_accuracy": sequencing,
        "insight":
            "Story sequencing ability improving with exposure."
            if sequencing > 0
            else "Narrative sequencing still emerging.",
    }

    # -------------------------------------------------
    # Recall Decay
    # -------------------------------------------------
    short_term = retention
    long_term = max(
        0,
        retention - decay * 100
    )

    recall = {
        "short_term": round(short_term),
        "long_term": round(long_term),
        "interpretation":
            "Healthy memory retention pattern detected."
            if retention > 40
            else "Memory reinforcement recommended.",
    }

    # -------------------------------------------------
    # FINAL RESPONSE
    # -------------------------------------------------
    return {
        "mq_score": mq,
        "instructional_capacity": instructional,
        "narrative_sequencing": narrative,
        "recall_decay": recall,
    }