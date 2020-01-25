import markovify
import json
import os
import random
import re

# Closest approximation of typical vowel sequences I can easily come up with
vowelLists = [
    [first + last for last in ["a", "e", "i", "o", "u", "y"]]
    for first in ["a", "e", "o", "y", ""]
]
vowels = [vowel for sublist in vowelLists for vowel in sublist]

implementedGenders = {
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

genderSynonyms = {
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


def generateName(param):
    # the directory containing all the races.json config file specifying all the available races
    raceDirPath = "." + os.sep + "names" + os.sep

    with open("." + os.sep + "names" + os.sep + "races.json") as racesFile:
        races = json.load(racesFile)

        # if the race is unspecified, we'll choose a random race to generate a name for
        if "race" in param and param["race"] in races["synonyms"]:
            synonym = races["synonyms"][param["race"]]
            # the races.json config file specifies the directory that contains the information for that race
            raceDirPath += races["races"][synonym]["directory"]
        elif ("race" in param and param["race"] == "") or ("race" not in param):
            # Choose a random race
            raceDirPath += weightedChoice(races["races"])["directory"]
        else:
            return None  # Asking for an unknown race

    # if the subrace is unspecified, a random one will be chosen
    subrace = param["subrace"] if "subrace" in param else ""

    # opens the correct race/subrace directory, taking into account races without subraces
    racePath = findRaceDir(raceDirPath, subrace)
    configPath = racePath + os.sep + "config.json"

    with open(configPath) as configFile:
        config = json.load(configFile)
        name = config["structure"]

        gender = ""
        if "gender" in param and param["gender"] != "":
            # the actual gender the user specified
            chosenGender = param["gender"]

            # map the given gender to one of the supported ones, if possible
            gender = (
                genderSynonyms[chosenGender] if (chosenGender in genderSynonyms) else ""
            )
        else:
            gender = random.choice(
                ["male", "female"]
            )  # Genders past those two are hard to account for in everything B(

        types = (
            param["types"] if "types" in param else ["first"]
        )  # First name is the most important, so it's the default

        for nameType in types:
            components = config["components"]

            if nameType in components:
                structureChoice = {}

                # Use the user-specified gender and gender-neutral options
                possibleStructures = (
                    components[nameType][gender]
                    if (gender in components[nameType])
                    else []
                ) + (
                    components[nameType]["all"]
                    if "all" in (components[nameType])
                    else []
                )

                if possibleStructures:
                    structureChoice = weightedChoice(possibleStructures)
                else:
                    return None  # User-specified gender not found, and no gender-neutral structures

                namePart = structureChoice[
                    "structure"
                ]  # The part of the full name (e.g. the first name or the last name)
                tokens = re.findall("<(.*?)>", namePart)
                for token in tokens:
                    tokenLower = token.lower()

                    # The number of arguments keeps getting longer as I write this
                    nameToken = generateToken(
                        racePath, structureChoice, token.lower(), config, param, gender
                    )
                    namePart = namePart.replace("<" + token.upper() + ">", nameToken)

                name = name.replace("<" + nameType.upper() + ">", namePart)

    name = re.sub(r"<(.*?)>", "", name)
    name = name.strip()
    return name


def generateToken(racePath, structureChoice, tokenName, config, param, gender):
    tokenInfo = structureChoice["components"][tokenName]
    tokenFile = ""
    tokenChoice = []
    noFile = False

    startsWith = ""
    if tokenName == "first":
        startsWith = param["first starts with"] if "first starts with" in param else ""
    elif tokenName == "last":
        startsWith = param["last starts with"] if "last starts with" in param else ""

    stateSize = config["state_size"]

    joinChar = ""
    if "join" in structureChoice:
        joinChar = structureChoice["join"]

    maxSyllables = 0
    if "syllables" in param and param["syllables"] != "" and param["syllables"] > 0:
        maxSyllables = param["syllables"]
    elif "max_syllables" in config:
        maxSyllables = config["max_syllables"]

    capitalize = True
    if "capitalize" in tokenInfo:
        capitalize = tokenInfo["capitalize"]

    generatedName = ""

    if "file" in tokenInfo:
        if tokenInfo["file"]:
            tokenFile = racePath + os.sep + tokenInfo["file"]
            with open(tokenFile) as tf:
                if "select" in tokenInfo:
                    if tokenInfo["select"]:
                        # Select one name from the file
                        names = tf.read().splitlines()
                        generatedName = random.choice(names)
                    else:
                        # Markov chain a name
                        textModel = markovify.NewlineText(
                            tf.read(), state_size=stateSize
                        )
                        generatedName = markovGenerateName(
                            textModel,
                            startsWith,
                            stateSize,
                            maxSyllables,
                            joinChar,
                            capitalize,
                            gender,
                        )
        else:
            noFile = True
    else:
        noFile = True

    if noFile:
        if "choice" in tokenInfo:
            if tokenInfo["choice"]:
                tokenChoice = tokenInfo["choice"]
                if "select" in tokenInfo:
                    if tokenInfo["select"]:
                        # Select one name from the file
                        generatedName = random.choice(tokenChoice)
                    else:
                        # Markov chain a name
                        textModel = markovify.Text(tokenChoice, state_size=stateSize)
                        generatedName = markovGenerateName(
                            textModel,
                            startsWith,
                            stateSize,
                            maxSyllables,
                            joinChar,
                            capitalize,
                            gender,
                        )

    return generatedName.title() if capitalize else generatedName


def markovGenerateName(
    textModel, startsWith, stateSize, maxSyllables, joinChar, capitalize, gender
):
    name = None
    shortEnough = int(maxSyllables) <= 0

    while name is None or not shortEnough:
        if startsWith == "":
            name = textModel.make_sentence()
        else:
            try:
                name = textModel.make_sentence_with_start(startsWith)
            except:
                return None

        if not shortEnough and name is not None:
            syllables = 0
            for vowel in vowels:
                syllables += name.count(vowel)

            if syllables <= maxSyllables:
                shortEnough = True

    name = joinChar.join(name.split())
    if gender in implementedGenders:
        for genderedWord in implementedGenders[gender]:
            name = name.replace(
                genderedWord.upper(), implementedGenders[gender][genderedWord]
            )

    return name


def findRaceDir(raceDirPath, userSubrace):
    try:
        subraceConfig = None
        with open(raceDirPath + os.sep + "race.json") as raceFile:
            subraceConfig = json.load(raceFile)
    except:
        return raceDirPath
    else:
        subrace = ""

        if userSubrace not in subraceConfig["synonyms"]:
            subrace = weightedChoice(subraceConfig["subraces"])["directory"]
        else:
            subrace = subraceConfig["synonyms"][userSubrace]

        return raceDirPath + os.sep + subrace


def weightedChoice(weightedValues):
    values = []
    weights = []

    for weightedValue in weightedValues:
        if isinstance(weightedValues, dict):
            values.append(weightedValues[weightedValue])
            weights.append(weightedValues[weightedValue]["weight"])
        elif isinstance(weightedValues, list):
            values.append(weightedValue)
            weights.append(weightedValue["weight"])

    totalWeight = sum(weights)

    # Convert the weights into ranges for a random int to be compared against
    # The lower bound of each item is the upper bound of the previous
    for i in range(1, len(weights)):
        weights[i] += weights[i - 1]

    choice = random.randint(1, totalWeight)

    for i, value in enumerate(values):
        if choice <= weights[i]:
            return value
    else:
        return None  # Should never happen


if __name__ == "__main__":
    race = input("Race    : ")
    subrace = input("Subrace : ")
    gender = input("Gender  : ")
    userTypes = input("Types   : ")
    types = "".join(userTypes.split()).split(",") if userTypes != "" else ["first"]
    param = {"race": race, "subrace": subrace, "gender": gender, "types": types}
    print(generateName(param))
