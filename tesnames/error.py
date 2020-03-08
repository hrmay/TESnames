class UnknownRaceError(Exception):
    """Raised when a name for an unknown race is requested from the generator."""

    def __init__(self, race):
        self.message = f"Cannot generate name for unknown race '{race}'!"


class UnknownSubraceError(Exception):
    """Raised when a name for an unknown subrace is requested from the generator."""

    def __init__(self, race, subrace):
        self.message = (
            f"Cannot generate name for unknown subrace '{subrace}' of race '{race}'!"
        )


class UnknownGenderError(Exception):
    """Raised when a name for an unknown gender is requested from the generator."""

    def __init__(self, gender):
        self.message = f"Cannot generate name for unknown gender '{gender}'!"


class NoStructuresForGenderError(Exception):
    """Raised when no name structures exist for a given gender."""

    def __init__(self, name_type, gender):
        self.message = f"No name structures exist for name type '{name_type}' and gender '{gender}' for the given race and subrace!"