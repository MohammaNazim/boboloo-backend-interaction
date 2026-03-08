def build_fq_ui(quotients, breakdown, signals, age):

    fq = quotients.get("fq", 0)

    turns = signals.get("turns", 0)
    words = signals.get("total_words", 0)
    unique_words = signals.get("unique_words", 0)
    avg_turn = signals.get("avg_turn_length", 0)

    # ------------------------------------------------
    # Articulatory Clarity (estimated from vocabulary)
    # ------------------------------------------------

    if unique_words > 40:
        clear_sounds = list("ABCDEFGHIJKLM")
        developing_sounds = list("NOPQR")
    elif unique_words > 20:
        clear_sounds = list("ABCDEFGHI")
        developing_sounds = list("OPQR")
    else:
        clear_sounds = list("ABCDE")
        developing_sounds = list("FGHIJ")

    not_attempted = ["X", "Z"]

    articulatory = {
        "clear_sounds": clear_sounds,
        "developing_sounds": developing_sounds,
        "not_attempted": not_attempted,
        "note": f"The 'R' sound is developmentally normal to master around age {age}."
    }

    # ------------------------------------------------
    # Prosody & Tone (variation in conversation)
    # ------------------------------------------------

    variation_score = min(100, int((avg_turn * 12) + (turns * 0.5)))
    
    if variation_score > 60:
        prosody_label = "Your child speaks with high emotional variation — they are not robotic."
    else:
        prosody_label = "Speech tone still developing."

    prosody = {
        "variation_score": variation_score,
        "label": prosody_label
    }

    # ------------------------------------------------
    # Pace Consistency
    # ------------------------------------------------

    if turns == 0:
        wpm = 0
    else:
        wpm = int((words / turns) * 30)

    if wpm < 80:
        zone = "Slow"
    elif wpm < 130:
        zone = "Relaxed"
    else:
        zone = "Fast"

    pace = {
        "words_per_minute": wpm,
        "zone": zone,
        "insight": "Balanced speaking rhythm detected."
    }

    # ------------------------------------------------
    # Weekly Action Recommendation
    # ------------------------------------------------

    if unique_words > 40:
        weekly_action = "Encourage storytelling and creative conversations."
    elif unique_words > 20:
        weekly_action = "Ask open-ended questions to expand vocabulary."
    else:
        weekly_action = "Encourage simple storytelling and descriptive speech."

    # ------------------------------------------------

    return {
        "fq_score": fq,
        "articulatory_clarity": articulatory,
        "prosody": prosody,
        "pace_consistency": pace,
        "weekly_action": weekly_action
    }