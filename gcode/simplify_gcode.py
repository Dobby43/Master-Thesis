import re
from typing import List, Set

from unicodedata import decimal

import gcode

# Define necessary G-code commands to keep
DICTIONARY = [
    "G0",
    "G1",
    ";LAYER",
    ";TYPE",
    ";MINX",
    ";MINY",
    ";MINZ",
    ";MAXX",
    ";MAXY",
    ";MAXZ",
]


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
        # Entferne führende und nachfolgende Leerzeichen und wandle in Kleinbuchstaben um
        line_lower = line.strip().lower()

        # Prüfe auf Übereinstimmungen mit den Einträgen in DICTIONARY in Kleinbuchstaben
        if any(line_lower.startswith(item.lower()) for item in DICTIONARY):
            gcode_necessary.append(line)  # Originalzeile hinzufügen, wenn sie passt

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
        # Strip whitespace for an exact match with DICTIONARY entries
        striped_lines = line.strip()

        # Only add the line if it's not solely one of the necessary DICTIONARY entries
        if striped_lines not in DICTIONARY:
            gcode_cleaned.append(line)

    return gcode_cleaned


def append_z_height(gcode: List[str]) -> List[str]:
    """
    Updates and appends the current Z Value for every line in the G-Code.

    Args:
        gcode (List[str]): Original list of G-code lines.

    Returns:
        List[str]: Updated and appended G-code lines.
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

    formatted_lines = []
    max_lengths = {"X": 4, "Y": 4, "Z": 4}
    # x_max, y_max, z_max = None, None, None
    # # Searches first few lines of code for maximum values of x,y and z
    # # TODO: account for negative values as well!
    # for line in gcode:
    #     if not x_max:
    #         x_max = re.search(r";MAXX:\s*([-?\d\.]+)", line)
    #     if not y_max:
    #         y_max = re.search(r";MAXY:\s*([-?\d\.]+)", line)
    #     if not z_max:
    #         z_max = re.search(r";MAXZ:\s*([-?\d\.]+)", line)
    #     if x_max and y_max and z_max:
    #         break  # Ends search if all values are located
    #
    # # Determines length of string for maximum x,y and z
    # max_lengths = {
    #     "X": len(x_max.group(1).split(".")[0]) if x_max else 0,
    #     "Y": len(y_max.group(1).split(".")[0]) if y_max else 0,
    #     "Z": len(z_max.group(1).split(".")[0]) if z_max else 0,
    # }

    for line in gcode:
        # Extracts all x,y and z information in Lines starting with "G"
        match = re.search(
            r"(G\d)\s*X(-?\d+\.?\d+?)\s*Y(-?\d+\.?\d+?)\s*Z(-?\d+\.?\d+?)",
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
                f"{g_command:<3} "  # G-Befehl (G0 oder G1), linksbündig
                f"X {x_val:<{max_lengths['X'] + decimals + 1}.{decimals}f}, "  # X-Wert mit fester Breite und Dezimalstellen
                f"Y {y_val:<{max_lengths['Y'] + decimals + 1}.{decimals}f}, "  # Y-Wert mit fester Breite und Dezimalstellen
                f"Z {z_val:<{max_lengths['Z'] + decimals + 1}.{decimals}f},"  # Z-Wert mit fester Breite und Dezimalstellen
            )
            formatted_lines.append(formatted_line)
        else:
            # appends non-matching lines without change
            formatted_lines.append(line)

    return formatted_lines
