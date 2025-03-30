import json
from typing import Any, Dict


def load_settings(json_path: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    DESCRIPTION:
    Loads the 'settings' section from a JSON file and returns a nested dict:

    :param json_path: path to the printer parameter .json file
    :return: nested dict -> settings[section][key] = {"value": ..., "type": ..., "description": ...}
    """

    # opens .json file and reads file with utf-8 standard
    with open(json_path, "r", encoding="utf-8") as file:
        full_config = json.load(file)

    # search full_config for "settings" key
    raw_settings = full_config.get("settings", {})

    # empty dict to be filled
    structured_settings: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # building the nested dict for every available section under "settings"
    for section, entries in raw_settings.items():
        structured_settings[section] = {}
        for key, entry in entries.items():
            if isinstance(entry, dict) and "value" in entry and "type" in entry:
                structured_settings[section][key] = {
                    "value": entry["value"],
                    "type": entry["type"],
                    "description": entry.get("description", ""),
                }

    return structured_settings


if __name__ == "__main__":
    from pathlib import Path

    # Setup-Pfad
    setup_path = f"{Path(__file__).parent / "setup.json"}"

    # Lade Settings
    settings = load_settings(setup_path)
    print(settings)
