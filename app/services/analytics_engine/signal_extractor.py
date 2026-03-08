import re
from collections import Counter


QUESTION_PATTERNS = {"why", "how", "what", "where"}
SEQUENCE_WORDS = {"then", "after", "because", "and"}

# Topic keywords
TOPIC_MAP = {
    "science": {"why", "how", "sky", "rain", "sun", "bird"},
    "story": {"story", "tale", "character", "dragon"},
    "emotion": {"sad", "happy", "angry", "scared", "love"},
    "learning": {"learn", "teach", "explain", "know"},
}

VERB_WORDS = {"run", "eat", "go", "play", "jump", "come", "take", "give"}
SOCIAL_WORDS = {"please", "bye", "hello", "thanks", "sorry"}


def extract_signals(messages):

    # --------------------------------------------------
    # Extract user messages
    # --------------------------------------------------

    user_msgs = [
        m["content"].lower()
        for m in messages
        if m.get("role", "").lower() == "user"
    ]

    turns = len(user_msgs)

    text = " ".join(user_msgs)

    words = re.findall(r"\b\w+\b", text)

    total_words = len(words)

    unique_words = len(set(words))

    # --------------------------------------------------
    # Curiosity detection (token based)
    # --------------------------------------------------

    curiosity = 0

    for msg in user_msgs:

        tokens = set(msg.split())

        if tokens.intersection(QUESTION_PATTERNS) or "?" in msg:
            curiosity += 1

    curiosity_ratio = curiosity / max(turns, 1)

    # --------------------------------------------------
    # Sequencing detection
    # --------------------------------------------------

    sequencing = sum(
        1 for w in words if w in SEQUENCE_WORDS
    )

    # --------------------------------------------------
    # Vocabulary novelty
    # --------------------------------------------------

    word_freq = Counter(words)

    new_words = len(
        [w for w, c in word_freq.items() if c == 1]
    )

    novelty_ratio = new_words / max(unique_words, 1)

    # --------------------------------------------------
    # Average message length
    # --------------------------------------------------

    if turns == 0:
        avg_turn_length = 0
    else:
        avg_turn_length = total_words / turns

    # --------------------------------------------------
    # Topic detection (faster)
    # --------------------------------------------------

    word_set = set(words)

    topic_scores = {}

    for topic, topic_words in TOPIC_MAP.items():
        topic_scores[topic] = len(
            word_set.intersection(topic_words)
        )

    top_topics = sorted(
        topic_scores,
        key=topic_scores.get,
        reverse=True
    )[:3]

    # --------------------------------------------------
    # Word Category Detection
    # --------------------------------------------------

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

        "noun": round(
            (noun_count / max(total_words, 1)) * 100, 1
        ),

        "verb": round(
            (verb_count / max(total_words, 1)) * 100, 1
        ),

        "social": round(
            (social_count / max(total_words, 1)) * 100, 1
        ),
    }

    # --------------------------------------------------

    return {

        "total_words": total_words,

        "unique_words": unique_words,

        "curiosity": curiosity,

        "curiosity_ratio": round(curiosity_ratio, 2),

        "sequencing": sequencing,

        "novelty_ratio": novelty_ratio,

        "avg_turn_length": avg_turn_length,

        "turns": turns,

        "top_topics": top_topics,

        "category_distribution": category_distribution,
    }