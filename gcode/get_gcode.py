from pathlib import Path


def get_gcode_lines(directory: str, file_name: str) -> list[str]:
    """
    DESCRIPTION:
    Reads a G-code file from the specified directory and returns its lines as a list.

    ARGUMENTS:
    directory: The directory where the G-code file is located.
    file_name: The name of the G-code file.

    RETURNS:
    A list of lines from the G-code file, where each line is a string containing one line of G-code.
    """
    # Combine the directory and file name using Path
    file_path = Path(directory) / file_name

    # Try statement for redundancy as it saves an empty list
    try:
        with open(file_path, "r") as file:
            gcode_lines = file.readlines()
            return gcode_lines
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []
