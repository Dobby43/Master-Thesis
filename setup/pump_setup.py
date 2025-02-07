import json


def get_pump_settings(json_file: str) -> dict[str, any]:
    """
    DESCRIPTION:
    Extracts pump settings from the JSON file and returns them in a formatted dictionary.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    All pump settings in form of a dictionary.
    """

    # Load the JSON file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Access the "Rhino" section in "settings"
    rhino_config = config["settings"]["Pump"]
    retract = rhino_config["retract"]["value"]

    # Return a dictionary with all Pump settings
    return {
        "retract": retract,
    }
