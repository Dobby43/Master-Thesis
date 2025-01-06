import json


def extract_slicer_arguments(config_path: str) -> dict[str, dict[str, any]]:
    """
    DESCRIPTION:
    Extracts all slicer arguments, including default_value, type, and options (for enums),
    from a JSON configuration file.

    ARGUMENTS:
    config_path: Path to the slicer configuration JSON file.

    RETURNS:
    A dictionary with all slicer arguments:
    {
        "argument_name": {
            "default_value": ...,
            "type": ...,
            "raw_type": ...,
            "options": [...],  # Only for type:"enum"
        },
        ...
    }
    """
    with open(config_path, "r") as file:
        config = json.load(file)

    extracted_arguments = {}

    def recursive_extract(data):
        if isinstance(data, dict):
            for key, value in data.items():
                # Only process if value is a dict and contains 'default_value' and 'type'
                if (
                    isinstance(value, dict)
                    and "default_value" in value
                    and "type" in value
                ):
                    extracted_arguments[key] = {
                        "default_value": value["default_value"],
                        "type": value["type"],  # Known type or custom
                        "raw_type": type(
                            value["default_value"]
                        ).__name__,  # Python-detected type
                    }
                    # Extract options for enums
                    if value["type"] == "enum" and "options" in value:
                        extracted_arguments[key]["options"] = list(
                            value["options"].keys()
                        )
                # Recurse into nested dictionaries
                if isinstance(value, (dict, list)):
                    recursive_extract(value)
        elif isinstance(data, list):
            for item in data:
                recursive_extract(item)

    # Start the recursive extraction
    recursive_extract(config.get("settings", {}))
    return extracted_arguments


# Example usage
if __name__ == "__main__":
    config_path = r"C:\Program Files\UltiMaker Cura 5.8.1\share\cura\resources\definitions\12_command_line_settings_fdmprinter.def - Kopie.json"  # Replace with the actual path
    slicer_arguments = extract_slicer_arguments(config_path)
    print(json.dumps(slicer_arguments, indent=4))
