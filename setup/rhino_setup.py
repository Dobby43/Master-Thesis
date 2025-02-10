import json
from typing import Dict, Any


def get_rhino_settings(json_file: str) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Extracts relevant Rhino settings from a JSON file without validation.

    ARGUMENTS:
    json_file: Path to the JSON file.
    """
    # Load the JSON file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Access the "Rhino" section in "settings"
    rhino_config = config.get("settings", {}).get("Rhino", {})

    # Extract point_print (bool)
    point_print = rhino_config.get("point_print", {}).get("value", False)

    # Extract point_types (dict[str, str])
    point_types = {
        key: value.get("value", "")
        for key, value in rhino_config.get("point_types", {}).items()
        if isinstance(value, dict) and "value" in value
    }

    # Extract line_types (dict[str, dict[str, Any]])
    raw_line_types = rhino_config.get("line_types", {})
    line_types = {
        key: {
            "cura": value.get("cura", []),
            "orca": value.get("orca", []),
            "color": value.get("color", {}).get("value", ""),
            "linetype": value.get("linetype", {}).get("value", ""),
        }
        for key, value in raw_line_types.items()
        if isinstance(value, dict)
    }

    # Extract line_widths (dict[str, float])
    line_widths = rhino_config.get("line_widths", {}).get("value", {})

    # Return extracted settings as a dictionary
    return {
        "point_print": point_print,
        "point_types": point_types,
        "line_types": line_types,
        "line_widths": line_widths,
    }
