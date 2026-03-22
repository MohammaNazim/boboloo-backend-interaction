def build_fq_ui(quotients, breakdown, signals, age):

    quotients = quotients or {}
    breakdown = breakdown or {}
    signals = signals or {}

    fq = round(quotients.get("fq", 0), 1)

    turns = signals.get("turns", 0)
    total_words = signals.get("total_words", 0)

    ttr = signals.get("ttr", 0)
    prosody_score = signals.get("prosody_score", 0)
    disfluency = signals.get("disfluency_score", 0)
    long_turn_ratio = signals.get("long_turn_ratio", 0)

    avg_turn = signals.get("avg_turn_length", 0)

    # -----------------------------------------
    # Speech Density
    # -----------------------------------------

    speech_density = round(avg_turn, 1) if turns > 0 else 0

    # -----------------------------------------
    # Fluency Level (SMOOTHED)
    # -----------------------------------------

    if fq >= 75:
        fluency_level = "Advanced conversational fluency detected."
    elif fq >= 60:
        fluency_level = "Healthy and confident fluency development."
    elif fq >= 45:
        fluency_level = "Fluency emerging with interaction."
    else:
        fluency_level = "Encourage more conversational practice."

    # -----------------------------------------
    # Vocabulary richness (BALANCED)
    # -----------------------------------------

    if ttr > 0.5:
        vocab_label = "Rich and varied vocabulary usage."
    elif ttr > 0.35:
        vocab_label = "Balanced vocabulary usage."
    else:
        vocab_label = "Vocabulary range still expanding."

    vocabulary = {
        "type_token_ratio": round(ttr, 2),
        "insight": vocab_label,
    }

    # -----------------------------------------
    # Prosody / Rhythm (TUNED)
    # -----------------------------------------

    if prosody_score > 0.7:
        prosody_label = "Highly expressive speech rhythm."
    elif prosody_score > 0.35:
        prosody_label = "Moderate sentence variation."
    else:
        prosody_label = "Speech rhythm still developing."

    prosody = {
        "variation_score": round(prosody_score, 2),
        "label": prosody_label,
    }

    # -----------------------------------------
    # Expressive Speech (IMPROVED)
    # -----------------------------------------

    if long_turn_ratio > 0.5:
        expressive_text = "Child frequently uses detailed and expressive sentences."
    elif long_turn_ratio > 0.25:
        expressive_text = "Child is beginning to form longer responses."
    else:
        expressive_text = "Conversation dominated by shorter responses."

    expressive = {
        "long_turn_ratio": round(long_turn_ratio, 2),
        "interpretation": expressive_text,
    }

    # -----------------------------------------
    # Disfluency (LESS HARSH)
    # -----------------------------------------

    if disfluency < 0.04:
        disfluency_text = "Smooth and fluent speech."
    elif disfluency < 0.08:
        disfluency_text = "Minor hesitation observed."
    else:
        disfluency_text = "Noticeable hesitation in speech."

    disfluency_block = {
        "disfluency_score": round(disfluency, 3),
        "interpretation": disfluency_text,
    }

    # -----------------------------------------
    # Pace (MORE NATURAL)
    # -----------------------------------------

    if speech_density < 4:
        pace_zone = "Short responses"
    elif speech_density < 8:
        pace_zone = "Balanced conversation"
    else:
        pace_zone = "Expressive conversation"

    pace = {
        "words_per_turn": speech_density,
        "zone": pace_zone,
    }

    # -----------------------------------------
    # Weekly recommendation (SMARTER)
    # -----------------------------------------

    if long_turn_ratio > 0.5:
        weekly_action = "Encourage storytelling and imaginative play."
    elif ttr > 0.4:
        weekly_action = "Ask open-ended questions to deepen conversations."
    else:
        weekly_action = "Encourage longer and more descriptive responses."

    # -----------------------------------------
    # Final response
    # -----------------------------------------

    return {

        "fq_score": fq,

        "fluency_level": fluency_level,

        "vocabulary": vocabulary,

        "prosody": prosody,

        "expressive_speech": expressive,

        "disfluency": disfluency_block,

        "conversation_pace": pace,

        "weekly_action": weekly_action,
    }