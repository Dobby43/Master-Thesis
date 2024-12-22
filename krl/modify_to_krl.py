from typing import List, Dict, Union


def krl_format(
    gcode: list[dict[str, str | float | int | None]],
    *,
    a: float,
    b: float,
    c: float,
    end_pos: str,
    vel: float,
) -> list[str]:
    """
    Converts processed G-code to KRL format, including layer and type annotations.

    :param gcode: List of processed G-code entries.
    :type gcode: List[Dict[str, Union[str, float, int, None]]]
    :param a: Orientation of rotary axis A in degrees.
    :type a: float
    :param b: Orientation of rotary axis B in degrees.
    :type b: float
    :param c: Orientation of rotary axis C in degrees.
    :type c: float
    :param end_pos: End position of robot in KRL format.
    :type end_pos: str
    :param vel: Velocity of robot during printing.
    :type vel: float
    :returns: Updated list of KRL formatted lines.
    :rtype: List[str]
    """
    krl_lines = []
    current_layer = None
    current_type = None
    first_position = True  # To handle the first position separately

    # Define column widths for alignment
    field_width_x = 7
    field_width_y = 7
    field_width_z = 7
    coord_format_x = f"{{:>{field_width_x}.2f}}"
    coord_format_y = f"{{:>{field_width_y}.2f}}"
    coord_format_z = f"{{:>{field_width_z}.2f}}"

    for entry in gcode:
        # Extract relevant values from the entry
        x = coord_format_x.format(entry.get("X", 0))
        y = coord_format_y.format(entry.get("Y", 0))
        z = coord_format_z.format(entry.get("Z", 0))
        layer = entry.get("Layer")
        move_type = entry.get("Move")
        type_ = entry.get("Type", "UNKNOWN")

        # Insert a layer comment on layer change
        if layer != current_layer:
            krl_lines.append("\n" f";LAYER: {layer}")
            current_layer = layer

        # Insert a type comment on type change
        if type_ != current_type:
            krl_lines.append("\n" f";TYPE: {type_}")
            current_type = type_

        # Format the KRL command
        if move_type in ["G1", "G0"]:  # Only process G0 (Travel) or G1 (Print)
            if first_position:
                # First position is a PTP movement
                krl_lines.append(
                    f"PTP {{X {x}, Y {y}, Z {z}, A {a}, B {b}, C {c}, "
                    f"E1 0, E2 0, E3 0, E4 0}} C_PTP"
                )
                krl_lines.append("\n" f"$VEL.CP={vel:.2f}")  # Add velocity only once
                first_position = False
            else:
                # LIN movements for subsequent points
                krl_lines.append(
                    f"LIN {{X {x}, Y {y}, Z {z}, A {a}, B {b}, C {c}, "
                    f"E1 0, E2 0, E3 0, E4 0}} C_DIS"
                )

    # Append the final position
    krl_lines.append(
        f"\n "
        ";TYPE TRAVEL "
        "\n"
        f"PTP {{{end_pos[1:-1]}, E1 0, E2 0, E3 0, E4 0 }} C_PTP"
    )

    return krl_lines
