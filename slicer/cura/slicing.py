import subprocess
from pathlib import Path
from typing import Tuple, List


def slicer(
    file_name_stl: str,
    directory_stl: str,
    export_directory_gcode: str,
    export_file_gcode: str,
    cura_engine_path: str,
    cura_def_file: str,
    additional_args: dict[str, str],
) -> Tuple[bool, str]:
    """
    DESCRIPTION:
    Slices an STL file using CuraEngine and generates G-code.

    :param file_name_stl: Name of the STL file to be sliced.
    :param directory_stl: Directory containing the STL file.
    :param export_directory_gcode: Directory to save the generated G-code to.
    :param export_file_gcode: Name of the output G-code file [without extension (.gcode)]
    :param cura_engine_path: Path to the Cura Engine executable.
    :param cura_def_file: Path to the Cura printer definition file.
    :param additional_args: Additional slicing arguments in the format ["key=value"].

    RETURNS:
    tuple[bool, str]: A tuple containing:
        - bool: Success status (True if slicing succeeded, False otherwise).
        - str: Message with details of success or error.
    """
    # Validate STL input file
    stl_path = Path(directory_stl) / file_name_stl
    if not stl_path.exists():
        return False, f"[ERROR] STL file not found at {stl_path}."
    if stl_path.suffix.lower() != ".stl":
        return False, f"[ERROR] {stl_path} is not a valid STL file."

    # Validate CuraEngine path
    cura_engine = Path(cura_engine_path)
    if not cura_engine.exists() or not cura_engine.is_file():
        return False, f"[ERROR] CuraEngine not found at {cura_engine_path}."

    # Validate Cura definition file
    cura_def = Path(cura_def_file)
    if not cura_def.exists() or not cura_def.is_file():
        return False, f"[ERROR] Cura definition file not found at {cura_def_file}."

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
    ]

    # Add additional arguments immediately after the definition file
    for key, value in additional_args.items():
        command.extend(["-s", f"{key}={value}"])

    # Append STL and output G-code file paths
    command.extend(
        [
            "-l",
            str(stl_path),
            "-o",
            str(gcode_file),
        ]
    )

    print(command)

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return (
            True,
            f"[INFO] G-Code generated at {gcode_file}\n{result.stdout}",
        )

    except subprocess.CalledProcessError as error:
        # Handle Cura slicing errors
        error_message = error.stderr if error.stderr else error.stdout
        return False, f"[ERROR] Error during slicing:\n{error_message}"

    except Exception as e:
        # Catch unexpected errors
        return False, f"[ERROR] Unexpected error: {str(e)}"
