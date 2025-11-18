def classify_triple(triple):
    topic_markers = ["is", "was", "are", "has", "have", "created", "developed"]
    subj, pred, obj = triple
    if pred.lower() in topic_markers:
        return "topic_marker"
    return "common"

def classify_triples(triples):
    return [(t, classify_triple(t)) for t in triples]
