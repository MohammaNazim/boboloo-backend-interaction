import re
from collections import Counter
from wordfreq import zipf_frequency


# --------------------------------
# Core language patterns
# --------------------------------

QUESTION_PATTERNS = {"why", "how", "what", "where"}
SEQUENCE_WORDS = {"then", "after", "because"}

# --------------------------------
# Stop words
# --------------------------------

STOP_WORDS = {
    "the", "is", "a", "to", "of", "in", "it", "that",
    "this", "on", "for", "with", "as", "was", "are"
}

# --------------------------------
# Filler words
# --------------------------------

FILLER_WORDS = {
    "um", "uh", "hmm", "like", "erm", "ah", "okay",
    "so", "well", "you", "know", "ok",
    "huh", "mm", "er", "ahh", "hmmm",
    "uhh", "umm", "uhhh", "ummm"
}

# --------------------------------
# Topic keywords
# --------------------------------

TOPIC_MAP = {
    "science": {"why", "how", "sky", "rain", "sun", "bird"},
    "story": {"story", "tale", "character", "dragon"},
    "emotion": {"sad", "happy", "angry", "scared", "love"},
    "learning": {"learn", "teach", "explain", "know"},
}

VERB_WORDS = {"run", "eat", "go", "play", "jump", "come", "take", "give"}
SOCIAL_WORDS = {"please", "bye", "hello", "thanks", "sorry"}


# =====================================================
# ZIPF DIFFICULTY CALCULATION
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

    if not scores:
        return 0

    return sum(scores) / len(scores)


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

    content_words = [w for w in words if w not in STOP_WORDS]

    content_word_count = len(content_words)

    unique_words = len(set(content_words))

    # --------------------------------
    # Lexical diversity
    # --------------------------------

    ttr = unique_words / max(content_word_count, 1)

    # --------------------------------
    # Word frequency
    # --------------------------------

    word_freq = Counter(content_words)

    # --------------------------------
    # Vocabulary novelty
    # --------------------------------

    new_words = len([w for w, c in word_freq.items() if c == 1])

    novelty_ratio = new_words / max(unique_words, 1)

    # --------------------------------
    # Repetition detection
    # --------------------------------

    repeated_tokens = sum((c - 1) for c in word_freq.values() if c > 1)

    repetition_rate = repeated_tokens / max(content_word_count, 1)

    # --------------------------------
    # Filler detection
    # --------------------------------

    filler_count = sum(1 for w in words if w in FILLER_WORDS)

    filler_ratio = filler_count / max(total_words, 1)

    disfluency_score = repetition_rate + filler_ratio

    # --------------------------------
    # Curiosity detection
    # --------------------------------

    curiosity = 0

    for msg in user_msgs:

        tokens = set(msg.split())

        if tokens.intersection(QUESTION_PATTERNS) or "?" in msg:
            curiosity += 1

    curiosity_ratio = curiosity / max(turns, 1)

    # --------------------------------
    # Sequencing detection
    # --------------------------------

    sequencing = sum(1 for w in words if w in SEQUENCE_WORDS)

    # --------------------------------
    # Sentence statistics
    # --------------------------------

    sentence_lengths = [len(msg.split()) for msg in user_msgs]

    avg_turn_length = total_words / max(turns, 1)

    mean_len = avg_turn_length

    sentence_variance = sum(
        (l - mean_len) ** 2 for l in sentence_lengths
    ) / max(turns, 1)

    # --------------------------------
    # Long expressive turns
    # --------------------------------

    long_turns = sum(1 for l in sentence_lengths if l >= 8)

    long_turn_ratio = long_turns / max(turns, 1)

    # --------------------------------
    # Topic consistency
    # --------------------------------

    topic_switches = 0

    for i in range(1, len(user_msgs)):

        prev_words = set(user_msgs[i - 1].split())
        curr_words = set(user_msgs[i].split())

        if len(prev_words.intersection(curr_words)) == 0:
            topic_switches += 1

    topic_consistency = 1 - (topic_switches / max(turns - 1, 1))

    # --------------------------------
    # Topic detection
    # --------------------------------

    word_set = set(content_words)

    topic_scores = {}

    for topic, topic_words in TOPIC_MAP.items():
        topic_scores[topic] = len(word_set.intersection(topic_words))

    top_topics = sorted(
        topic_scores,
        key=topic_scores.get,
        reverse=True
    )[:3]

    # --------------------------------
    # Word category distribution
    # --------------------------------

    noun_count = 0
    verb_count = 0
    social_count = 0

    for w in words:

        if w in VERB_WORDS:
            verb_count += 1

        elif w in SOCIAL_WORDS:
            social_count += 1

        else:
            noun_count += 1

    category_distribution = {

        "noun": round((noun_count / max(total_words, 1)) * 100, 1),
        "verb": round((verb_count / max(total_words, 1)) * 100, 1),
        "social": round((social_count / max(total_words, 1)) * 100, 1),

    }

    # --------------------------------
    # Zipf difficulty
    # --------------------------------

    difficulty_score = compute_zipf_difficulty(content_words)

    # --------------------------------
    # Conversation confidence
    # --------------------------------

    confidence = min(1.0, total_words / 50)

    # --------------------------------
    # Final signals
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

        "sequencing": sequencing,

        "novelty_ratio": round(novelty_ratio, 3),
        "repetition_rate": round(repetition_rate, 3),

        "filler_ratio": round(filler_ratio, 3),
        "disfluency_score": round(disfluency_score, 3),

        "avg_turn_length": round(avg_turn_length, 2),
        "sentence_variance": round(sentence_variance, 2),

        "long_turn_ratio": round(long_turn_ratio, 2),
        "topic_consistency": round(topic_consistency, 2),

        "turns": turns,

        "top_topics": top_topics,

        "category_distribution": category_distribution,

        # IMPORTANT FOR VOCAB MEMORY
        "content_words_list": content_words,
    }