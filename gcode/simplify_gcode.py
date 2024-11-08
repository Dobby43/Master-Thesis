import re
from typing import List, Dict, Any

# Define necessary G-code commands to keep
DICTIONARY = [
    "G0",
    "G1",
    ";LAYER",
    ";TYPE",
]


def necessary_gcode(gcode: List[str]) -> List[str]:
    """
    Filters the G-code lines to keep only necessary commands.

    :param gcode: Original list of G-code lines.
    :type gcode: List[str]
    :returns: Filtered G-code lines with necessary commands only.
    :rtype: List[str]
    """

    gcode_necessary = []
    for line in gcode:
        # deletes whitespaces and converts line to lower case
        line_lower = line.strip().lower()

        # Checks for matching entries in DICTIONARY (also converted to lower case)
        if any(line_lower.startswith(item.lower()) for item in DICTIONARY):
            gcode_necessary.append(line)  # Adds original line for matching lines

    return gcode_necessary


def delete_feed(gcode: List[str]) -> List[str]:
    """
    Removes feed rate (F) values from each G-code line.

    :param gcode: List of G-code lines.
    :type gcode: List[str]
    :returns: G-code lines without feed rate values.
    :rtype: List[str]
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

    :param gcode: List of G-code lines.
    :type gcode: List[str]
    :returns: G-code lines without extrusion values.
    :rtype: List[str]
    """

    extrusion_deleted = []
    for line in gcode:
        # Remove E values (e.g., E1234.56) without extra spaces
        line = re.sub(r" ?E-?[\d\.]+\b", "", line).strip()
        extrusion_deleted.append(line)

    return extrusion_deleted


def clean_gcode(gcode: List[str]) -> List[str]:
    """
    Cleans G-code from unnecessary (empty lines) after modification.

    :param gcode: List of G-code lines.
    :type gcode: List[str]
    :returns: G-code lines without extrusion values.
    :rtype: List[str]
    """

    gcode_cleaned = []
    for line in gcode:
        # Strip whitespace for an exact match with DICTIONARY entries
        striped_lines = line.strip()

        # Only add the line if it's not solely one of the necessary DICTIONARY entries
        if striped_lines not in DICTIONARY:
            gcode_cleaned.append(line)

    return gcode_cleaned


def append_z_height(gcode: List[str]) -> List[str]:
    """
    Updates and appends the current Z Value for every line in the G-Code.

    :param gcode: List of G-code lines.
    :type gcode: List[str]
    :returns: G-code lines with current Z height in every line
    :rtype: List[str]
    """
    current_z_height = None
    z_height_appended = []
    for line in gcode:
        z_match = re.search(r"Z\s*[\d\.]+", line)
        if z_match:
            current_z_height = str(z_match.group(0))

        if current_z_height and " Z" not in line:
            y_match = re.search(r"Y\s*[-?\d\.]+", line)
            if y_match:
                insert_pos = y_match.end()
                line = (
                    line[:insert_pos] + " " + current_z_height + "" + line[insert_pos:]
                )
        z_height_appended.append(line)
    return z_height_appended


def format_gcode(gcode: List[str], decimals: int) -> List[str]:
    """
    Takes simplified G-Code and rounds it to specified decimal places.
    Formats rounded G-code lines so that after every defined space for the X, Y, and Z value a comma is placed.

    :param gcode: Original list of G-code lines.
    :type gcode: List[str]
    :param decimals: Defines decimal places.
    :type decimals: int
    :returns: Rounded G-code lines.
    :rtype: List[str]
    """

    formatted_lines = []
    max_lengths = {"X": 4, "Y": 4, "Z": 4}

    for line in gcode:
        # Extracts all x,y and z information in Lines starting with "G"
        match = re.search(
            r"(G\d)\s*X(-?\d+\.?\d+?)\s*Y(-?\d+\.?\d+?)\s*Z(-?\d+\.?\d+?)?.*",
            line,
        )

        if match:
            g_command = match.group(1)  # G0 or G1
            x_val = float(match.group(2))  # value of X
            y_val = float(match.group(3))  # value of Y
            z_val = float(match.group(4))  # value of Z

            # Round values of x,y and z according to decimals input
            x_val = round(x_val, decimals)
            y_val = round(y_val, decimals)
            z_val = round(z_val, decimals)

            # Formats lines to maximum length of value for x, y and z
            formatted_line = (
                f"\n{g_command:<3} "  # G-command (G0 or G1)
                f"X {x_val:<{max_lengths['X'] + decimals + 1}.{decimals}f}, "  # X-Wert mit fester Breite und Dezimalstellen
                f"Y {y_val:<{max_lengths['Y'] + decimals + 1}.{decimals}f}, "  # Y-Wert mit fester Breite und Dezimalstellen
                f"Z {z_val:<{max_lengths['Z'] + decimals + 1}.{decimals}f},"  # Z-Wert mit fester Breite und Dezimalstellen
            )
            formatted_lines.append(formatted_line)
        else:
            # appends non-matching lines without change
            formatted_lines.append("\n" + line)

    return formatted_lines
