from pathlib import Path


def get_gcode_lines(directory: str, file_name: str) -> list[str]:
    """
    DESCRIPTION:
    Reads a G-code file from the specified directory and returns its lines as a list.

    :param directory: The directory to search for G-code files.
    :param file_name: The name of the G-code file.

    :return: A list of lines from the G-code file.
    """
    # Combine the directory and file name using Path
    file_path = Path(directory) / file_name

    # Try statement for redundancy as it saves an empty list
    try:
        with open(file_path, "r") as file:
            gcode_lines = file.readlines()
            return gcode_lines
    except FileNotFoundError:
        print(f"[ERROR] File '{file_path}' not found.")
        return []
