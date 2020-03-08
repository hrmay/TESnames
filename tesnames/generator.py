import markovify
import json
import os
import random
import re

from .parameter_parser import get_race_path, get_gender, get_starts_with, get_syllables
from .choice import weighted_choice
from .error import NoStructuresForGenderError

# The maximum number of syllables a name should have if all other attempts at figuring this out fail
DEFAULT_MAX_SYLLABLES = 4

# Closest approximation of typical vowel sequences I can easily come up with
vowel_lists = [
    [first + last for last in ["a", "e", "i", "o", "u", "y"]]
    for first in ["a", "e", "o", "y", ""]
]
vowels = [vowel for sublist in vowel_lists for vowel in sublist]

pronouns = {
    "male": {"pronoun": "he", "possessive": "his", "object": "him", "person": "man"},
    "female": {
        "pronoun": "she",
        "possessive": "her",
        "object": "her",
        "person": "woman",
    },
    "neutral": {
        "pronoun": "they",
        "possessive": "their",
        "object": "them",
        "person": "person",
    },
}


def generate_name(parameters):
    """Generate a name based on the given dictionary. The dictionary can contain the race, subrace, gender, name types, and beginnings of the first and/or last names."""

    # Fold everything to lowercase since that's what the generator uses internally
    params = to_lower(parameters)

    race_path = get_race_path(params)
    gender = get_gender(params)

    with open(os.path.join(race_path, "config.json")) as config_file:
        config = json.load(config_file)
        name = config["structure"]

        types = (
            params["types"] if "types" in params else ["first"]
        )  # First name is the most important, so it's the default

        for name_type in types:
            components = config["components"]

            if name_type in components:
                structure = choose_structure(components, name_type, gender)

                # The parts of the full name (e.g. the first name and the last name)
                name_part = structure["structure"]

                tokens = re.findall("<(.*?)>", name_part)

                for token in tokens:

                    # The number of arguments keeps getting longer as I write this
                    name_token = generate_token(
                        race_path, structure, token.lower(), config, params, gender,
                    )
                    name_part = name_part.replace("<" + token.upper() + ">", name_token)

                name = name.replace("<" + name_type.upper() + ">", name_part)

    name = re.sub(r"<(.*?)>", "", name)
    name = name.strip()
    return name


def choose_structure(components, name_type, gender):
    """Chooses a name structure from components based on the given name type and gender."""

    # Use the user-specified gender and gender-neutral options
    possible_structures = (
        components[name_type][gender] if (gender in components[name_type]) else []
    ) + (components[name_type]["all"] if "all" in (components[name_type]) else [])

    if possible_structures:
        return weighted_choice(possible_structures)
    else:
        raise NoStructuresForGenderError(name_type, gender)


def generate_token(race_path, structure, token_name, config, parameters, gender):
    token_info = structure["components"][token_name]
    starts_with = get_starts_with(parameters, token_name)
    state_size = config["state_size"]
    join_char = structure["join"] if "join" in structure else ""
    config_max_syllables = config["max_syllables"] if "max_syllables" in config else 0
    max_syllables = (
        get_syllables(parameters) or config_max_syllables or DEFAULT_MAX_SYLLABLES
    )
    capitalize = token_info["capitalize"] if "capitalize" in token_info else True
    select = token_info["select"] if "select" in token_info else False
    name_data = None

    if "file" in token_info:
        token_file = f"{race_path}/{token_info['file']}"

        with open(token_file) as tf:
            name_data = tf.read().splitlines() if select else tf.read()
    elif "choice" in token_info:
        name_data = token_info["choice"]

    generated_name = ""
    if select:
        # Select a single name from the source set of names
        generated_name = random.choice(name_data)
    else:
        # Markov chain a name
        text_model = markovify.NewlineText(name_data, state_size=state_size)
        generated_name = markov_generate_name(
            text_model,
            starts_with,
            state_size,
            max_syllables,
            join_char,
            capitalize,
            gender,
        )

    return generated_name.title() if capitalize else generated_name


def markov_generate_name(
    text_model, starts_with, state_size, max_syllables, join_char, capitalize, gender
):
    name = None
    short_enough = int(max_syllables) <= 0

    while name is None or not short_enough:
        if starts_with == "":
            name = text_model.make_sentence()
        else:
            try:
                name = text_model.make_sentence_with_start(starts_with)
            except:
                return None

        if not short_enough and name is not None:
            syllables = 0
            for vowel in vowels:
                syllables += name.count(vowel)

            if syllables <= max_syllables:
                short_enough = True

    name = join_char.join(name.split())
    if gender in pronouns:
        for gendered_word in pronouns[gender]:
            name = name.replace(gendered_word.upper(), pronouns[gender][gendered_word])

    return name


def to_lower(parameters):
    """Folds the parameters to lowercase."""
    return json.loads(json.dumps(parameters).lower())


if __name__ == "__main__":
    race = input("Race    : ")
    subrace = input("Subrace : ")
    gender = input("Gender  : ")
    user_types = input("Types   : ")
    types = "".join(user_types.split()).split(",") if user_types != "" else ["first"]
    param = {"race": race, "subrace": subrace, "gender": gender, "types": types}
    print(generate_name(param))
