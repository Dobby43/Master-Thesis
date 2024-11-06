import re


def krl_format(
    gcode: list, *, a: float, b: float, c: float, end_pos: str, vel: float
) -> list:
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
    :param end_pos: End position of robot.
    :type end_pos: str
    :param vel: Velocity of robot during printing.
    :type vel: float
    :returns: Updated list of G-code lines with orientations for axes A, B, and C.
    :rtype: List[str]
    """

    krl_axis = []
    found_first_coord = False  # switch to check if first coordinate is found

    for line in gcode:
        match = re.search(r"(G[01]\s*)(.*)", line)
        if match and not found_first_coord:
            coordinates = match.group(2)
            krl_axis.append(
                f"\nPTP {{{coordinates} A {a}, B {b}, C {c}, E1 0, E2 0, E3 0, E4 0}} C_PTP"
            )
            krl_axis.append(f"\n$VEL.CP={vel:.2f}")
            found_first_coord = True
        elif match:
            coordinates = match.group(2)
            krl_line = f"\nLIN {{{coordinates} A {a}, B {b}, C {c}, E1 0, E2 0, E3 0, E4 0}} C_DIS"
            krl_axis.append(krl_line)
        else:
            krl_axis.append(line)

    krl_axis.append("\nPTP {" + end_pos[1:-1] + " E1 0, E2 0, E3 0, E4 0} C_PTP")

    return krl_axis
