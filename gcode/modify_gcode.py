import re

from main import gcode_lines
from dictionary import dictionary


def modify_gcode_lines(gcode_lines: list, dictionary: str) -> list:
    """
    Modifies a list of G-code strings based on the specified replacement rules.

    Args:
        gcode_lines (list of str): List of G-code lines as strings.
        dictionary (dict): Dictionary where keys are the substrings to replace, and values are the replacement.

    Returns:
        list of str: Modified G-code lines.
    """
    modified_lines = []
    for line in gcode_lines:
        for old, new in dictionary.items():
            # Use word boundaries (\b) for  exact matches only
            line = re.sub(rf"\b{old}\b", new, line)

        # Add the modified line to the results list
        modified_lines.append(line)

    return modified_lines


# Apply the function
modified_gcode = modify_gcode_lines(gcode_lines, dictionary)

# Output the modified G-code lines
for line in modified_gcode:
    print(line)

# def get_z_height (modified_gcode: str) -> list:
#     for line in modified_gcode:
#         re.search()
