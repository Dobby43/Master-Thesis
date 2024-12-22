import json


def get_slicer_settings(json_file):
    """
    Extrahiert die Slicer-Einstellungen aus der JSON-Datei.

    :param json_file: Pfad zur JSON-Datei mit den Konfigurationsinformationen
    :return: Dictionary mit den Slicer-Einstellungen
    """
    # JSON-Datei laden
    with open(json_file, "r") as file:
        config = json.load(file)

    # Slicer-Einstellungen extrahieren
    slicer_settings = {
        "slicer_name": config["settings"]["Slicer"]["slicer_name"]["value"],
        "slicer_cmd_path": config["settings"]["Slicer"]["slicer_cmd_path"]["value"],
        "slicer_config_file_path": config["settings"]["Slicer"][
            "slicer_config_file_path"
        ]["value"],
        "slicer_arguments": config["settings"]["Slicer"]["slicer_arguments"]["value"],
    }

    return slicer_settings
