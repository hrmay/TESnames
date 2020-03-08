import random


def weighted_choice(weighted_values):
    values = []
    weights = []

    for weighted_value in weighted_values:
        if isinstance(weighted_values, dict):
            values.append(weighted_values[weighted_value])
            weights.append(weighted_values[weighted_value]["weight"])
        elif isinstance(weighted_values, list):
            values.append(weighted_value)
            weights.append(weighted_value["weight"])

    total_weight = sum(weights)

    # Convert the weights into ranges for a random int to be compared against
    # The lower bound of each item is the upper bound of the previous
    for i in range(1, len(weights)):
        weights[i] += weights[i - 1]

    choice = random.randint(1, total_weight)

    for i, value in enumerate(values):
        if choice <= weights[i]:
            return value
    else:
        return None  # Should never happen
