from ..constants import MIN_SCORE, MAX_SCORE

def clamp(value):
    return max(MIN_SCORE, min(MAX_SCORE, round(value, 1)))

def compute_cq(signals):

    question_drive = signals["curiosity"] * 8
    exploration_depth = signals["turns"] * 2
    why_how_intensity = signals["curiosity"] * 6

    score = (question_drive + exploration_depth + why_how_intensity) / 3

    return {
        "score": clamp(score),
        "breakdown": {
            "questions_asked": signals["curiosity"],
            "exploration_score": round(exploration_depth, 1),
        }
    }