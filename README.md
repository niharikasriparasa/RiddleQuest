🧩 RiddleGen: Automatic Riddle Generation From Knowledge Triples
RiddleGen is a modular pipeline that transforms knowledge triples into high-quality riddles, and then solves/validates them using a symbolic lookup-based validator.
The system supports:
✔ Triple classification
✔ Embedding & similarity visualization
✔ Template-based riddle generation (3 versions)
✔ Automated riddle solving
✔ Saving riddles + all possible answers
✔ Fully pluggable triples, templates, and concepts
RiddleGen is designed for NLP research, reasoning tasks, and educational content generation.
📁 Project Structure
.
├── triples/
│   └── triples_class.json
├── templates/
│   └── templates.json
├── lookup/
│   └── lookup.json
├── generator/
│   └── generator.py
├── validator/
│   └── validator.py
├── pipeline/
│   ├── build_lookup.py
│   ├── pipeline.py
│   └── visualise.py
├── outputs/
│   └── riddles_with_answers.json
├── embeddings/
│   └── embeddings.json
├── requirements.txt
├── README.md
└── LICENSE
🚀 Features
1. Triple Embedding & Classification
Generates embeddings for each triple
Computes similarity between concepts
Classifies triples as:
topic_marker → unique to one concept
common → shared across concepts
2. Riddle Generation (3 Versions)
Version 1 — Topic-Marker Riddles
Uses unique triples of a concept.
Example:
I breathe using gills.
I live in water.
I use fins to move.
What am I?
Version 2 — Contrast Riddles
Uses common properties + contrasting with another concept.
I am furry but not a dog.
What am I?
Version 3 — Positive vs Negative Property Riddles
Uses properties to strengthen reasoning.
I have whiskers but not retractable claws.
What am I?
3. Symbolic Riddle Validator
Given a riddle, extracts:
positive clues
negative clues
Then uses lookup dictionaries to identify:
answer
all possible answers (if multiple concepts fit)
Saves to:
outputs/riddles_with_answers.json
4. Visualization
The pipeline can create:
t-SNE embedding plots
Similarity maps
Concept clusters with labels
🛠️ Installation
Clone repository:
git clone https://github.com/yourusername/riddlegen.git
cd riddlegen
Install dependencies:
pip install -r requirements.txt
▶️ Running the Pipeline
1. Build Lookup
python pipeline/build_lookup.py
2. Generate Embeddings & Classify Triples
python pipeline/pipeline.py
3. Visualise
python pipeline/visualise.py
4. Generate Riddles
python generator/generator.py
5. Validate Riddles
python validator/validator.py
📦 Outputs
Final riddles with answers and possible answers:
outputs/riddles_with_answers.json
Example entry:
{
  "concept": "Cat",
  "version": "v1",
  "riddle": "I have whiskers.\nI am a carnivore.\nI sleep for most of the day.\nWhat am I?",
  "answer": "Cat",
  "possible_answers": ["Cat", "Tiger"]
}
📜 Templates Format
templates/templates.json
{
  "v1": [
    "{s1}\n{s2}\n{s3}\nWhat am I?"
  ],
  "v2": [
    "I am {p1} but not {contrast_concept}.\nWhat am I?"
  ],
  "v3": [
    "I have {positive_prop} but not {negative_prop}.\nWhat am I?"
  ]
}
🧠 Lookup Format
lookup/lookup.json
{
  "concept_to_props": {
    "Cat": ["has_fur", "has_whiskers", "meows"],
    "Dog": ["has_fur", "barks"]
  },
  "prop_to_concepts": {
    "has_fur": ["Cat", "Dog"],
    "meows": ["Cat"],
    "barks": ["Dog"]
  }
}
🤝 Contributing
Contributions are welcome.
Please open an issue before large changes.
📜 License
This project is licensed under the MIT License.
