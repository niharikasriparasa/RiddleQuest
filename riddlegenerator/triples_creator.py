import wikipedia
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_triples(concept):
    """
    Extract subject-predicate-object triples from Wikipedia summary.
    """
    summary = wikipedia.summary(concept)
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
