def build_fq_ui(quotients, breakdown, signals, age):

    quotients = quotients or {}
    breakdown = breakdown or {}
    signals = signals or {}

    fq = quotients.get("fq", 0)

    turns = signals.get("turns", 0)
    total_words = signals.get("total_words", 0)

    ttr = signals.get("ttr", 0)
    variance = signals.get("sentence_variance", 0)
    disfluency = signals.get("disfluency_score", 0)
    long_turn_ratio = signals.get("long_turn_ratio", 0)

    avg_turn = signals.get("avg_turn_length", 0)

    # -----------------------------------------
    # Speech Density (words per turn)
    # -----------------------------------------

    if turns == 0:
        speech_density = 0
    else:
        speech_density = round(total_words / turns, 1)

    # -----------------------------------------
    # Fluency Interpretation
    # -----------------------------------------

    if fq >= 70:
        fluency_level = "Advanced conversational fluency detected."
    elif fq >= 55:
        fluency_level = "Healthy fluency development."
    elif fq >= 40:
        fluency_level = "Fluency emerging with interaction."
    else:
        fluency_level = "Encourage more conversational practice."

    # -----------------------------------------
    # Vocabulary richness insight
    # -----------------------------------------

    if ttr > 0.45:
        vocab_label = "Rich vocabulary diversity."
    elif ttr > 0.30:
        vocab_label = "Balanced vocabulary usage."
    else:
        vocab_label = "Vocabulary range still expanding."

    vocabulary = {
        "type_token_ratio": round(ttr, 2),
        "insight": vocab_label,
    }

    # -----------------------------------------
    # Prosody / Rhythm
    # -----------------------------------------

    if variance > 5:
        prosody_label = "Dynamic sentence rhythm."
    elif variance > 2:
        prosody_label = "Moderate sentence variation."
    else:
        prosody_label = "Speech rhythm still developing."

    prosody = {
        "variation_score": round(variance, 2),
        "label": prosody_label,
    }

    # -----------------------------------------
    # Expressive Speech
    # -----------------------------------------

    expressive = {
        "long_turn_ratio": round(long_turn_ratio, 2),
        "interpretation": (
            "Child frequently produces longer expressive sentences."
            if long_turn_ratio > 0.4
            else "Conversation dominated by shorter responses."
        ),
    }

    # -----------------------------------------
    # Disfluency detection
    # -----------------------------------------

    disfluency_block = {
        "disfluency_score": round(disfluency, 3),
        "interpretation": (
            "Minimal hesitation detected."
            if disfluency < 0.05
            else "Some conversational hesitation observed."
        ),
    }

    # -----------------------------------------
    # Pace / Density
    # -----------------------------------------

    if speech_density < 4:
        pace_zone = "Short replies"
    elif speech_density < 9:
        pace_zone = "Balanced conversation"
    else:
        pace_zone = "Highly expressive dialogue"

    pace = {
        "words_per_turn": speech_density,
        "zone": pace_zone,
    }

    # -----------------------------------------
    # Weekly action
    # -----------------------------------------

    if long_turn_ratio > 0.4:
        weekly_action = "Encourage storytelling and imaginative conversations."
    elif ttr > 0.35:
        weekly_action = "Ask open-ended questions to expand conversation."
    else:
        weekly_action = "Encourage descriptive responses and longer sentences."

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