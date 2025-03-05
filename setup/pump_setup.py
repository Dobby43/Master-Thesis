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

    # Access the "Pump" section in "settings"
    pump_config = config["settings"]["Pump"]
    retract = pump_config["retract"]["value"]
    characteristic_curve = pump_config["characteristic_curve"]["value"]
    filament_diameter = pump_config["filament_diameter"]["value"]
    linetype_flow = pump_config["linetype_flow"]["value"]

    # Return a dictionary with all Pump settings
    return {
        "retract": retract,
        "characteristic_curve": characteristic_curve,
        "filament_diameter": filament_diameter,
        "linetype_flow": linetype_flow,
    }
