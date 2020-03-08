import markovify
import json
import os
import random
import re

from .validator import race

# Closest approximation of typical vowel sequences I can easily come up with
vowel_lists = [
    [first + last for last in ["a", "e", "i", "o", "u", "y"]]
    for first in ["a", "e", "o", "y", ""]
]
vowels = [vowel for sublist in vowel_lists for vowel in sublist]

implemented_genders = {
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

gender_synonyms = {
    "male": "male",
    "m": "male",
    "man": "male",
    "masc": "male",
    "masculine": "male",
    "boy": "male",
    "female": "female",
    "f": "female",
    "woman": "female",
    "fem": "female",
    "femme": "female",
    "feminine": "female",
    "girl": "female",
    "neutral": "neutral",
    "neuter": "neuter",
    "enby": "neutral",
    "nonbinary": "neutral",
    "nb": "neutral",
    "non-binary": "neutral",
    "n": "neutral",
    "other": "neutral",
}

def generate_name(parameters):
    """Generate a name based on the given dictionary. The dictionary can contain the race, subrace, gender, name types, and beginnings of the first and/or last names."""

    race_path = get_race(parameters)
    gender = get_gender(parameters)
    

    with open(config_path) as config_file:
        config = json.load(config_file)
        name = config["structure"]


        types = (
            param["types"] if "types" in param else ["first"]
        )  # First name is the most important, so it's the default

        for name_type in types:
            components = config["components"]

            if name_type in components:
                structure_choice = {}

                # Use the user-specified gender and gender-neutral options
                possible_structures = (
                    components[name_type][gender]
                    if (gender in components[name_type])
                    else []
                ) + (
                    components[name_type]["all"]
                    if "all" in (components[name_type])
                    else []
                )

                if possible_structures:
                    structure_choice = weighted_choice(possible_structures)
                else:
                    return None  # User-specified gender not found, and no gender-neutral structures

                name_part = structure_choice[
                    "structure"
                ]  # The part of the full name (e.g. the first name or the last name)
                tokens = re.findall("<(.*?)>", name_part)
                for token in tokens:
                    token_lower = token.lower()

                    # The number of arguments keeps getting longer as I write this
                    name_token = generate_token(
                        race_path, structure_choice, token.lower(), config, param, gender
                    )
                    name_part = name_part.replace("<" + token.upper() + ">", name_token)

                name = name.replace("<" + name_type.upper() + ">", name_part)

    name = re.sub(r"<(.*?)>", "", name)
    name = name.strip()
    return name



def generate_token(race_path, structure_choice, token_name, config, param, gender):
    token_info = structure_choice["components"][token_name]
    token_file = ""
    token_choice = []
    no_file = False

    starts_with = ""
    if token_name == "first":
        starts_with = param["first starts with"] if "first starts with" in param else ""
    elif token_name == "last":
        starts_with = param["last starts with"] if "last starts with" in param else ""

    state_size = config["state_size"]

    join_char = ""
    if "join" in structure_choice:
        join_char = structure_choice["join"]

    max_syllables = 0
    if "syllables" in param and param["syllables"] != "" and param["syllables"] > 0:
        max_syllables = param["syllables"]
    elif "max_syllables" in config:
        max_syllables = config["max_syllables"]

    capitalize = True
    if "capitalize" in token_info:
        capitalize = token_info["capitalize"]

    generated_name = ""

    if "file" in token_info:
        if token_info["file"]:
            token_file = race_path + os.sep + token_info["file"]
            with open(token_file) as tf:
                if "select" in token_info:
                    if token_info["select"]:
                        # Select one name from the file
                        names = tf.read().splitlines()
                        generated_name = random.choice(names)
                    else:
                        # Markov chain a name
                        text_model = markovify.NewlineText(
                            tf.read(), state_size=state_size
                        )
                        generated_name = markov_generate_name(
                            text_model,
                            starts_with,
                            state_size,
                            max_syllables,
                            join_char,
                            capitalize,
                            gender,
                        )
        else:
            no_file = True
    else:
        no_file = True

    if no_file:
        if "choice" in token_info:
            if token_info["choice"]:
                token_choice = token_info["choice"]
                if "select" in token_info:
                    if token_info["select"]:
                        # Select one name from the file
                        generated_name = random.choice(token_choice)
                    else:
                        # Markov chain a name
                        text_model = markovify.Text(token_choice, state_size=state_size)
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
    if gender in implemented_genders:
        for gendered_word in implemented_genders[gender]:
            name = name.replace(
                gendered_word.upper(), implemented_genders[gender][gendered_word]
            )

    return name






if __name__ == "__main__":
    race = input("Race    : ")
    subrace = input("Subrace : ")
    gender = input("Gender  : ")
    user_types = input("Types   : ")
    types = "".join(user_types.split()).split(",") if user_types != "" else ["first"]
    param = {"race": race, "subrace": subrace, "gender": gender, "types": types}
    print(generate_name(param))