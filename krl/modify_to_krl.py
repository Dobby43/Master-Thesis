def krl_format(
    gcode: list[dict[str, str | float | int | None]],
    a: float,
    b: float,
    c: float,
    vel: float,
) -> list[str]:
    """
    DESCRIPTION:
    Converts processed G-code into KRL format, including layer and type annotations.

    ARGUMENTS:
    gcode: A list of dictionaries containing processed G-code entries.
    a: Orientation of rotary axis A in degrees.
    b: Orientation of rotary axis B in degrees.
    c: Orientation of rotary axis C in degrees.
    end_pos: The robot's end position in KRL format.
    vel: The velocity of the robot during printing.

    RETURNS:
    A list of KRL-formatted lines, including layer and type annotations.
    """
    krl_lines = []
    previous_layer = None
    previous_type = None
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
        current_layer = entry.get("Layer")
        move_type = entry.get("Move")
        current_type = entry.get("Type", "UNKNOWN")

        # Insert a layer comment on layer change
        if current_layer != previous_layer:
            krl_lines.append("\n" f"LAYER = {current_layer}")
            current_layer = previous_layer

        # Insert a type comment on type change
        if current_type != previous_type:
            krl_lines.append("\n" f"PATH_TYPE = {current_type}")
            previous_type = current_type

        # Format the KRL command
        if move_type in ["G1", "G0"]:  # Only process G0 (Travel) or G1 (Print)
            if first_position:
                # First position is a PTP movement
                krl_lines.append(
                    ""
                    f"PTP {{X {x}, Y {y}, Z {z}, A {a}, B {b}, C {c}, "
                    f"E1 0, E2 0, E3 0, E4 0}} C_PTP"
                    ""
                    f"$VEL.CP={vel:.2f}"
                )
                first_position = False
            else:
                # LIN movements for subsequent points
                krl_lines.append(
                    f"LIN {{X {x}, Y {y}, Z {z}, A {a}, B {b}, C {c}, "
                    f"E1 0, E2 0, E3 0, E4 0}} C_DIS"
                )

    return krl_lines
