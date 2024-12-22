def export_to_src(
    krl_lines: list[str],
    start_code: list[str],
    end_code: list[str],
    output_path: str,
    file_name: str,
):
    """
    Combines the robot start code, KRL lines, and end code into a single .src file.

    :param krl_lines: List of KRL-formatted lines (main G-code converted to KRL).
    :param start_code: List of robot start code lines.
    :param end_code: List of robot end code lines.
    :param output_path: Path to the directory where the .src file will be saved.
    :param file_name: Name of the output .src file (without extension).
    """
    # Ensure the output path ends with a separator
    if not output_path.endswith(("\\", "/")):
        output_path += "/"

    # Combine all lines into a single list
    combined_lines = start_code + [""] + krl_lines + [""] + end_code

    # Construct the full file path
    full_file_path = f"{output_path}{file_name}.src"

    try:
        # Write the combined lines to the .src file
        with open(full_file_path, "w") as file:
            file.write("\n".join(combined_lines))
        print(f"Successfully exported to {full_file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to export .src file: {e}")
