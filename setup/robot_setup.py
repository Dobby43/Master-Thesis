import re
import json
from typing import Any, Dict, Set


def extract_placeholders_from_robot(json_data: Dict[str, Any]) -> Set[str]:
    """
    DESCRIPTION:
    Extracts placeholders from the 'Robot' start and end code sections in the JSON data.

    ARGUMENTS:
    json_data: The loaded JSON object (dictionary).

    RETURNS:
    A set of placeholders found in the 'Robot' start and end code sections.
    """
    placeholders = set()

    def recursive_search(data: Any):
        if isinstance(data, dict):
            for value in data.values():
                recursive_search(value)
        elif isinstance(data, list):
            for item in data:
                recursive_search(item)
        elif isinstance(data, str):
            matches = re.findall(r"\{([a-zA-Z0-9_]+)\}", data)
            placeholders.update(matches)

    # Search only in the start and end code of the Robot section
    robot_section = json_data.get("settings", {}).get("Robot", {})
    start_code = robot_section.get("start_code", [])
    end_code = robot_section.get("end_code", [])
    recursive_search(start_code)
    recursive_search(end_code)

    return placeholders


def replace_placeholders(
    json_data: Dict[str, Any], placeholders: Set[str]
) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Replaces placeholders in the 'Robot' start and end code with corresponding values from the JSON.

    ARGUMENTS:
    json_data: Loaded JSON object (dictionary).
    placeholders: Set of placeholder names to replace.

    RETURNS:
    A dictionary with the replaced values for the placeholders.
    """
    replaced_values = {}

    def find_value_for_placeholder(placeholder: str, data: Any) -> Any:
        """
        Finds the value for a placeholder based on its name.

        ARGUMENTS:
        placeholder: Name of the placeholder.
        data: Current JSON data fragment.

        RETURNS:
        The value for the placeholder, if found.
        """
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
            # Format dictionaries as "key value, key value"
            if isinstance(value, dict):
                value = ", ".join(f"{key} {val}" for key, val in value.items())
            replaced_values[placeholder] = value

    return replaced_values


def apply_replacements_to_robot(
    json_data: Dict[str, Any], replacements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Applies placeholder replacements to 'start_code' and 'end_code' in the Robot section.

    ARGUMENTS:
    json_data: Loaded JSON object (dictionary).
    replacements: Dictionary of placeholder values.

    RETURNS:
    Updated 'Robot' section with placeholders replaced.
    """

    def convert_value_to_string(value: Any) -> str:
        """
        Converts a value to a string based on its type.
        - dict: "key value, key value"
        - list: "[item1, item2, ...]"
        - float: Rounded to 2 decimal places
        - int: As-is
        - bool: "TRUE"/"FALSE"
        - str: Returns as-is
        """
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
        """
        Replaces placeholders in a list of strings and returns the updated list.
        """
        updated_list = []
        for line in code_list:
            if isinstance(line, str):  # Ensure it's a string
                for placeholder, replacement in replacements.items():
                    # Replace the placeholder with its string representation
                    replacement_str = convert_value_to_string(replacement)
                    line = line.replace(f"{{{placeholder}}}", replacement_str)
            updated_list.append(line)
        return updated_list

    # Extract 'start_code' and 'end_code' from the Robot section
    robot_section = json_data.get("settings", {}).get("Robot", {})
    start_code = robot_section.get("start_code", {}).get("value", [])
    end_code = robot_section.get("end_code", {}).get("value", [])

    # Ensure start_code and end_code remain lists of strings
    robot_section["start_code"] = replace_placeholders_in_list(start_code)
    robot_section["end_code"] = replace_placeholders_in_list(end_code)

    return robot_section


def get_robot_settings(json_file: str) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Extracts and replaces placeholders in the 'Robot' start and end code, and returns specific robot settings.

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
        "bed_size": updated_robot_section.get("bed_size", {}).get("value"),
        "tool_orientation": updated_robot_section.get("tool_orientation", {}).get(
            "value"
        ),
        "base_coordinates": updated_robot_section.get("base_coordinates", {}).get(
            "value"
        ),
        "tool_coordinates": updated_robot_section.get("tool_coordinates", {}).get(
            "value"
        ),
        "start_position": updated_robot_section.get("start_position", {}).get("value"),
        "end_position": updated_robot_section.get("end_position", {}).get("value"),
        "print_speed": updated_robot_section.get("print_speed", {}).get("value"),
        "start_code": updated_robot_section.get("start_code", []),
        "end_code": updated_robot_section.get("end_code", []),
    }


if __name__ == "__main__":
    # Example usage
    json_file_path = "setup.json"  # Replace with your JSON file path
    robot_settings = get_robot_settings(json_file_path)
    print(json.dumps(robot_settings, indent=4))
