import json
from typing import Dict, Any


def get_slicer_settings(json_file: str) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Extracts slicer settings from a JSON file based on the slicer name.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    A dictionary with slicer settings [slicer_name, slicer_cmd_path,
    slicer_config_file_path, slicer_arguments].
    """
    # Load the JSON file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Extract slicer name
    slicer_name = config["settings"]["Slicer"]["slicer_name"]["value"].upper()

    # Ensure the slicer exists in the JSON
    if slicer_name not in config["settings"]["Slicer"]:
        raise KeyError(f"Slicer '{slicer_name}' not found in JSON settings.")

    # Access the slicer-specific settings
    slicer_section = config["settings"]["Slicer"][slicer_name]

    # Dynamically build the correct keys based on the slicer name
    slicer_settings = {
        "slicer_name": slicer_name,
        "slicer_cmd_path": slicer_section[f"{slicer_name.lower()}_cmd_path"]["value"],
        "slicer_config_file_path": slicer_section[
            f"{slicer_name.lower()}_config_file_path"
        ]["value"],
        "slicer_arguments": slicer_section[f"{slicer_name.lower()}_arguments"]["value"],
        "slicer_scaling": slicer_section[f"{slicer_name.lower()}_scaling"]["value"],
    }

    return slicer_settings
