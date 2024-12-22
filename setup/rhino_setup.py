import json
from typing import Dict, Any


def get_rhino_settings(json_file: str) -> dict[str, Any]:
    """
    DESCRIPTION:
    Extracts Rhino settings from the JSON file and returns them in a formatted dictionary.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    A dictionary with formatted Rhino settings, including TYPE_VALUES
    with attributes like CURA, ORCA, Color, and Linetype.
    """
    # Load the JSON file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Access the "Rhino" section in "settings"
    rhino_config = config["settings"]["Rhino"]

    # Access "TYPE_VALUES" and format the data
    raw_type_values = rhino_config["TYPE_VALUES"]
    formatted_type_values = {
        key: {
            "CURA": value.get("CURA", []),
            "ORCA": value.get("ORCA", []),
            "Color": value["color"]["value"],
            "Linetype": value["linetype"]["value"],
        }
        for key, value in raw_type_values.items()
    }

    # Return a dictionary with all Rhino settings
    return {
        "TYPE_VALUES": formatted_type_values,
    }
