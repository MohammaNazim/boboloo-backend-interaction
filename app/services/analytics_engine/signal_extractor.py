import re
from collections import Counter


QUESTION_PATTERNS = {"why", "how", "what", "where"}
SEQUENCE_WORDS = {"then", "after", "because", "and"}

FILLER_WORDS = {
    "um", "uh", "hmm", "like", "erm", "ah", "okay","so", "well", "you know","ok","huh", "mm", "huh", "er", "ahh", "hmmm", "uhh", "ummm",
    "huh", "ermm", "ahhh", "hmmmm", "uhhh", "ummmm"
}

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
    # Lexical Diversity
    # --------------------------------------------------

    ttr = unique_words / max(total_words, 1)

    # --------------------------------------------------
    # Curiosity detection
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
    # Repetition detection (disfluency)
    # --------------------------------------------------

    repeated_words = sum(
        c for c in word_freq.values() if c > 2
    )

    repetition_rate = repeated_words / max(total_words, 1)

    # --------------------------------------------------
    # Filler detection (disfluency)
    # --------------------------------------------------

    filler_count = sum(
        1 for w in words if w in FILLER_WORDS
    )

    filler_ratio = filler_count / max(total_words, 1)

    # --------------------------------------------------
    # Combined disfluency signal
    # --------------------------------------------------

    disfluency_score = repetition_rate + filler_ratio

    # --------------------------------------------------
    # Sentence lengths
    # --------------------------------------------------

    sentence_lengths = [
        len(msg.split()) for msg in user_msgs
    ]

    if turns == 0:

        avg_turn_length = 0
        avg_sentence_length = 0
        sentence_variance = 0

    else:

        avg_turn_length = total_words / turns
        avg_sentence_length = avg_turn_length

        mean_len = avg_turn_length

        sentence_variance = sum(
            (l - mean_len) ** 2 for l in sentence_lengths
        ) / max(turns, 1)

    # --------------------------------------------------
    # Long turn ratio (expressive speech)
    # --------------------------------------------------

    long_turns = sum(
        1 for l in sentence_lengths if l >= 8
    )

    long_turn_ratio = long_turns / max(turns, 1)

    # --------------------------------------------------
    # Topic coherence detection (NEW SIGNAL)
    # --------------------------------------------------

    topic_switches = 0

    for i in range(1, len(user_msgs)):

        prev_words = set(user_msgs[i-1].split())
        curr_words = set(user_msgs[i].split())

        if len(prev_words.intersection(curr_words)) == 0:
            topic_switches += 1

    topic_consistency = 1 - (topic_switches / max(turns - 1, 1))

    # --------------------------------------------------
    # Topic detection
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

        "ttr": round(ttr, 3),

        "curiosity": curiosity,

        "curiosity_ratio": round(curiosity_ratio, 2),

        "sequencing": sequencing,

        "novelty_ratio": novelty_ratio,

        "repetition_rate": round(repetition_rate, 3),

        "filler_ratio": round(filler_ratio, 3),

        "disfluency_score": round(disfluency_score, 3),

        "avg_turn_length": avg_turn_length,

        "avg_sentence_length": avg_sentence_length,

        "sentence_variance": round(sentence_variance, 2),

        "long_turn_ratio": round(long_turn_ratio, 2),

        "topic_consistency": round(topic_consistency, 2),

        "turns": turns,

        "top_topics": top_topics,

        "category_distribution": category_distribution,
    }