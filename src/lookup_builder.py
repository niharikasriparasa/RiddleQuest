
import json
import os
import re
from collections import defaultdict
from typing import Tuple

TRIPLES_PATH = "triples_class.json"
LOOKUP_OUT = "lookup.json"


def extract_property_from_sentence(sentence: str, concept: str) -> str:
    """
    Convert sentence-like triple ("Dog is a domesticated mammal.") into a short property phrase:
      - removes the concept token, leading verbs/articles, 'by' 'to', trailing punctuation
      - returns e.g. 'domesticated mammal', 'keen sense of smell', 'barking'
    """
    if not sentence:
        return ""
    s = str(sentence).strip()
    # remove concept (case-insensitive) at start
    s = re.sub(rf'^\s*{re.escape(concept)}\b', '', s, flags=re.IGNORECASE).strip()
    # remove leading common verbs/articles
    s = re.sub(r'^(is|are|was|were|has|have|can|often|commonly|sometimes|may)\b', '', s, flags=re.IGNORECASE).strip()
    s = re.sub(r'^(a|an|the)\b', '', s, flags=re.IGNORECASE).strip()
    # remove common connecting prepositions used in triples
    s = re.sub(r'\bby\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bto\b', '', s, flags=re.IGNORECASE)
    s = s.rstrip(".!?").strip()
    # collapse spaces
    s = re.sub(r'\s+', ' ', s)
    return s


def build_lookup(triples_path: str = TRIPLES_PATH, save_path: str = LOOKUP_OUT) -> dict:
    """
    Read triples_class.json and create:
      - concept_to_props: concept -> list of property strings
      - prop_to_concepts: property -> list of concepts that have it
      - triples_meta: concept -> list of { phrase, label, neighboring_concepts }
    Saves JSON to lookup/lookup.json and returns the dict.
    """
    if not os.path.exists(triples_path):
        raise FileNotFoundError(f"Triples file not found: {triples_path}")

    raw = json.load(open(triples_path, "r", encoding="utf-8"))

    concept_to_props = defaultdict(set)
    prop_to_concepts = defaultdict(set)
    triples_meta = defaultdict(list)

    for concept, entries in raw.items():
        for e in entries:
            # e expected to contain e["triple"] (sentence) and e["label"]
            sent = e.get("triple") if isinstance(e, dict) else e
            label = e.get("label") if isinstance(e, dict) else None
            neigh = e.get("neighboring_concepts", []) if isinstance(e, dict) else []

            prop = extract_property_from_sentence(sent, concept)
            if not prop:
                continue

            # normalize to lower-case compact phrase
            norm = prop.lower().strip()

            concept_to_props[concept].add(norm)
            prop_to_concepts[norm].add(concept)
            triples_meta[concept].append({
                "phrase": norm,
                "label": label,
                "neighboring_concepts": neigh
            })

    # build final dict
    lookup = {
        "concept_to_props": {c: sorted(list(ps)) for c, ps in concept_to_props.items()},
        "prop_to_concepts": {p: sorted(list(cs)) for p, cs in prop_to_concepts.items()},
        "triples": {c: v for c, v in triples_meta.items()}
    }

    # save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(lookup, f, indent=2, ensure_ascii=False)

    print(f"[lookup_builder] saved lookup to {save_path} — {len(lookup['concept_to_props'])} concepts")
    return lookup


if __name__ == "__main__":
    build_lookup()
