import json
import random
from typing import List, Dict


class RiddleGenerator:
    def __init__(self, triples_path: str, templates_path: str):
        self.triples = self._load(triples_path)
        self.templates = self._load(templates_path)

    def _load(self, path):
        with open(path, "r") as f:
            return json.load(f)

    # -------------------------------------------------------
    # Extract property text from "Dog has acute hearing"
    # -------------------------------------------------------
    def extract_property(self, concept: str, sentence: str) -> str:
        txt = sentence.replace(concept, "").strip()
        tokens = txt.split()
        if len(tokens) <= 1:
            return txt
        # drop “is / has / can / are / was”
        if tokens[0].lower() in ["is", "are", "has", "have", "can", "may", "was"]:
            tokens = tokens[1:]
        return " ".join(tokens).rstrip(".")

    # -------------------------------------------------------
    # Collect properties by label
    # -------------------------------------------------------
    def get_topic_properties(self, concept):
        props = []
        for t in self.triples[concept]:
            if t["label"] == "topic_marker":
                p = self.extract_property(concept, t["triple"])
                if p:
                    props.append(p)
        return props

    def get_common_properties(self, concept):
        props = []
        for t in self.triples[concept]:
            if t["label"] == "common":
                p = self.extract_property(concept, t["triple"])
                if p:
                    props.append((p, t["neighboring_concepts"]))
        return props

    # -------------------------------------------------------
    # Helper: get properties of a neighboring concept
    # -------------------------------------------------------
    def get_neighbor_properties(self, neighbor: str) -> List[str]:
        if neighbor not in self.triples:
            return []
        props = []
        for t in self.triples[neighbor]:
            p = self.extract_property(neighbor, t["triple"])
            if p:
                props.append(p)
        return props

    # -------------------------------------------------------
    # Version 1: Topic marker riddles
    # -------------------------------------------------------
    def make_v1(self, concept: str) -> Dict:
        props = self.get_topic_properties(concept)
        if len(props) < 3:
            return None

        chosen = random.sample(props, min(5, max(3, len(props))))

        template = random.choice(self.templates["v1"])

        lines = [template.replace("{prop}", p) for p in chosen]
        lines.append("What am I?")

        return {"concept": concept, "version": "v1", "riddle": "\n".join(lines)}

    # -------------------------------------------------------
    # Version 2: common property vs negated concept
    # -------------------------------------------------------
    def make_v2(self, concept: str) -> Dict:
        commons = self.get_common_properties(concept)
        if not commons:
            return None

        lines = []
        for (prop, neighbors) in commons:
            if not neighbors:
                continue
            neg_con = random.choice(neighbors)
            template = random.choice(self.templates["v2"])
            line = template.replace("{prop}", prop).replace("{neg_con}", neg_con)
            lines.append(line)

        if len(lines) < 3:
            return None

        chosen = random.sample(lines, min(5, max(3, len(lines))))
        chosen.append("What am I?")

        return {"concept": concept, "version": "v2", "riddle": "\n".join(chosen)}

    # -------------------------------------------------------
    # Version 3: common property vs negated property
    # -------------------------------------------------------
    def make_v3(self, concept: str) -> Dict:
        commons = self.get_common_properties(concept)
        if not commons:
            return None

        lines = []
        for (prop, neighbors) in commons:
            if not neighbors:
                continue
            neg_con = random.choice(neighbors)
            neg_props = self.get_neighbor_properties(neg_con)

            if not neg_props:
                continue

            neg_prop = random.choice(neg_props)

            template = random.choice(self.templates["v3"])
            line = template.replace("{prop}", prop).replace("{neg_prop}", neg_prop)
            lines.append(line)

        if len(lines) < 3:
            return None

        chosen = random.sample(lines, min(5, max(3, len(lines))))
        chosen.append("What am I?")

        return {"concept": concept, "version": "v3", "riddle": "\n".join(chosen)}

    # -------------------------------------------------------
    # Generate all riddles for all concepts
    # -------------------------------------------------------
    def generate_all(self):
        output = []

        for concept in self.triples:
            r1 = self.make_v1(concept)
            r2 = self.make_v2(concept)
            r3 = self.make_v3(concept)

            for r in [r1, r2, r3]:
                if r:
                    output.append(r)

        return output

    # -------------------------------------------------------
    # Save riddles with answers
    # -------------------------------------------------------
    def save(self, output_path: str, riddles):
        out = {"riddles": riddles}
        with open(output_path, "w") as f:
            json.dump(out, f, indent=2)


rg = RiddleGenerator("triples_class.json", "templates.json")
riddles = rg.generate_all()
rg.save("riddles_with_answers.json", riddles)

print("Generated:", len(riddles), "riddles")