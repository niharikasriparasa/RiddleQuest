# pipeline.py
import json
import os
from generator import RiddleGenerator
from validator import RiddleValidator
from lookup_builder import build_lookup

TRIPLE_PATH = "triples_class.json"
TEMPLATE_PATH = "templates.json"
LOOKUP_PATH="lookup.json"
OUTPUT_PATH = "riddles_with_answers.json"


def run_pipeline():
    # 1) build lookup (and save it)
    lookup = build_lookup(TRIPLE_PATH, LOOKUP_PATH)

    # 2) generate riddles
    gen = RiddleGenerator(TRIPLE_PATH, TEMPLATE_PATH)
    riddles = gen.generate_all(save_path="outputs/generated_riddles.json")

    # 3) validate riddles using lookup
    validator = RiddleValidator(LOOKUP_PATH)

    final = {"riddles": [], "answers": {}}

    for r in riddles:
        pos = r.get("pos_clues", [])
        neg = r.get("neg_clues", [])
        # ensure normalization: lower-case strings as in lookup
        pos = [str(x).lower().strip() for x in pos]
        neg = [str(x).lower().strip() for x in neg]

        answers = validator.solve(pos, neg)
        final["riddles"].append(r)
        final["answers"][r["riddle"]] = answers

    # save single combined file
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    print(f"[pipeline] saved output to {OUTPUT_PATH}")
    print(f"Riddles generated: {len(final['riddles'])}")
    return final


if __name__ == "__main__":
    run_pipeline()