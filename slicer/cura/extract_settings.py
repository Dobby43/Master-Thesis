import json
from pathlib import Path
from slicer.cura.preset_arguments import def_preset_arguments


def load_json(filepath):
    """
    DESCRIPTION:
    Loads a .json file from the given filepath

    :param filepath: path to .json file
    :return: Parsed JSON content as a Python object
    """

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_settings(data):
    """
    DESCRIPTION:
    Extracts all settings from the JSON structure under "settings," not just the deepest ones.
    - Stores 'Key', 'Type', and 'Default Value'.
    - If 'enum', also stores the available 'options'.

    :param data: input from loaded .json file

    :return: nested dict consisting of parent key and every child under parent given in for example printer_configuration
    (Example: {'roofing_line_width': {'value': 25, 'type': 'float'}, 'roofing_pattern': {'value': 'lines', 'type': 'enum', 'options': ['lines', 'concentric', 'zigzag']}}
    """

    extracted_data = {}

    for key, value in data.items():  # Sets new key for every key-value pair
        if isinstance(value, dict):
            if "type" in value and "default_value" in value:
                setting_entry = {"value": value["default_value"], "type": value["type"]}

                if value["type"] == "enum" and "options" in value:
                    setting_entry["options"] = list(value["options"].keys())

                extracted_data[key] = setting_entry

            if "children" in value and isinstance(value["children"], dict):
                extracted_data.update(extract_settings(value["children"]))

    return extracted_data


def validate_user_arguments(
    user_arguments: dict[str, str],
    printer_default: dict[str, dict],
    extruder_default: dict[str, dict],
) -> dict[str, str]:
    """
    DESCRIPTION:
    Validates user arguments against the default printer and extruder settings.
    Returns a dictionary of validated arguments.

    :param user_arguments: input from loaded setup.json file
    :param printer_default: default printer settings
    :param extruder_default: default extruder settings

    :return: A dictionary of validated user inputs.
    """

    validated_arguments = {}

    for key, user_value in user_arguments.items():
        base_entries = []

        # Searches in both the extruder and the printer settings for comparable key
        if key in printer_default:
            base_entries.append(printer_default[key])
        if key in extruder_default:
            base_entries.append(extruder_default[key])

        # If key not in printer or extruder, key and value get ignored and default is used
        if not base_entries:
            print(
                f"[WARNING] Key '{key}' has no matching key in Cura settings and is therefore ignored."
            )
            print(f"[INFO] Check for a typo in setup.json for '{key}'.")
            continue

        for base_data in base_entries:
            expected_type = base_data.get("type")

            # Handle type conversion and validation
            try:
                if expected_type == "float":
                    validated_value = float(user_value)
                elif expected_type == "int":
                    validated_value = int(user_value)
                elif expected_type == "bool":
                    if str(user_value.lower()) in {"true", "1"}:
                        validated_value = True
                    elif str(user_value.lower()) in {"false", "0"}:
                        validated_value = False
                    else:
                        raise ValueError(f"Invalid boolean value: {user_value}")
                elif expected_type == "enum":
                    options = base_data.get("options", [])
                    if user_value not in options:
                        print(
                            f"[WARNING] Key '{key}' from setup.json has an invalid value ('{user_value}')."
                        )
                        print(f"[INFO] Choose a valid option: {options}.")
                        continue  # Invalid value not taken into account
                    validated_value = user_value
                elif expected_type == "str":
                    validated_value = str(user_value)
                else:
                    print(
                        f"[WARNING] Unsupported type '{expected_type}' for key '{key}' in setup.json. Skipping."
                    )
                    continue

                # Saves valid arguments dictionary of valid arguments
                validated_arguments[key] = validated_value
                print(f"[INFO] {key} = {validated_value} from setup.json is valid")

            except ValueError:
                print(
                    f"[WARNING] Key '{key}' from setup.json has an invalid type and is therefor ignored."
                )

    return validated_arguments


def final_arguments(
    validated_arguments: dict[str, str], preset_arguments: dict[str, any]
) -> dict[str, str]:
    """
    DESCRIPTION:
    Combines validated user arguments with preset arguments.
    Preset arguments take precedence if a key from Preset arguments appears in validated_arguments.

    :param validated_arguments: Dictionary of user-specified and validated arguments.
    :param preset_arguments: Dictionary of preset arguments.

    :return: A final dictionary with user values + presets applied.
    """
    final_args = preset_arguments
    # Overwrites validated user argument with value from key in preset arguments
    for key, value in validated_arguments.items():
        if key in preset_arguments:
            print(
                f"[WARNING] Preset value applied for '{key}': {preset_arguments[key]}"
            )
        else:
            final_args[key] = value

    return final_args


if __name__ == "__main__":
    base_file_path_printer = str(
        Path(__file__).parent / "default" / "TUM_C3DP_fdmprinter.def.json"
    )
    base_file_path_extruder = str(
        Path(__file__).parent / "default" / "TUM_C3DP_fdmextruder.def.json"
    )

    print("[INFO] Loading default settings...")
    base_data_printer = load_json(base_file_path_printer)
    printer_basic_values = extract_settings(base_data_printer.get("settings", {}))

    base_data_extruder = load_json(base_file_path_extruder)
    extruder_basic_values = extract_settings(base_data_extruder.get("settings", {}))

    # User-Argumente direkt als Dictionary
    user_arguments = {
        "layer_height_0": "15",
        "layer_height": "15",
        "infill_sparse_density": "20",
        "roofing_layer_count": "1",
        "mesh_position_x": "412.5",
        "retraction_enable": "true",
        "infill_pattern": "invalid_option",
    }

    # Maschinen-Parameter für die Presets definieren
    machine_name = "My_3D_Printer"
    bed_size = {"X": 300, "Y": 300, "Z": 400}
    flow = {
        "wall_outer": 100,
        "wall_inner": 100,
        "surface": 100,
        "infill": 100,
        "bridge": 100,
        "curb": 100,
        "support": 100,
        "unknown": 100,
    }
    pump_retract = False
    scaling = "[[1,0,0];[0,1,0];[0,0,1]]"
    filament_dia = 1.75

    print("[INFO] Validating and updating user arguments...")
    validated_user_arguments = validate_user_arguments(
        user_arguments, printer_basic_values, extruder_basic_values
    )

    preset_argument = def_preset_arguments(
        machine_name, bed_size, flow, pump_retract, scaling, filament_dia
    )

    final_arguments = final_arguments(validated_user_arguments, preset_argument)
    print(final_arguments)
