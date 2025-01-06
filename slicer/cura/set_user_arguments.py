def set_user_arguments(
    user_arguments: list[str], additional_args: dict[str, str | int | float | bool]
) -> list[str]:
    """
    DESCRIPTION:
    Extends the user arguments list with additional fixed values.

    ARGUMENTS:
    user_arguments: List of validated user arguments in the format ["key=value"].
    additional_args: Dictionary of additional key-value pairs to include, where each value is taken from a fixed
                     source in the JSON file.

    RETURNS:
    The extended list of arguments.
    """
    for key, value in additional_args.items():
        # Convert the key-value pair into the format "key:value"
        argument = f"{key}={value}"
        user_arguments.append(argument)

    return user_arguments


# Example usage in __main__
if __name__ == "__main__":
    # Fixed bed size values
    BED_SIZE_X = 1200
    BED_SIZE_Y = 4500
    BED_SIZE_Z = 2000

    # Existing validated user arguments
    validated_arguments = ["layer_height=0.2", "wall_line_width=0.5"]

    # Additional arguments from other parts of the JSON
    additional_args = {
        "machine_width": BED_SIZE_X,
        "machine_depth": BED_SIZE_Y,
        "machine_height": BED_SIZE_Z,
    }

    # Extend the user arguments with additional arguments
    extended_arguments = set_user_arguments(validated_arguments, additional_args)

    # Debug output
    print("Extended Arguments:")
    for arg in extended_arguments:
        print(arg)
