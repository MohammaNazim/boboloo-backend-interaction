from ..constants import MIN_SCORE, MAX_SCORE

def clamp(value):
    return max(MIN_SCORE, min(MAX_SCORE, round(value, 1)))

def compute_mq(signals, age):

    sequence_retention = signals.get("sequencing", 0) * 7
    topic_linking = signals.get("unique_words", 0) * 0.3
    recall_consistency = signals.get("turns", 0) * 2.5

    score = (sequence_retention + topic_linking + recall_consistency) / 3

    return {
        "score": clamp(score),
        "breakdown": {
            "sequence_usage": signals["sequencing"],
            "topic_linking_score": round(topic_linking, 1),
        }
    }