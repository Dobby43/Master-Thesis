import subprocess
from pathlib import Path
from typing import Tuple, List


def slice(
    stl_file: str,
    import_directory_stl: str,
    export_directory_gcode: str,
    export_file_gcode: str,
    cura_engine_path: str,
    cura_def_file: str,
    additional_args: List[str],
) -> Tuple[bool, str]:
    """
    DESCRIPTION:
    Slices an STL file using CuraEngine and generates G-code.

    ARGUMENTS:
    stl_file (str): Name of the STL file to be sliced.
    import_directory_stl (str): Directory containing the STL file.
    export_directory_gcode (str): Directory to save the generated G-code.
    export_file_gcode (str): Name of the output G-code file (without extension).
    cura_engine_path (str): Path to the CuraEngine executable.
    cura_def_file (str): Path to the Cura printer definition file.
    additional_args (List[str]): Additional slicing arguments in the format ["key=value"].

    RETURNS:
    tuple[bool, str]: A tuple containing:
        - bool: Success status (True if slicing succeeded, False otherwise).
        - str: Message with details of success or error.
    """
    # Validate STL input file
    stl_path = Path(import_directory_stl) / stl_file
    if not stl_path.exists():
        return False, f"Error: STL file not found at {stl_path}."
    if stl_path.suffix.lower() != ".stl":
        return False, f"Error: {stl_path} is not a valid STL file."

    # Validate CuraEngine path
    cura_engine = Path(cura_engine_path)
    if not cura_engine.exists() or not cura_engine.is_file():
        return False, f"Error: CuraEngine not found at {cura_engine_path}."

    # Validate Cura definition file
    cura_def = Path(cura_def_file)
    if not cura_def.exists() or not cura_def.is_file():
        return False, f"Error: Cura definition file not found at {cura_def_file}."

    # Prepare G-code output directory and file
    gcode_path = Path(export_directory_gcode)
    gcode_path.mkdir(parents=True, exist_ok=True)
    gcode_file = gcode_path / f"{export_file_gcode}.gcode"

    # Construct the slicing command
    command = [
        str(cura_engine),
        "slice",
        "-j",
        str(cura_def),
        "-s",
        "roofing_layer_count=1",  # TODO: roofing_layer_count lösen
    ]

    # Add additional arguments immediately after the definition file
    if additional_args:
        for arg in additional_args:
            command.extend(["-s", arg])

    # Append STL and output G-code file paths
    command.extend(
        [
            "-l",
            str(stl_path),
            "-o",
            str(gcode_file),
        ]
    )

    # Debugging: Print the constructed command
    print("Generated Command:", " ".join(command))

    try:
        # Execute the slicing command
        result = subprocess.run(
            command, check=True, capture_output=True, text=True
        )  # TODO: Error message überprüfen
        return (
            True,
            f"G-code successfully generated at {gcode_file}\nOutput:\n{result.stdout}",
        )

    except subprocess.CalledProcessError as error:
        # Handle Cura slicing errors
        error_message = error.stderr if error.stderr else error.stdout
        return False, f"Error during slicing:\n{error_message}"

    except Exception as e:
        # Catch unexpected errors
        return False, f"Unexpected error: {str(e)}"
