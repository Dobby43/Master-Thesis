from pathlib import Path

def get_gcode_lines(directory, file_name):
    """
    Reads a G-code file from the specified directory and returns the lines as a list.

    Args:
        directory (str): The directory where the G-code file is located.
        file_name (str): The name of the G-code file.

    Returns:
        list: A list of lines from the G-code file.
    """
    # Combine the directory and file name using Path
    file_path = Path(directory) / file_name

    try:
        with open(file_path, 'r') as file:
            gcode_lines = file.readlines()
        return gcode_lines
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []
