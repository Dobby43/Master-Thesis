import json


def get_rhino_settings(json_file: str) -> dict[str, any]:
    """
    DESCRIPTION:
    Extracts Rhino settings from the JSON file and returns them in a formatted dictionary.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    A dictionary with formatted Rhino settings, including TYPE_VALUES
    with attributes like CURA, ORCA, Color, and Linetype.
    """
    # TODO: only import necessary rhino settings, not cura and orca (only whats needed)

    # Load the JSON file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Access the "Rhino" section in "settings"
    rhino_config = config["settings"]["Rhino"]

    # Access "TYPE_VALUES" and format the data
    raw_type_values = rhino_config["type_values"]
    formatted_type_values = {
        key: {
            "cura": value.get("cura", []),
            "orca": value.get("orca", []),
            "type_number": value["type_number"]["value"],
            "color": value["color"]["value"],
            "linetype": value["linetype"]["value"],
        }
        for key, value in raw_type_values.items()
    }
    line_widths = rhino_config["line_widths"]

    # Return a dictionary with all Rhino settings
    return {
        "type_values": formatted_type_values,
        "line_widths": line_widths,
    }
