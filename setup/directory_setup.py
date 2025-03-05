import os
import json
from datetime import datetime


def get_directory_setup(json_file: str) -> dict[str, str]:
    """
    DESCRIPTION:
    Extracts input and output paths from the setup JSON file and creates a time-based subfolder in the output directory.

    ARGUMENTS:
    json_file: Path to the JSON configuration file.

    RETURNS:
    A dictionary containing:
        - input_directory: Path to the input directory.
        - input_name: Name of the input file (without extension).
        - output_directory: Path to the final output directory with a time-based subfolder.
        - output_name: Name of the output folder or files.
    """
    # Load JSON configuration file
    with open(json_file, "r") as file:
        config = json.load(file)

    # Extract input directory and file name
    input_directory = config["settings"]["Directory"]["input_directory"]["value"]
    input_name = config["settings"]["Directory"]["input_name"]["value"]

    # Extract base output directory and output name
    output_directory = config["settings"]["Directory"]["output_directory"]["value"]
    output_name = config["settings"]["Directory"]["output_name"]["value"]

    # Generate a time-based subfolder
    current_time = datetime.now().strftime("%H_%M_%S")
    time_subfolder = f"{output_name}_{current_time}"
    final_output_directory = os.path.join(output_directory, time_subfolder)

    # Create the output directory if it doesn't exist
    os.makedirs(final_output_directory, exist_ok=True)

    print(f"[INFO] Output directory prepared: {final_output_directory}")

    # Return relevant paths
    return {
        "input_directory": input_directory,
        "input_name": input_name,
        "output_directory": final_output_directory,
        "output_name": output_name,
    }
