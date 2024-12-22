import re
import json
from typing import Dict, Any, Set

def extract_placeholders_from_robot(json_data: Dict[str, Any]) -> Set[str]:
    """
    DESCRIPTION:
    Extracts placeholders from the 'Robot' section of the JSON data, excluding certain keys.

    ARGUMENTS:
    json_data: The loaded JSON object (dictionary).

    RETURNS:
    A set of placeholders found in the 'Robot' section.
    """
    placeholders = set()
    excluded_keys = {"description"}  # Keys to exclude from placeholder search

    def recursive_search(data: Any, parent_key: str = None):
        if isinstance(data, dict):
            for key, value in data.items():
                # Skip keys in the exclusion list
                if key in excluded_keys:
                    continue
                recursive_search(value, key)
        elif isinstance(data, list):
            for item in data:
                recursive_search(item)
        elif isinstance(data, str):
            # Look for placeholders in the string
            matches = re.findall(r"\{([a-zA-Z_]+)\}", data)
            placeholders.update(matches)

    # Start search only in the 'Robot' section
    robot_section = json_data.get("settings", {}).get("Robot", {})
    recursive_search(robot_section)
    return placeholders


def replace_placeholders(
    json_data: Dict[str, Any], placeholders: Set[str]
) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Replaces placeholders in the entire JSON file with their corresponding values.

    ARGUMENTS:
    json_data: Loaded JSON object (dictionary).
    placeholders: Set of placeholder names to replace.

    RETURNS:
    A dictionary of placeholders and their corresponding values.
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
                # Check if the current key matches the placeholder and contains a "value"
                if key == placeholder and isinstance(value, dict) and "value" in value:
                    return value["value"]

                # Recursive search in subcategories
                result = find_value_for_placeholder(placeholder, value)
                if result is not None:
                    return result

        elif isinstance(data, list):
            for item in data:
                result = find_value_for_placeholder(placeholder, item)
                if result is not None:
                    return result

        return None

    # Search for each placeholder in the JSON
    for placeholder in placeholders:
        value = find_value_for_placeholder(placeholder, json_data)

        # Special handling for `output_name`: truncate to max. 25 characters
        if placeholder == "output_name" and value is not None:
            value = value[:25]

        if value is not None:
            replaced_values[placeholder] = value

    return replaced_values


def apply_replacements_to_robot(
    json_data: Dict[str, Any], replacements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Applies the replaced placeholder values to the 'Robot' section.

    ARGUMENTS:
    json_data: Loaded JSON object (dictionary).
    replacements: Dictionary of placeholder values.

    RETURNS:
    Updated 'Robot' section with placeholders replaced.
    """
    def recursive_replace(data: Any) -> Any:
        if isinstance(data, dict):
            return {key: recursive_replace(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [recursive_replace(item) for item in data]
        elif isinstance(data, str):
            # Replace all placeholders in the string
            for placeholder, replacement in replacements.items():
                data = data.replace(f"{{{placeholder}}}", str(replacement))
            return data
        return data

    # Replace values only in the 'Robot' section
    robot_section = json_data.get("settings", {}).get("Robot", {})
    return recursive_replace(robot_section)


def get_robot_settings(json_file: str) -> Dict[str, Any]:
    """
    DESCRIPTION:
    Extracts and replaces placeholders in the 'Robot' section of the JSON file.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    Dictionary of relevant robot setup configurations.
    """
    # Load the JSON file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Step 1: Extract placeholders
    placeholders = extract_placeholders_from_robot(config)

    # Step 2: Replace placeholders with their values
    placeholder_values = replace_placeholders(config, placeholders)

    # Step 3: Apply replacements to the Robot section
    updated_robot_section = apply_replacements_to_robot(config, placeholder_values)

    # Return relevant robot setup values
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
        "start_code": updated_robot_section.get("start_code", {}).get("value"),
        "end_code": updated_robot_section.get("end_code", {}).get("value"),
    }
