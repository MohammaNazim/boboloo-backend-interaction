import re
from collections import Counter
from wordfreq import zipf_frequency
from datetime import datetime

# --------------------------------
# Core language patterns
# --------------------------------

QUESTION_PATTERNS = {"why", "how", "what", "where"}

# --------------------------------
# Stop words
# --------------------------------

STOP_WORDS = {
    "the","is","a","to","of","in","it","that",
    "this","on","for","with","as","was","are"
}

# --------------------------------
# Filler words
# --------------------------------

FILLER_WORDS = {
    "um","uh","hmm","like","erm","ah","okay",
    "so","well","you","know","ok",
    "huh","mm","er","ahh","hmmm",
    "uhh","umm","uhhh","ummm"
}

# --------------------------------
# Emotion words
# --------------------------------

EMOTION_WORDS = {
    "happy":{"happy","yay","great","fun","nice"},
    "sad":{"sad","cry","upset"},
    "angry":{"angry","mad"},
    "excited":{"wow","excited","amazing","awesome"},
    "anxious":{"scared","afraid","nervous","worried"}
}

NEGATION_WORDS = {"no","not","don't","can't","won't","never"}

VERB_WORDS = {"run","eat","go","play","jump","come","take","give"}
SOCIAL_WORDS = {"please","bye","hello","thanks","sorry"}


# =====================================================
# ZIPF DIFFICULTY
# =====================================================

def compute_zipf_difficulty(words):

    if not words:
        return 0

    scores = []

    for w in words:
        try:
            zipf = zipf_frequency(w, "en")
            difficulty = 7 - zipf
            scores.append(difficulty)
        except:
            continue

    return sum(scores) / len(scores) if scores else 0


# =====================================================
# PACE
# =====================================================

def classify_pace(wpm):

    if wpm < 40:
        return "stressed"
    elif wpm < 60:
        return "anxious"
    elif wpm < 80:
        return "neutral"
    elif wpm < 100:
        return "relaxed"
    elif wpm < 120:
        return "happy"
    else:
        return "excited"


def pace_text(zone):

    mapping = {
        "excited": "High excitement detected in recent chats.",
        "anxious": "Possible anxiety or rushed responses detected.",
        "relaxed": "Comfortable conversation pace.",
        "neutral": "Balanced speaking rhythm.",
        "happy": "Energetic and engaged conversation.",
    }

    return mapping.get(zone, "Speech pace still stabilizing.")


# =====================================================
# SIGNAL EXTRACTION
# =====================================================

def extract_signals(messages):

    user_msgs = [
        m.get("content", "").lower()
        for m in messages
        if m.get("role", "").lower() == "user"
    ]

    turns = len(user_msgs)

    text = " ".join(user_msgs)
    words = re.findall(r"\b[a-z]+\b", text)

    total_words = len(words)

    # --------------------------------
    # Content words
    # --------------------------------

    content_words = [
        w for w in words
        if w not in STOP_WORDS
        and w not in FILLER_WORDS
        and len(w) > 2
    ]

    content_word_count = len(content_words)
    unique_words = len(set(content_words))

    # --------------------------------
    # Diversity
    # --------------------------------

    ttr = unique_words / max(content_word_count, 1)

    # --------------------------------
    # Repetition
    # --------------------------------

    word_freq = Counter(content_words)

    repeated_tokens = sum((c - 1) for c in word_freq.values() if c > 1)
    repetition_rate = repeated_tokens / max(content_word_count, 1)

    # --------------------------------
    # Disfluency
    # --------------------------------

    filler_count = sum(1 for w in words if w in FILLER_WORDS)
    filler_ratio = filler_count / max(total_words, 1)

    disfluency_score = repetition_rate + filler_ratio

    # --------------------------------
    # Curiosity (FIXED regex)
    # --------------------------------

    curiosity = sum(
        1 for msg in user_msgs
        if "?" in msg or any(
            re.search(rf"\b{q}\b", msg) for q in QUESTION_PATTERNS
        )
    )

    curiosity_ratio = curiosity / max(turns, 1)

    # --------------------------------
    # Sentence stats
    # --------------------------------

    sentence_lengths = [len(msg.split()) for msg in user_msgs]

    avg_turn_length = total_words / max(turns, 1)

    sentence_variance = sum(
        (l - avg_turn_length) ** 2 for l in sentence_lengths
    ) / max(turns, 1)

    # --------------------------------
    # Prosody
    # --------------------------------

    long_turn_ratio = sum(
        1 for l in sentence_lengths if l >= 8
    ) / max(turns, 1)

    punctuation_emphasis = (
        text.count("!") + text.count("?") + text.count("...")
    ) / max(turns, 1)

    normalized_variance = sentence_variance / max(avg_turn_length, 1)

    prosody_score = (
        normalized_variance * 0.5
        + long_turn_ratio * 0.3
        + punctuation_emphasis * 0.2
    )

    prosody_score = max(0, min(prosody_score, 1))

    # --------------------------------
    # Category distribution
    # --------------------------------

    noun_count = verb_count = social_count = 0

    for w in content_words:
        if w in VERB_WORDS:
            verb_count += 1
        elif w in SOCIAL_WORDS:
            social_count += 1
        else:
            noun_count += 1

    category_distribution = {
        "noun": round((noun_count / max(content_word_count, 1)) * 100, 1),
        "verb": round((verb_count / max(content_word_count, 1)) * 100, 1),
        "social": round((social_count / max(content_word_count, 1)) * 100, 1),
    }

    # --------------------------------
    # Emotion
    # --------------------------------

    emotion_scores = {k: 0 for k in EMOTION_WORDS}

    for i, w in enumerate(words):
        for emotion, vocab in EMOTION_WORDS.items():
            if w in vocab:
                emotion_scores[emotion] += 1

    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    if emotion_scores[dominant_emotion] == 0:
        dominant_emotion = "neutral"

    # --------------------------------
    # SAFE WPM
    # --------------------------------

    timestamps = []

    for m in messages:
        try:
            if m.get("role") == "user" and m.get("created_at"):
                timestamps.append(datetime.fromisoformat(m["created_at"]))
        except:
            continue

    if len(timestamps) >= 2:
        duration = (max(timestamps) - min(timestamps)).total_seconds() / 60
        wpm = total_words / duration if duration > 0.1 else avg_turn_length * 6
    else:
        wpm = avg_turn_length * 6

    pace_zone = classify_pace(wpm)
    pace_text_value = pace_text(pace_zone)

    # 🔥 NEW: pace consistency
    if sentence_variance < 5:
        pace_consistency = "stable"
    elif sentence_variance < 15:
        pace_consistency = "slightly_variable"
    else:
        pace_consistency = "inconsistent"

    # --------------------------------
    # Difficulty + confidence
    # --------------------------------

    difficulty_score = compute_zipf_difficulty(content_words)
    confidence = min(1.0, total_words / 50)

    # --------------------------------
    # FINAL OUTPUT
    # --------------------------------

    return {

        "total_words": total_words,
        "content_word_count": content_word_count,
        "unique_words": unique_words,

        "ttr": round(ttr, 3),
        "difficulty_score": round(difficulty_score, 3),
        "confidence": round(confidence, 2),

        "curiosity": curiosity,
        "curiosity_ratio": round(curiosity_ratio, 2),

        "repetition_rate": round(repetition_rate, 3),

        "filler_ratio": round(filler_ratio, 3),
        "disfluency_score": round(disfluency_score, 3),

        "avg_turn_length": round(avg_turn_length, 2),
        "sentence_variance": round(sentence_variance, 2),

        "prosody_score": round(prosody_score, 3),

        "long_turn_ratio": round(long_turn_ratio, 2),

        "turns": turns,
        "category_distribution": category_distribution,

        "words_per_minute": round(wpm, 1),
        "pace_zone": pace_zone,
        "pace_consistency": pace_consistency,
        "pace_text": pace_text_value,

        "emotion": dominant_emotion,

        "content_words_list": content_words
    }