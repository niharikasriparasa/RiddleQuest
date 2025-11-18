import wikipedia
import nltk
import spacy
from neural_extractors import Extractor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK resources if not already present
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load neural extractor model
neural_extractor = Extractor("relbert-base")  # or "relbert-large" if you have GPU

# -----------------------------
# 1. NLTK-based Triple Extractor
# -----------------------------
def nltk_triples(summary):
    tokens = nltk.word_tokenize(summary)
    pos_tags = nltk.pos_tag(tokens)
    triples = []

    for i in range(len(pos_tags) - 2):
        w1, t1 = pos_tags[i]
        w2, t2 = pos_tags[i + 1]
        w3, t3 = pos_tags[i + 2]
        # Simple heuristic: (Noun, Verb, Noun/Adj)
        if t1.startswith("NN") and t2.startswith("VB") and (t3.startswith("NN") or t3.startswith("JJ")):
            triples.append((w1, w2, w3))
    return triples

# -----------------------------
# 2. spaCy-based Triple Extractor
# -----------------------------
def spacy_triples(summary):
    doc = nlp(summary)
    triples = []
    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "ROOT":
                subj = [w.text for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                obj = [w.text for w in token.rights if w.dep_ in ("dobj", "pobj")]
                if subj and obj:
                    triples.append((subj[0], token.text, obj[0]))
    return triples

# -----------------------------
# 3. Neural Extractors
# -----------------------------
def neural_triples(summary):
    triples = neural_extractor.extract(summary)
    # neural_extractors outputs (subject, relation, object)
    return [(t["subject"], t["relation"], t["object"]) for t in triples]

# -----------------------------
# 4. Compare Content Scores
# -----------------------------
def compute_content_score(triples_a, triples_b):
    """
    Compute content similarity between two sets of triples using TF-IDF cosine similarity.
    """
    if not triples_a or not triples_b:
        return 0.0

    text_a = [" ".join(t) for t in triples_a]
    text_b = [" ".join(t) for t in triples_b]

    vectorizer = TfidfVectorizer().fit(text_a + text_b)
    vec_a = vectorizer.transform([" ".join(text_a)])
    vec_b = vectorizer.transform([" ".join(text_b)])

    score = cosine_similarity(vec_a, vec_b)[0][0]
    return score

# -----------------------------
# 5. Pipeline Runner
# -----------------------------
def compare_extractors(concept):
    print(f"\n🔍 Comparing Triple Extractors for: {concept}")
    summary = wikipedia.summary(concept, sentences=5)

    triples_nltk = nltk_triples(summary)
    triples_spacy = spacy_triples(summary)
    triples_neural = neural_triples(summary)

    score_nltk_spacy = compute_content_score(triples_nltk, triples_spacy)
    score_spacy_neural = compute_content_score(triples_spacy, triples_neural)
    score_nltk_neural = compute_content_score(triples_nltk, triples_neural)

    print(f"\n📄 Wikipedia Summary:\n{summary[:400]}...\n")

    print(f"NLTK Triples ({len(triples_nltk)}): {triples_nltk[:5]}")
    print(f"spaCy Triples ({len(triples_spacy)}): {triples_spacy[:5]}")
    print(f"Neural Triples ({len(triples_neural)}): {triples_neural[:5]}")

    print("\n--- Content Similarity Scores (Cosine) ---")
    print(f"NLTK ↔ spaCy:   {score_nltk_spacy:.3f}")
    print(f"spaCy ↔ Neural: {score_spacy_neural:.3f}")
    print(f"NLTK ↔ Neural:  {score_nltk_neural:.3f}")

if __name__ == "__main__":
    compare_extractors("Python (programming language)")
