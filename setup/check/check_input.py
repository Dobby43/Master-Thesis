import json
from typing import Any, Dict, Tuple


def validate_json_types(json_file: str) -> bool:
    """
    DESCRIPTION:
    Validates if the "value" in the JSON matches its corresponding "type".
    Exceptions: int and float are treated as the same type.

    ARGUMENTS:
    json_file: Path to the JSON file.

    RETURNS:
    bool: True if all values match their types, False otherwise.
    """

    with open(json_file, "r") as file:
        config = json.load(file)

    is_valid = True

    def parse_expected_type(type_str: str) -> str:
        """
        Extracts the main type from type annotations like 'dict[str,float]'.
        """
        return type_str.split("[")[0].strip()

    def check_type(value: Any, expected_type: str, key_path: str):
        nonlocal is_valid
        actual_type = type(value).__name__
        expected_base_type = parse_expected_type(expected_type)

        if expected_base_type == "float" and actual_type == "int":
            return  # Allow int where float is expected
        if expected_base_type == "int" and actual_type == "float":
            return  # Allow float where int is expected

        if actual_type != expected_base_type:
            print(
                f"[ERROR] Type mismatch at '{key_path}': expected '{expected_base_type}', got '{actual_type}'."
            )
            is_valid = False

    def recursive_validate(data: Dict[str, Any], parent_path: str = ""):
        if isinstance(data, dict):
            for key, value in data.items():
                key_path = f"{parent_path}.{key}" if parent_path else key

                if isinstance(value, dict) and "value" in value and "type" in value:
                    check_type(value["value"], value["type"], key_path)
                else:
                    recursive_validate(value, key_path)

    recursive_validate(config)
    return is_valid


# Example usage
if __name__ == "__main__":
    json_file_path = r"C:\Users\daves\Master-Thesis\setup\setup.json"  # Replace with your JSON file path
    valid = validate_json_types(json_file_path)
    print("Validation Result:", "Passed" if valid else "Failed")
