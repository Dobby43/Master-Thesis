import re
from typing import List, Set

import gcode

# Define necessary G-code commands to keep
dictionary: Set[str] = {"G0", "G1", ";Layer", ";Type"}


def necessary_gcode(gcode: List[str]) -> List[str]:
    """
    Filters the G-code lines to keep only necessary commands.

    Args:
        gcode (List[str]): Original list of G-code lines.

    Returns:
        List[str]: Filtered G-code lines with necessary commands only.
    """
    gcode_necessary = []
    for line in gcode:
        # Check if line starts with any necessary command
        if any(line.startswith(item) for item in dictionary):
            gcode_necessary.append(line)  # Append line if it matches

    return gcode_necessary


def delete_feed(gcode: List[str]) -> List[str]:
    """
    Removes feed rate (F) values from each G-code line.

    Args:
        gcode (List[str]): List of G-code lines.

    Returns:
        List[str]: G-code lines without feed rate values.
    """
    feed_deleted = []
    for line in gcode:
        # Remove F values (e.g., F1234.56) without extra spaces
        line = re.sub(r" ?F[\d\.]+\b", "", line).strip()
        feed_deleted.append(line)

    return feed_deleted


def delete_extrusion(gcode: List[str]) -> List[str]:
    """
    Removes extrusion (E) values from each G-code line.

    Args:
        gcode (List[str]): List of G-code lines.

    Returns:
        List[str]: G-code lines without extrusion values.
    """
    extrusion_deleted = []
    for line in gcode:
        # Remove E values (e.g., E1234.56) without extra spaces
        line = re.sub(r" ?E-?[\d\.]+\b", "", line).strip()
        extrusion_deleted.append(line)

    return extrusion_deleted


def clean_gcode(gcode: List[str]) -> List[str]:
    """
    Cleans G-Code from unnecessary (empty lines) after modification

    Args:
        gcode (List[str]): List of G-code lines.

    Returns:
        List[str]: G-code lines without extrusion values.
    """

    gcode_cleaned = []
    for line in gcode:
        # Strip whitespace for an exact match with dictionary entries
        striped_lines = line.strip()

        # Only add the line if it's not solely one of the necessary dictionary entries
        if striped_lines not in dictionary:
            gcode_cleaned.append(line)

    return gcode_cleaned


def format_gcode_lines(gcode_lines: List[str], decimals: int) -> List[str]:
    """
    Formats G-code lines by rounding coordinates to a specific number of decimals,
    adding a space between the axis (X, Y) and the value, and appending a comma after each value.

    Args:
        gcode_lines (List[str]): List of G-code lines.
        decimals (int): Number of decimal places to round to.

    Returns:
        List[str]: Formatted G-code lines.
    """
    formatted_lines = []

    for line in gcode_lines:
        # uses regular expression to search for String X or Y followed by a number seperated by a "."
        line = re.sub(
            r"([XYZ])(\d+(\.\d+)?)",
            lambda match: f"{match.group(1)} {round(float(match.group(2)), decimals):.{decimals}f},",
            line,
        )

        # Append formatted line to the result list
        formatted_lines.append(line)

    return formatted_lines


def append_z_height (gcode: List[str]) -> List[str]:
    z_height_appended = []
    for line in gcode
        z_match = re.search(r"(\d+)Z\s\d+", line)
        if z_match:
            current_z_height = float(z_match.group(0))

        if current_z_height and " Z" not in line:
            y_match = re.search(r"Y\s\d+", line)
            if y_match:
                insert_pos = y_match.end()
                line = line[:insert_pos] + " " + current_z_height + "," + line[insert_pos:]
        z_height_appended.append(line)
    return z_height_appended