class UnknownRaceError(Exception):
    """Raised when a name for an unknown race is requested from the generator."""

    def __init__(self, race):
        self.message = f"Cannot generate name for unknown race '{race}'!"


class UnknownSubraceError(Exception):
    """Raised when a name for an unknown subrace is requested from the generator."""

    def __init__(self, race, subrace):
        self.message = f"Cannot generate name for unknown subrace '{subrace}' of race '{race}'!"


class UnknownGenderError(Exception):
    """Raised when a name for an unknown gender is requested from the generator."""

    def __init__(self, gender):
        self.message = f"Cannot generate name for unknown gender '{gender}'!"
