def krl_format(
    gcode: list[dict[str, str | float | int | None]],
    type_mapping: dict[str, dict[str, int]],
    a: float,
    b: float,
    c: float,
    vel: float,
    x_max: float,
    y_max: float,
    z_max: float,
) -> list[str]:
    """
    DESCRIPTION:
    Converts processed G-code into a properly formatted KRL program.

    ARGUMENTS:
    gcode: A list of dictionaries containing processed G-code entries.
    type_mapping: A dictionary mapping types to their properties, including 'type_number'.
    a, b, c: Rotational axis angles (A, B, C) in degrees.
    vel: The velocity of the robot during printing.
    x_max, y_max, z_max: Maximum print bed dimensions used for field width calculation.

    RETURNS:
    A list of KRL-formatted lines with properly aligned decimal places and signs.
    """

    krl_lines = []
    previous_layer = None
    previous_type = None
    first_position = True  # First movement should be a PTP movement

    # Calculate the required field width for alignment based on max values
    def calc_field_width(max_value: float, decimal_places: int) -> int:
        return (
            len(str(int(max_value))) + decimal_places + 3
        )  # +3 for sign, space, and dot

    field_width_x = calc_field_width(x_max, 2)
    field_width_y = calc_field_width(y_max, 2)
    field_width_z = calc_field_width(z_max, 2)
    field_width_rot = 4  # Fixed width for A, B, C
    field_width_extra = 2  # Fixed width for E1 - E4

    # Formatting functions
    def format_float(value: float, width: int) -> str:
        """Formats float values with a fixed number of decimal places and sign."""
        return f"{'+' if value >= 0 else '-'} {abs(value):>{width - 2}.2f}"

    def format_int(value: int, width: int) -> str:
        """Formats integer values with a fixed width and sign."""
        return f"{'+' if value >= 0 else '-'} {abs(value):>{width - 2}}"

    for entry in gcode:
        # Extract values from G-code entry
        x = entry.get("X", 0)
        y = entry.get("Y", 0)
        z = entry.get("Z", 0)
        current_layer = entry.get("Layer")
        move_type = entry.get("Move")
        current_type = entry.get("Type", "unknown").lower()

        # Determine type number from mapping
        type_number = type_mapping.get(current_type, {}).get("type_number", 10)

        # Insert layer change if needed
        if current_layer != previous_layer:
            krl_lines.append(f"\nLAYER = {current_layer}")
            previous_layer = current_layer

        # Insert type change if needed
        if current_type != previous_type:
            krl_lines.append(f"\nPATH_TYPE = {type_number}")
            previous_type = current_type

        # Format the movement commands
        if move_type in ["G1", "G0"]:  # Only process G0 (Travel) or G1 (Print)
            formatted_x = format_float(x, field_width_x)
            formatted_y = format_float(y, field_width_y)
            formatted_z = format_float(z, field_width_z)
            formatted_a = format_int(a, field_width_rot)
            formatted_b = format_int(b, field_width_rot)
            formatted_c = format_int(c, field_width_rot)
            formatted_e1 = format_int(0, field_width_extra)
            formatted_e2 = format_int(0, field_width_extra)
            formatted_e3 = format_int(0, field_width_extra)
            formatted_e4 = format_int(0, field_width_extra)

            # First movement as PTP
            if first_position:
                krl_lines.append(
                    f"PTP {{X {formatted_x}, Y {formatted_y}, Z {formatted_z}, "
                    f"A {formatted_a}, B {formatted_b}, C {formatted_c}, "
                    f"E1 {formatted_e1}, E2 {formatted_e2}, E3 {formatted_e3}, E4 {formatted_e4}}} C_PTP"
                )
                krl_lines.append(f"$VEL.CP={vel:.2f}")
                first_position = False
            else:
                # Subsequent movements as LIN
                krl_lines.append(
                    f"LIN {{X {formatted_x}, Y {formatted_y}, Z {formatted_z}, "
                    f"A {formatted_a}, B {formatted_b}, C {formatted_c}, "
                    f"E1 {formatted_e1}, E2 {formatted_e2}, E3 {formatted_e3}, E4 {formatted_e4}}} C_DIS"
                )

    return krl_lines
