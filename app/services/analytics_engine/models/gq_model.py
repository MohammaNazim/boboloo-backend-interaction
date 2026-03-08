def compute_gq(fq, vq, cq, mq):

    score = (
        fq * 0.3 +
        vq * 0.3 +
        cq * 0.2 +
        mq * 0.2
    )

    return {
        "score": round(score, 1),
        "breakdown": {
            "fluency": fq,
            "vocabulary": vq,
            "curiosity": cq,
            "memory": mq,
        }
    }