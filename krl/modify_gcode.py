import re


def toolhead_orientation(gcode: list, *, a: float, b: float, c: float) -> list:
    """
    Updates the G-code with specified orientations for the rotary axes A, B, and C.

    :param gcode: Original list of G-code lines.
    :type gcode: List[str]
    :param a: Orientation of rotary axis A in degrees.
    :type a: float
    :param b: Orientation of rotary axis B in degrees.
    :type b: float
    :param c: Orientation of rotary axis C in degrees.
    :type c: float
    :returns: Updated list of G-code lines with orientations for axes A, B, and C.
    :rtype: List[str]
    """

    krl_axis = []
    for line in gcode:
        if line.startswith("G"):
            line = f"{line} A {a}, B {b}, C {c}"
        krl_axis.append(line)
    else:
        krl_axis.append(line)

    return krl_axis


# def format_gcode(gcode: List[str], decimals: int) -> List[str]:
#     """
#     Takes simplified G-Code and rounds it to specified decimal places.
#     Formats rounded G-code lines so that after every defined space for the X, Y, and Z value a comma is placed.
#
#     :param gcode: Original list of G-code lines.
#     :type gcode: List[str]
#     :param decimals: Defines decimal places.
#     :type decimals: int
#     :returns: Rounded G-code lines.
#     :rtype: List[str]
#     """
#
#     formatted_lines = []
#     max_lengths = {"X": 4, "Y": 4, "Z": 4}
#
#     for line in gcode:
#         # Extracts all x,y and z information in Lines starting with "G"
#         match = re.search(
#             r"(G[01])(?.*)", line)
#         coordinates = match.group(2)
#         if match:
#             formatted_line = (
#                 f"{g_command_new:<3} + {coordinates} "
#             formatted_lines.append(formatted_line)
#         else:
#             # appends non-matching lines without change
#             formatted_lines.append(line)
#
#     return formatted_lines
