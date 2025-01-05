import subprocess
import os
from pathlib import Path


def slice(
    stl_file: str,
    import_directory_stl: str,
    export_directory_gcode: str,
    export_file_gcode: str,
    cura_engine_path: str,
    cura_def_file: str,
    **kwargs,
) -> tuple[bool, str]:
    """
    Slices an STL file using CuraEngine.
    """
    # Ensure the input directory and STL file are valid
    stl_path = Path(import_directory_stl) / stl_file
    if not stl_path.exists() or stl_path.suffix.lower() != ".stl":
        return False, f"Error: {stl_path} is not a valid .stl file or does not exist."

    # Set the output directory and file
    gcode_path = Path(export_directory_gcode)
    gcode_path.mkdir(parents=True, exist_ok=True)  # Ensure the export directory exists
    gcode_file = gcode_path / (export_file_gcode + ".gcode")

    # Construct the slicing command
    command = [
        cura_engine_path,
        "slice",
        "-j",
        cura_def_file,
        "-s",
        "roofing_layer_count=1",
        "-l",
        str(stl_path),
        "-o",
        str(gcode_file),
    ]

    # Add additional settings from kwargs
    for key, value in kwargs.items():
        command.extend(["-s", f"{key}={value}"])

    # Debugging: Print the command
    print("Generated Command:", " ".join(command))

    try:
        # Execute the slicing command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return (
            True,
            f"G-code successfully generated at {gcode_file}\nOutput:\n{result.stdout}",
        )

    except subprocess.CalledProcessError as error:
        # Capture stderr or stdout for debugging
        return False, f"Error during slicing:\n{error.stderr or error.stdout}"


if __name__ == "__main__":
    # Define input parameters
    IMPORT_DIRECTORY_STL = (
        r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\Slicing_Data\Input\STL"
    )
    IMPORT_FILE_STL = r"Quader 200x200x60.stl"

    # Define output parameters
    EXPORT_DIRECTORY_GCODE = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\Slicing_Data\Output\GCODE_Files\automated"
    EXPORT_FILE_GCODE = r"Quader_200x200x60.gcode"

    # Call the slicing function
    success, message = slice(
        stl_file=IMPORT_FILE_STL,
        import_directory_stl=IMPORT_DIRECTORY_STL,
        export_directory_gcode=EXPORT_DIRECTORY_GCODE,
        export_file_gcode=EXPORT_FILE_GCODE,
    )

    # Print the result
    print(message)
