from error import UnknownRaceError, UnknownSubraceError, UnknownGenderError

def get_race(parameters):
    """Parses the race from the parameter dictionary. If the dict contains a "race" key, and the value is a valid race, that race is chosen. If no race is given, a random race is selected. If the given race is not valid, an UnknownRaceError is raised."""
    
    # the directory containing all the races.json config file specifying all the available races
    race_dir_path = f".{os.sep}names{os.sep}"

    with open(f"{race_dir_path}races.json") as races_file:
        valid_races = json.load(races_file)

        # if the race is unspecified, we'll choose a random race to generate a name for
        if "race" in parameters and parameters["race"] in valid_races["synonyms"]:
            standard_race_name = valid_races["synonyms"][parameters["race"]]
            # the races.json config file specifies the directory that contains the information for that race
            race_dir_path += valid_races["races"][standard_race_name]["directory"]
        elif ("race" in parameters and parameters["race"] == "") or ("race" not in parameters):
            # Choose a random race
            race_dir_path += weighted_choice(valid_races["races"])["directory"]
        else:
            raise UnknownRaceError(parameters["race"])  # Asking for an unknown race

def get_subrace(parameters):
    """Parses the subrace from the parameter dictionary."""
    # if the subrace is unspecified, a random one will be chosen
    subrace = param["subrace"] if "subrace" in param else ""

    # opens the correct race/subrace directory, taking into account races without subraces
    race_path = find_race_dir(race_dir_path, subrace)
    config_path = race_path + os.sep + "config.json"


def get_gender(parameters):

    gender = ""
    if "gender" in param and param["gender"] != "":
        # the actual gender the user specified
        chosen_gender = param["gender"]

        # map the given gender to one of the supported ones, if possible
        gender = (
            gender_synonyms[chosen_gender] if (chosen_gender in gender_synonyms) else ""
        )
    else:
        gender = random.choice(
            ["male", "female"]
        )  # Genders past those two are hard to account for in everything B(

def find_race_dir(race_dir_path, user_subrace):
    try:
        subrace_config = None
        with open(race_dir_path + os.sep + "race.json") as race_file:
            subrace_config = json.load(race_file)
    except:
        return race_dir_path
    else:
        subrace = ""

        if user_subrace not in subrace_config["synonyms"]:
            subrace = weighted_choice(subrace_config["subraces"])["directory"]
        else:
            subrace = subrace_config["synonyms"][user_subrace]

        return race_dir_path + os.sep + subrace

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
