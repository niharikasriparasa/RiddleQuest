import time
from riddle_generator.triples_creator import extract_triples
import spacy
from sklearn.metrics import precision_score, recall_score, f1_score

# ground truth sample triples (you can expand this manually for a few test summaries)
# These are for evaluation purposes — adjust as needed
GROUND_TRUTH = {
    "Python (programming language)": [
        ("Python (programming language)", "is", "programming language"),
        ("Python (programming language)", "supports", "object-oriented programming"),
        ("Python (programming language)", "was created", "Guido van Rossum"),
    ]
}

nlp = spacy.load("en_core_web_sm")

def normalize_token(text):
    return text.lower().strip()

def evaluate(concept):
    """
    Simple evaluation: compare extracted triples with ground truth
    based on overlap of (subject, object) pairs.
    """
    print(f"\nEvaluating concept: {concept}")
    start = time.time()
    extracted = extract_triples(concept)
    elapsed = time.time() - start

    gt_triples = GROUND_TRUTH.get(concept, [])
    gt_pairs = {(normalize_token(s), normalize_token(o)) for (s, _, o) in gt_triples}
    extracted_pairs = {(normalize_token(s), normalize_token(o)) for (s, _, o) in extracted}

    true_pos = len(gt_pairs & extracted_pairs)
    false_pos = len(extracted_pairs - gt_pairs)
    false_neg = len(gt_pairs - extracted_pairs)

    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) else 0
    recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print(f"Extracted {len(extracted)} triples in {elapsed:.2f}s")
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1: {f1:.2f}")

    # qualitative sample
    print("\nSample extracted triples:")
    for t in extracted[:8]:
        print(f"  {t}")

if __name__ == "__main__":
    evaluate("Python (programming language)")
