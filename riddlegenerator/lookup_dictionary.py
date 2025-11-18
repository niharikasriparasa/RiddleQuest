class ConceptPropertyDictionary:
    def __init__(self):
        self.mapping = {}

    def add_triples(self, concept, triples):
        self.mapping[concept] = triples

    def get_properties(self, concept):
        return self.mapping.get(concept, [])
