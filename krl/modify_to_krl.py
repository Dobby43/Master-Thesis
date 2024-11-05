import re


def krl_format(gcode: list, *, a: float, b: float, c: float) -> list:
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
        match = re.search(r"(G[01]\s*)(.*)", line)
        if match:
            coordinates = match.group(2)
            krl_line = f"\nLIN {{{coordinates} A {a}, B {b}, C {c}}} C_DIS"
            krl_axis.append(krl_line)
            # alternative
            # if match:
            #     coordinates = match.group(2)
            #     krl_line = line.replace(match.group(1), "LIN ")
            #     krl_line_extended = f"{krl_line}{{A {a}, B {b}, C {c}}} C_DIS"
            #     krl_axis.append(krl_line_extended)
        else:
            krl_axis.append("\n" + line)

    return krl_axis
