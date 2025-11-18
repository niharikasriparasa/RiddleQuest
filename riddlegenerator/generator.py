import random

def generate_riddle(triples_classified, riddle_type="easy"):
    topic_triples = [t for t, cls in triples_classified if cls == "topic_marker"]
    common_triples = [t for t, cls in triples_classified if cls == "common"]

    if not topic_triples:
        topic_triples = common_triples

    if riddle_type == "easy":
        triple = random.choice(topic_triples)
        return f"I am {triple[1]} {triple[2]}. Who am I?"
    
    elif riddle_type == "v2":
        if not common_triples:
            common_triples = topic_triples
        triple1 = random.choice(topic_triples)
        triple2 = random.choice(common_triples)
        return f"I am {triple1[1]} {triple1[2]} and {triple2[1]} {triple2[2]}. Who am I?"

    elif riddle_type == "v3":
        all_triples = topic_triples + common_triples
        clues = random.sample(all_triples, min(3, len(all_triples)))
        clue_text = "; ".join([f"{t[1]} {t[2]}" for t in clues])
        return f"Here are some clues: {clue_text}. Who am I?"
    
    else:
        raise ValueError("Unknown riddle type")
