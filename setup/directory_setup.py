import os
import json
from datetime import datetime


def get_directory_setup(json_file):
    """
    Extrahiert die Input- und Output-Pfade aus der setup.json und erstellt einen Zeit-basierten Unterordner.

    :param json_file: Pfad zur JSON-Datei mit den Konfigurationsinformationen
    :return: Ein Dictionary mit den Input- und Output-Pfaden
    """
    # JSON-Datei laden
    with open(json_file, "r") as file:
        config = json.load(file)

    # Input STL-Pfad
    input_directory = config["settings"]["Directory"]["input_directory"]["value"]
    input_name = config["settings"]["Directory"]["input_name"]["value"]

    # Basis-Output-Verzeichnis und Name des Output-Ordners
    output_directory = config["settings"]["Directory"]["output_directory"]["value"]
    output_name = config["settings"]["Directory"]["output_name"]["value"]

    # Aktuelle Zeit für den Unterordner
    current_time = datetime.now().strftime("%H_%M_%S")
    time_subfolder = f"Data_{current_time}"
    final_output_directory = os.path.join(output_directory, time_subfolder)

    # Output-Ordner erstellen, falls nicht vorhanden
    os.makedirs(final_output_directory, exist_ok=True)

    print(f"Output directory prepared: {final_output_directory}")

    # Rückgabe der relevanten Pfade
    return {
        "input_directory": input_directory,
        "input_name": input_name,
        "output_directory": final_output_directory,
        "output_name": output_name,
    }
