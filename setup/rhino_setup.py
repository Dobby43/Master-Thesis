import json


def get_rhino_settings(json_file):
    """
    Extrahiert die Rhino-Einstellungen aus der JSON-Datei und gibt sie in einem Dictionary zurück.
    """
    with open(json_file, "r") as file:
        config = json.load(file)

    # Zugriff auf den Abschnitt "Rhino" in "settings"
    rhino_config = config["settings"]["Rhino"]

    # Zugriff auf "type_values" und Formatieren der Daten
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

    # Rückgabe eines vollständigen Dictionaries mit allen Rhino-Einstellungen
    return {
        "TYPE_VALUES": formatted_type_values,
    }
