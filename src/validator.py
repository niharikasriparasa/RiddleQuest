import json
import re
from typing import List, Set


# ---------------------------------------------------------
#   RIDDLE VALIDATOR (Self-contained, no external import)
# ---------------------------------------------------------
class RiddleValidator:
    def __init__(self, lookup_file: str = "lookup/lookup.json"):
        self.lookup_file = lookup_file

        with open(self.lookup_file, "r", encoding="utf-8") as f:
            self.lookup = json.load(f)

        # lookup structure:
        # {
        #   "concept_to_props": {concept: [prop1, ...], ...},
        #   "prop_to_concepts": {prop: [concepts...], ...}
        # }

        self.concept_to_props = {
            k: set(v) for k, v in self.lookup.get("concept_to_props", {}).items()
        }
        self.prop_to_concepts = {
            k: set(v) for k, v in self.lookup.get("prop_to_concepts", {}).items()
        }

    # ------------------------------------------
    # Solve the riddle using clue matching
    # ------------------------------------------
    def solve(self, pos_clues: List[str], neg_clues: List[str]) -> List[str]:
        """
        - pos_clues: list of properties that must be present
        - neg_clues: list of properties or concept names to exclude
        Strategy:
          - intersect all pos_clue property → possible concepts
          - remove negated concepts/properties
          - fallback: return best matches when empty
        """

        all_concepts = set(self.concept_to_props.keys())

        # start with all or intersection of pos_clues
        if not pos_clues:
            candidates = set(all_concepts)
        else:
            candidates = None
            for p in pos_clues:
                matching = set(self.prop_to_concepts.get(p, []))
                if candidates is None:
                    candidates = matching
                else:
                    candidates &= matching

            if candidates is None:
                candidates = set()

        # apply negations
        for n in neg_clues:
            # if equals a concept, remove it
            if n in candidates:
                candidates.discard(n)
                continue

            # if equals a property, remove all concepts with that property
            for c in list(candidates):
                if n in self.concept_to_props.get(c, set()):
                    candidates.discard(c)

        # fallback if empty → compute best property match
        if not candidates and pos_clues:
            scores = {}
            for c in all_concepts:
                props = self.concept_to_props.get(c, set())
                score = sum(1 for p in pos_clues if p in props)
                if score > 0:
                    scores[c] = score
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [c for c, _ in ranked[:5]]

        return sorted(list(candidates))


# ---------------------------------------------------------
#   EXTRACT CLUES BY SCANNING RIDDLE TEXT
# ---------------------------------------------------------
def extract_clues_from_riddle(riddle: str, all_properties: Set[str]):
    """
    Extract positive & negative clues:
      - pos_clue: direct mention of a property
      - neg_clue: "not X", "but not X"
    """
    text = riddle.lower()

    pos = []
    neg = []

    for prop in all_properties:
        prop_l = prop.lower()

        # negative patterns
        if re.search(rf"(not |but not )\b{re.escape(prop_l)}\b", text):
            neg.append(prop)
            continue

        # standard positive pattern
        if prop_l in text:
            pos.append(prop)

    return pos, neg


# ---------------------------------------------------------
#   VALIDATION PIPELINE
# ---------------------------------------------------------
def validate_riddles(
    riddles_path: str,
    lookup_path: str,
    output_path: str = "/Users/niharikasriparasa/karmaYogi/RiddleQuest1.0/data/json/riddles_validated.json"
):

    # load riddles
    riddles = json.load(open(riddles_path, "r", encoding="utf-8"))

    # init validator
    validator = RiddleValidator(lookup_file=lookup_path)

    all_properties = set(validator.prop_to_concepts.keys())

    output = []

    for item in riddles:

        # your riddle structure: {concept, version, riddle}
        riddle_text = item["riddle"]

        # extract clues
        pos, neg = extract_clues_from_riddle(riddle_text, all_properties)

        # solve using lookup
        possible_answers = validator.solve(pos, neg)
        best_answer = possible_answers[0] if possible_answers else None

        output.append({
            "concept": item.get("concept"),
            "version": item.get("version"),
            "riddle": riddle_text,
            "pos_clues": pos,
            "neg_clues": neg,
            "answer": best_answer,
            "possible_answers": possible_answers
        })

    # save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✔ Saved validated riddles → {output_path}")


# ---------------------------------------------------------
#   MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    validate_riddles(
        riddles_path="riddles_with_answers.json",
        lookup_path="lookup.json"
    )
