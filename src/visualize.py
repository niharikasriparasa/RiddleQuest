import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE

class TripleVisualizer:
    """
    Visualizes embeddings and concept similarity.
    """

    def __init__(self, triples_path, embeddings_path=None):
        self.triples_path = triples_path
        self.embeddings_path = embeddings_path

        with open(triples_path, "r") as f:
            self.triples = json.load(f)

        if embeddings_path:
            with open(embeddings_path, "r") as f:
                self.embeddings = json.load(f)
        else:
            self.embeddings = None

    # --------------------------------------------------------------
    # SAFE PROPERTY EXTRACTION
    # --------------------------------------------------------------
    def extract_property(self, triple_entry):

        if "property" in triple_entry:
            return triple_entry["property"]

        if "object" in triple_entry:
            return triple_entry["object"]

        if "relation" in triple_entry and "object" in triple_entry:
            return f"{triple_entry['relation']} {triple_entry['object']}"

        if "triple" in triple_entry:
            txt = triple_entry["triple"]
            for sep in [" is ", " are ", " has ", " have ", " can ", " may ",
                        " often ", " sometimes ", " uses ", " with "]:
                if sep in txt:
                    return txt.split(sep)[-1].strip()

            return txt

        return "unknown_property"

    # --------------------------------------------------------------
    # FANCY t-SNE PLOT (NO PCA)
    # --------------------------------------------------------------
    def plot_tsne(self, save_path="tsne_fancy.png"):
        if self.embeddings is None:
            raise ValueError("No embeddings.json found.")

        embeds = []
        concepts = []
        labels = []
        missing = 0

        for concept, triples in self.triples.items():
            for i, triple in enumerate(triples):
                key = f"{concept}_{i}"

                if key not in self.embeddings:
                    missing += 1
                    continue

                emb = self.embeddings[key]

                if not emb or len(emb) == 0:
                    missing += 1
                    continue

                embeds.append(emb)
                concepts.append(concept)
                labels.append(triple["label"])

        if len(embeds) == 0:
            print("[ERROR] No embeddings found.")
            return

        X = np.array(embeds)

        # ----------------------------------------------------------
        # t-SNE dimensionality reduction
        # ----------------------------------------------------------
        tsne = TSNE(
            n_components=2,
            perplexity=30,
            learning_rate=200,
            n_iter=1500,
            init="random",
            random_state=42,
        )
        reduced = tsne.fit_transform(X)

        # ----------------------------------------------------------
        # Assign colors to concepts
        # ----------------------------------------------------------
        concept_list = sorted(list(set(concepts)))
        palette = sns.color_palette("husl", len(concept_list))  # bright distinct colors
        color_map = {c: palette[i] for i, c in enumerate(concept_list)}

        colors = [color_map[c] for c in concepts]

        # ----------------------------------------------------------
        # Plot
        # ----------------------------------------------------------
        plt.figure(figsize=(12, 10))
        plt.scatter(
            reduced[:, 0],
            reduced[:, 1],
            c=colors,
            s=80,
            alpha=0.8,
            edgecolor="black",
            linewidth=0.5,
        )

        # Annotate each point faintly
        for i, concept in enumerate(concepts):
            plt.text(
                reduced[i, 0] + 0.5,
                reduced[i, 1] + 0.5,
                concept,
                fontsize=7,
                alpha=0.6,
            )

        # Add Legend
        for c in concept_list:
            plt.scatter([], [], c=color_map[c], label=c, s=120, edgecolor="black")

        plt.legend(
            title="Concepts",
            loc="upper right",
            fontsize=10,
            title_fontsize=12,
            frameon=True,
        )

        plt.title("t-SNE Visualization of Concept Embeddings", fontsize=16)
        plt.xlabel("t-SNE Dim 1")
        plt.ylabel("t-SNE Dim 2")
        plt.grid(alpha=0.2)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"[Saved] {save_path}")
        print(f"[Info] Missing embeddings skipped: {missing}")

    # --------------------------------------------------------------
    # PROPERTY SIMILARITY FOR 3 CONCEPTS
    # --------------------------------------------------------------
    def compare_three_concepts(self, concepts, save_path="concept_property_similarity.png"):
        if len(concepts) != 3:
            raise ValueError("Exactly 3 concepts required.")

        all_properties = {}
        for c in concepts:
            if c not in self.triples:
                raise KeyError(f"Concept '{c}' not found.")

            props = [self.extract_property(t) for t in self.triples[c]]
            all_properties[c] = list(set(props))

        # union
        union = sorted(list(set(p for group in all_properties.values() for p in group)))

        vectors = []
        for c in concepts:
            vec = [1 if p in all_properties[c] else 0 for p in union]
            vectors.append(vec)

        sim = cosine_similarity(np.array(vectors))

        plt.figure(figsize=(7, 5))
        sns.heatmap(
            sim,
            annot=True,
            cmap="Blues",
            xticklabels=concepts,
            yticklabels=concepts,
            fmt=".2f",
        )
        plt.title("Property Similarity Across Concepts")
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

        print(f"[Saved] {save_path}")


# --------------------------------------------------------------
# RUN (optional)
# --------------------------------------------------------------
if __name__ == "__main__":
    viz = TripleVisualizer("/Users/niharikasriparasa/karmaYogi/RiddleQuest1.0/data/json/triples_class.json", embeddings_path="/Users/niharikasriparasa/karmaYogi/RiddleQuest1.0/data/json/embeddings.json")
    viz.plot_tsne()
    viz.compare_three_concepts(["Dog", "Cat", "Fish"])
