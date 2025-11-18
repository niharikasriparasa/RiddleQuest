#from riddlegenerator.triples_creator import extract_triples
from riddlegenerator.triples_extraction import extract_triples
from riddlegenerator.properties_identifier import classify_triples
from riddlegenerator.lookup_dictionary import ConceptPropertyDictionary
from riddlegenerator.generator import generate_riddle

def run_pipeline():
    num_concepts = int(input("Enter number of concepts: "))
    concepts = []
    for i in range(num_concepts):
        concept_name = input(f"Enter concept {i+1} name: ")
        concepts.append(concept_name)

    lookup = ConceptPropertyDictionary()

    for concept in concepts:
        print(f"\nProcessing concept: {concept}")
        try:
            triples = extract_triples(concept)
            classified_triples = classify_triples(triples)
            lookup.add_triples(concept, classified_triples)
            
            print(f"Extracted {len(triples)} triples for '{concept}'")
            print("Easy Riddle:", generate_riddle(classified_triples, "easy"))
            print("V2 Riddle:", generate_riddle(classified_triples, "v2"))
            print("V3 Riddle:", generate_riddle(classified_triples, "v3"))
        except Exception as e:
            print(f"Failed to process '{concept}': {e}")

if __name__ == "__main__":
    run_pipeline()
