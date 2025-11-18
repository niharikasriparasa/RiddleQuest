import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------
# 1. Load your JSON triple data
# ---------------------------------------------------------
data = json.loads(open("/Users/niharikasriparasa/karmaYogi/RiddleQuest1.0/data/json/sample_data.json").read())

# ---------------------------------------------------------
# 2. Load embedding model
# ---------------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------------------------------------
# 3. Embed all triples per concept
# ---------------------------------------------------------
concept_embeddings = {}
concept_sentences = {}
concept_indices = {}

global_index = 0
for item in data:
    concept = item["concept"]
    sentences = item["triples"]
    embeds = model.encode(sentences)

    concept_embeddings[concept] = embeds
    concept_sentences[concept] = sentences

    idx_range = list(range(global_index, global_index + len(sentences)))
    concept_indices[concept] = idx_range
    global_index += len(sentences)

# Build global matrix + index→concept mapping
all_embeddings = np.vstack([concept_embeddings[c] for c in concept_embeddings])

index_to_concept = {}
for concept, idx_list in concept_indices.items():
    for idx in idx_list:
        index_to_concept[idx] = concept

# ---------------------------------------------------------
# 4. KNN neighbouring-concept classifier
# ---------------------------------------------------------
knn = NearestNeighbors(n_neighbors=3, metric="cosine")
knn.fit(all_embeddings)

def classify_with_neighbors(concept, threshold=0.65):
    results = []
    own_indices = concept_indices[concept]
    own_embeds = concept_embeddings[concept]

    for i, emb in enumerate(own_embeds):
        distances, indices = knn.kneighbors([emb])
        distances = distances[0]
        indices = indices[0]

        # Filter neighbours from other concepts
        filtered = [(d, idx) for d, idx in zip(distances, indices)
                    if index_to_concept[idx] != concept]

        if filtered:
            avg_dist = float(np.mean([d for d, _ in filtered]))
            neighbor_concepts = list({index_to_concept[idx] for _, idx in filtered})
            label = "topic_marker" if avg_dist > threshold else "common"
        else:
            avg_dist = float(distances.mean())
            neighbor_concepts = []
            label = "topic_marker"

        results.append({
            "triple": concept_sentences[concept][i],
            "avg_distance": avg_dist,
            "label": label,
            "neighboring_concepts": neighbor_concepts
        })

    return results

# ---------------------------------------------------------
# 5. Run classification for all concepts
# ---------------------------------------------------------
final_output = {}
for concept in concept_embeddings.keys():
    final_output[concept] = classify_with_neighbors(concept)

# ---------------------------------------------------------
# 6. SAVE OUTPUT JSON HERE
# ---------------------------------------------------------
with open("/Users/niharikasriparasa/karmaYogi/RiddleQuest1.0/data/json/triples_class.json", "w") as f:
    json.dump(final_output, f, indent=2)

print("Saved: triples_class.json")
