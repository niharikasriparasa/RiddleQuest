# validator.py

def get_possible_answers(riddle, lookup_dict):
    """
    Given a riddle and a lookup dictionary, returns all possible answers
    by checking which concepts have properties matching words in the riddle.

    Args:
        riddle (str): The riddle text.
        lookup_dict (dict): {concept: {property: object}}

    Returns:
        List[str]: Concepts that match the riddle clues.
    """
    riddle_words = set(riddle.lower().replace(',', '').replace('.', '').split())

    possible_answers = []

    for concept, props in lookup_dict.items():
        # Flatten all property names and values for matching
        prop_values = set()
        for k, v in props.items():
            if isinstance(v, str):
                prop_values.update(v.lower().split())
            if isinstance(k, str):
                prop_values.update(k.lower().split())

        # If any riddle word matches a property or value, consider as possible answer
        if riddle_words & prop_values:
            possible_answers.append(concept)

    return possible_answers
