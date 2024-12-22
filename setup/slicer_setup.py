import json
from typing import Any


def get_slicer_settings(json_file: str) -> dict[str, Any]:
    """
    DESCRIPTION:
    Extracts slicer settings from a JSON file.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    A dictionary with slicer settings [slicer_name, slicer_cmd_path,
    slicer_config_file_path, slicer_arguments].
    """
    # Load the JSON file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Extract slicer settings
    slicer_settings = {
        "slicer_name": config["settings"]["Slicer"]["slicer_name"]["value"],
        "slicer_cmd_path": config["settings"]["Slicer"]["slicer_cmd_path"]["value"],
        "slicer_config_file_path": config["settings"]["Slicer"][
            "slicer_config_file_path"
        ]["value"],
        "slicer_arguments": config["settings"]["Slicer"]["slicer_arguments"]["value"],
    }

    return slicer_settings
