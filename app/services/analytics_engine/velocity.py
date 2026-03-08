def classify_velocity(prev,current):

    if prev is None:
        return "baseline"

    d=current-prev

    if d>=4:
        return "accelerating"
    if d<=-4:
        return "declining"

    return "stable"