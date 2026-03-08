from ..constants import MIN_SCORE, MAX_SCORE

def clamp(value):
    return max(MIN_SCORE, min(MAX_SCORE, round(value, 1)))

def compute_mq(signals):

    sequence_retention = signals["sequencing"] * 7
    topic_linking = signals["unique_words"] * 0.3
    recall_consistency = signals["turns"] * 2.5

    score = (sequence_retention + topic_linking + recall_consistency) / 3

    return {
        "score": clamp(score),
        "breakdown": {
            "sequence_usage": signals["sequencing"],
            "topic_linking_score": round(topic_linking, 1),
        }
    }