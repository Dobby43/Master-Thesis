import re
from main import gcode_lines


def append_z_height(gcode_lines):
    """
    Modifies a list of G-code lines by adding the last seen Z value to LIN commands
    if they don't already have one, and appending Z after the Y value.

    Args:
        gcode_lines (list of str): List of G-code lines as strings.

    Returns:
        list of str: Modified G-code lines with Z values added to LIN commands.
    """
    modified_lines = []
    last_z_value = None  # Stores the most recent Z value

    for line in gcode_lines:
        # Check if there is a Z value in the current line and update last_z_value
        z_match = re.search(r"\bZ\s*([\d\.-]+)", line)
        if z_match:
            last_z_value = z_match.group(0)  # Store the full Z part (e.g., "Z10.5")

        # If the line starts with LIN and does not have a Z value, add the last Z value
        if line.startswith("G1") and last_z_value and " Z" not in line:
            # Find the position to insert the Z value directly after the Y value
            y_match = re.search(r"Y\s*([\d\.-]+)", line)
            if y_match:
                # Insert Z value right after the Y value
                insert_pos = y_match.end()  # End position of the Y match
                line = line[:insert_pos] + " " + last_z_value + line[insert_pos:]

        # Add the modified or original line to the list
        modified_lines.append(line)

    return modified_lines


modified_gcode = add_z_to_lin_lines(gcode_lines)

# Output the modified G-code lines
for line in modified_gcode:
    print(line)
