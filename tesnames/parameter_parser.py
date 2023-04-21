import random
import os
import json

from .choice import weighted_choice
from .error import UnknownRaceError, UnknownSubraceError, UnknownGenderError

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

ABSOLUTE_PATH = os.path.dirname(__file__)


def parse_params(parameters):
    """Parses all the parameters from parameter dictionary. If any keys aren't provided, a default or random value will be selected."""
    
    race, subrace = get_race_and_subrace(parameters)
    gender = get_gender(parameters)
    syllables = get_syllables(parameters)
    types = (
        parameters["types"] if "types" in parameters else ["first"]
    ) # First name is the most important, so it's the default
    
    params = {
        "race": race,
        "subrace": subrace,
        "gender": gender,
        "types": types,
        "syllables": syllables
    }
    
    for name_type in types:
        starts_with = get_starts_with(parameters, name_type)
        if starts_with != "":
            params[f"{name_type} starts with"] = starts_with
    
    return params


def get_race(parameters):
    """Parses the race from the parameter dictionary. If the dict contains a "race" key, and the value is a valid race, that race is chosen. If no race is given, a random race is selected. If the given race is not valid, an UnknownRaceError is raised."""

    race = ""

    with open(os.path.join(ABSOLUTE_PATH, "names/races.json")) as races_file:
        valid_races = json.load(races_file)

        # if the race is unspecified, we'll choose a random race to generate a name for
        if "race" in parameters and parameters["race"] in valid_races["synonyms"]:
            chosen_race = parameters["race"]

            race_name = valid_races["synonyms"][chosen_race]
            race = valid_races["races"][race_name]["directory"]
        elif ("race" in parameters and parameters["race"] == "") or (
            "race" not in parameters
        ):
            # Choose a random race
            race = weighted_choice(valid_races["races"])["directory"]
        else:
            raise UnknownRaceError(parameters["race"])  # Asking for an unknown race

    return race


def get_race_and_subrace(parameters):
    """Parses the race and subrace from the parameter dictionary, or randomly selects them if unspecified. Returns them in the form (race, subrace)."""

    race = get_race(parameters)

    subrace = ""

    with open(os.path.join(ABSOLUTE_PATH, f"names/{race}/race.json")) as race_file:
        valid_subraces = json.load(race_file)

        # if the subrace is unspecified, we'll choose a random subrace to generate a name for
        if (
            "subrace" in parameters
            and parameters["subrace"] in valid_subraces["synonyms"]
        ):
            chosen_subrace = parameters["subrace"]

            subrace_name = valid_subraces["synonyms"][chosen_subrace]
            subrace = valid_subraces["subraces"][subrace_name]["directory"]
        elif ("subrace" in parameters and parameters["subrace"] == "") or (
            "subrace" not in parameters
        ):
            # Choose a random race
            subrace = weighted_choice(valid_subraces["subraces"])["directory"]
        else:
            raise UnknownSubraceError(
                parameters["race"], parameters["subrace"]
            )  # Asking for an unknown subrace

    return race, subrace


def get_race_path(race, subrace):
    """Returns the path to the directory containing information used to generate that race's names."""

    return os.path.join(ABSOLUTE_PATH, f"names/{race}/{subrace}")


def get_gender(parameters):
    """Parses the gender from the parameter dictionary. If no gender is specified, "male" or "female" is randomly chosen. If the specified gender doesn't exist, an UnknownGenderError is raised."""

    gender = ""
    if "gender" in parameters and parameters["gender"] != "":
        # the actual gender the user specified
        chosen_gender = parameters["gender"]

        # map the given gender to one of the supported ones, if possible
        if chosen_gender in gender_synonyms:
            gender = gender_synonyms[chosen_gender]
        else:
            raise UnknownGenderError(chosen_gender)
    else:
        gender = random.choice(
            ["male", "female"]
        )  # Genders past those two are hard to account for in everything B(

    return gender


def get_starts_with(parameters, name_type):
    """Gets the character a name type must start with, if any."""

    return (
        parameters[f"{name_type} starts with"]
        if f"{name_type} starts with" in parameters
        else ""
    )


def get_syllables(parameters):
    """Gets the number of syllables the name should be. If the given number of syllables is improper, return 0."""

    if (
        "syllables" in parameters
        and parameters["syllables"] != ""
        and parameters["syllables"] > 0
    ):
        return parameters["syllables"]
    else:
        return 0
