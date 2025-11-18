import wikipedia
import torch
from transformers import BertTokenizer, BertForMaskedLM
import spacy
from rake_nltk import Rake

# Load NLP tools
nlp = spacy.load("en_core_web_sm")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForMaskedLM.from_pretrained("bert-base-uncased")

def get_keywords(summary, num_keywords=15):
    """Extract keywords from text using RAKE."""
    rake = Rake()
    rake.extract_keywords_from_text(summary)
    ranked = rake.get_ranked_phrases()[:num_keywords]
    return ranked

def get_pos_tokens(summary):
    """Get nouns, verbs, adjectives, adverbs from the summary."""
    doc = nlp(summary)
    pos_tokens = [token.text for token in doc if token.pos_ in ["NOUN", "VERB", "ADJ", "ADV"]]
    return list(set(pos_tokens))

def predict_relation(concept, keyword, top_k=1):
    """
    Use BERT MLM to find the most likely relation between concept and keyword.
    We use a masked template: "[CLS] <concept> [MASK] <keyword> . [SEP]"
    """
    template = f"[CLS] {concept} [MASK] {keyword} . [SEP]"
    inputs = tokenizer(template, return_tensors="pt")
    mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]

    with torch.no_grad():
        logits = model(**inputs).logits

    mask_token_logits = logits[0, mask_token_index, :]
    top_tokens = torch.topk(mask_token_logits, top_k, dim=1).indices[0].tolist()
    relations = [tokenizer.decode([token]).strip() for token in top_tokens]

    return relations[0] if relations else "related_to"

def extract_triples(concept):
    """
    Extract (subject, relation, object) triples from Wikipedia summaries using:
      - RAKE for keyphrases
      - POS tagging for key tokens
      - BERT MLM for relations
    """
    try:
        summary = wikipedia.summary(concept, sentences=5)
    except Exception as e:
        raise RuntimeError(f"Could not fetch Wikipedia summary for {concept}: {e}")

    keywords = get_keywords(summary)
    pos_tokens = get_pos_tokens(summary)
    combined_candidates = list(set(keywords + pos_tokens))

    triples = []
    for kw in combined_candidates:
        relation = predict_relation(concept, kw)
        triples.append((concept, relation, kw))

    return triples

if __name__ == "__main__":
    concept = "Python (programming language)"
    triples = extract_triples(concept)
    print("\nExtracted Triples:")
    for t in triples[:10]:
        print(t)
