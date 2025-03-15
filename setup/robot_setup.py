import re
import json
from typing import Any, Dict, Set


# TODO: use input data as f string
def extract_placeholders_from_robot(json_data: Dict[str, Any]) -> Set[str]:
    """
    Extracts placeholders from 'Robot' start_code[value] and end_code[value] in the JSON data.

    ARGUMENTS:
    json_data: The loaded JSON object (dictionary).

    RETURNS:
    A set of placeholders found in 'Robot' start_code[value] and end_code[value].
    """
    placeholders = set()

    def search_for_placeholders(code_list: list):
        """Searches for placeholders inside a list of strings."""
        if isinstance(code_list, list):
            for line in code_list:
                if isinstance(line, str):
                    matches = re.findall(r"\{([a-zA-Z0-9_]+)}", line)
                    placeholders.update(matches)

    # Access only 'start_code[value]' and 'end_code[value]'
    robot_section = json_data.get("settings", {}).get("Robot", {})
    start_code = robot_section.get("start_code", {}).get("value", [])
    end_code = robot_section.get("end_code", {}).get("value", [])

    # Extract placeholders only from start_code[value] and end_code[value]
    search_for_placeholders(start_code)
    search_for_placeholders(end_code)

    return placeholders


def replace_placeholders(
    json_data: Dict[str, Any], placeholders: Set[str]
) -> Dict[str, Any]:
    """
    Replaces placeholders in 'Robot' start_code[value] and end_code[value] with JSON values.

    ARGUMENTS:
    json_data: Loaded JSON object (dictionary).
    placeholders: Set of placeholder names to replace.

    RETURNS:
    A dictionary with the replaced values for the placeholders.
    """
    replaced_values = {}

    def find_value_for_placeholder(placeholder: str, data: Any) -> Any:
        """Finds the value for a placeholder inside the JSON."""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == placeholder and isinstance(value, dict) and "value" in value:
                    return value["value"]
                result = find_value_for_placeholder(placeholder, value)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = find_value_for_placeholder(placeholder, item)
                if result is not None:
                    return result
        return None

    for placeholder in placeholders:
        value = find_value_for_placeholder(placeholder, json_data)
        if value is not None:
            if isinstance(value, dict):
                value = ", ".join(f"{key} {val}" for key, val in value.items())
            replaced_values[placeholder] = value
        else:
            print(
                f"[WARNING] Placeholder '{{{placeholder}}}' has no matching value in the JSON!"
            )

    return replaced_values


def apply_replacements_to_robot(
    json_data: Dict[str, Any], replacements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Applies placeholder replacements to 'start_code[value]' and 'end_code[value]' in the Robot section.

    ARGUMENTS:
    json_data: Loaded JSON object (dictionary).
    replacements: Dictionary of placeholder values.

    RETURNS:
    Updated 'Robot' section with placeholders replaced.
    """

    def convert_value_to_string(value: Any) -> str:
        """Converts a value to a string based on its type."""
        if isinstance(value, dict):
            return ", ".join(
                f"{key} {convert_value_to_string(val)}" for key, val in value.items()
            )
        elif isinstance(value, list):
            return f"[{', '.join(map(convert_value_to_string, value))}]"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, int):
            return str(value)
        return value

    def replace_placeholders_in_list(code_list: list[str]) -> list[str]:
        """Replaces placeholders inside a list of strings."""
        updated_list = []
        for line in code_list:
            if isinstance(line, str):
                for placeholder, replacement in replacements.items():
                    replacement_str = convert_value_to_string(replacement)
                    line = line.replace(f"{{{placeholder}}}", replacement_str)

                # Warn if placeholders are still present in the line
                remaining_placeholders = re.findall(r"\{([a-zA-Z0-9_]+)}", line)
                if remaining_placeholders:
                    for missing_placeholder in remaining_placeholders:
                        print(
                            f"[WARNING] Placeholder '{{{missing_placeholder}}}' was not replaced in line: {line}"
                        )

            updated_list.append(line)
        return updated_list

    robot_section = json_data.get("settings", {}).get("Robot", {})
    start_code = robot_section.get("start_code", {}).get("value", [])
    end_code = robot_section.get("end_code", {}).get("value", [])

    # Ensure start_code and end_code remain lists of strings
    robot_section["start_code"]["value"] = replace_placeholders_in_list(start_code)
    robot_section["end_code"]["value"] = replace_placeholders_in_list(end_code)

    return robot_section


def get_robot_settings(json_file: str) -> Dict[str, Any]:
    """
    Extracts and replaces placeholders in 'Robot' start_code[value] and end_code[value],
    and returns specific robot settings.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    Dictionary of relevant robot setup configurations.
    """
    with open(json_file, "r") as file:
        config = json.load(file)

    placeholders = extract_placeholders_from_robot(config)
    placeholder_values = replace_placeholders(config, placeholders)
    updated_robot_section = apply_replacements_to_robot(config, placeholder_values)

    return {
        "id": updated_robot_section.get("id", {}).get("value"),
        "geometry": updated_robot_section.get("geometry", {}).get("value"),
        "base_coordinates": updated_robot_section.get("base_coordinates", {}).get(
            "value"
        ),
        "tool_offset": updated_robot_section.get("tool_offset", {}).get("value"),
        "tool_orientation": updated_robot_section.get("tool_orientation", {}).get(
            "value"
        ),
        "start_position": updated_robot_section.get("start_position", {}).get("value"),
        "end_position": updated_robot_section.get("end_position", {}).get("value"),
        "rotation_limit": updated_robot_section.get("rotation_limit", {}).get("value"),
        "rotation_sign": updated_robot_section.get("rotation_sign", {}).get("value"),
        "rotation_offset": updated_robot_section.get("rotation_offset", {}).get(
            "value"
        ),
        "base_radius": updated_robot_section.get("base_radius", {}).get("value"),
        "start_code": updated_robot_section.get("start_code", {}).get("value", []),
        "end_code": updated_robot_section.get("end_code", {}).get("value", []),
        "bed_size": updated_robot_section.get("bed_size", {}).get("value"),
        "tool_coordinates": updated_robot_section.get("tool_coordinates", {}).get(
            "value"
        ),
        "print_speed": updated_robot_section.get("print_speed", {}).get("value"),
        "type_number": updated_robot_section.get("type_number", {}).get("value"),
    }
