def validate_user_arguments(
    user_arguments: dict[str, str], default_arguments: dict[str, dict]
) -> list[str]:
    """
    Validates user arguments against default arguments and types.

    Args:
        user_arguments: User-provided arguments as key-value pairs (all values as strings).
        default_arguments: Default arguments with metadata, including default_value, type, and options.

    Returns:
        A list of validated arguments formatted as "key=value".
    """
    validated_arguments = []

    for key, user_value in user_arguments.items():
        # Check if the key exists in the default arguments
        if key not in default_arguments:
            print(f"[WARNING] Key '{key}' not found in default arguments. Skipping.")
            continue

        default_data = default_arguments[key]
        default_type = default_data.get(
            "type"
        )  # The expected type (e.g., "float", "int", "enum")

        # Handle type conversion and validation
        try:
            if default_type == "float":
                # Allow int inputs for float types
                validated_value = float(user_value)
            elif default_type == "int":
                validated_value = int(user_value)
            elif default_type == "bool":
                # Allow various representations for booleans
                if user_value.lower() in {"true", "1"}:
                    validated_value = True
                elif user_value.lower() in {"false", "0"}:
                    validated_value = False
                else:
                    raise ValueError(f"Invalid boolean value: {user_value}")
            elif default_type == "enum":
                # Ensure the user value is in the valid options
                options = list(default_data.get("options", {}).keys())
                if user_value not in options:
                    print(
                        f"[ERROR] Value '{user_value}' for key '{key}' is not a valid option. "
                        f"Valid options: {options}. Skipping."
                    )
                    continue
                validated_value = user_value
            elif default_type == "str":
                validated_value = str(user_value)
            else:
                print(
                    f"[WARNING] Unsupported type '{default_type}' for key '{key}'. Skipping."
                )
                continue

            # Add the validated argument to the list
            validated_arguments.append(f"{key}={validated_value}")

        except ValueError as e:
            print(
                f"[ERROR] Value '{user_value}' for key '{key}' is invalid for type '{default_type}'. Skipping."
            )

    return validated_arguments


if __name__ == "__main__":
    # Define sample user arguments
    user_arguments = {
        "layer_height": "0.5",  # Valid float
        "wall_line_width": "5",  # Valid int for a float
        "inset_direction": "inside_out",  # Invalid enum value
        "unknown_key": "value",  # Unknown key
        "layer_height": "0.3",  # Duplicate key (should override the previous one)
    }

    # Define sample default arguments
    default_arguments = {
        "layer_height": {"default_value": 2, "type": "int", "raw_type": "float"},
        "wall_line_width": {"default_value": 1, "type": "float", "raw_type": "int"},
        "inset_direction": {
            "default_value": "inside_out",
            "type": "enum",
            "raw_type": "str",
            "options": {
                "inside_out": "Inside To Outside",
                "outside_in": "Outside To Inside",
            },
        },
    }

    # Call the validation function
    validated_arguments = validate_user_arguments(user_arguments, default_arguments)

    # Output the results
    print("\nValidated Arguments:")
    print(validated_arguments)
