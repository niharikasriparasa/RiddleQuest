import json
from sentence_transformers import SentenceTransformer

class TripleEmbedder:
    def __init__(self, triples_file, out_file="embeddings.json",
                 model_name="all-MiniLM-L6-v2"):

        self.triples_file = triples_file
        self.out_file = out_file
        self.model = SentenceTransformer(model_name)

        with open(triples_file) as f:
            self.triples = json.load(f)

        self.embeddings = {}

    def create_embeddings(self):
        print("Generating embeddings...")

        for concept, items in self.triples.items():
            for idx, entry in enumerate(items):
                triple_text = entry["triple"]

                emb = self.model.encode(triple_text).tolist()

                key = f"{concept}::{idx}"
                self.embeddings[key] = emb

        with open(self.out_file, "w") as f:
            json.dump(self.embeddings, f, indent=2)

        print(f"Embeddings saved to {self.out_file}")
        return self.embeddings

embedder = TripleEmbedder("triples_class.json", "embeddings.json")
embedder.create_embeddings()