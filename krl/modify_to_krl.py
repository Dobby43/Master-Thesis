def format_value(value: float, width: int, precision: int = 2) -> str:
    """
    DESCRIPTION:
    Formats a float with a sign, a space, and right-aligned number.
    Ensures decimal points align across all formatted numbers.
    Example: '+   90.00', '-  900.00'

    :param value: The value to format
    :param width: The width of the formatted number
    :param precision: The number of significant digits after the decimal point.

    :return: The formatted value as a sting
    """
    sign = "+" if value >= 0 else "-"
    abs_number = f"{abs(value):.{precision}f}"
    return f"{sign} {abs_number.rjust(width - 2)}"  # 2 Zeichen für sign + space


def calc_field_width(min_val: float, max_val: float, precision: int) -> int:
    """
    DESCRIPTION:
    Calculates the total width required for the numeric part,
    including sign and space, to ensure aligned formatting.

    :param min_val: minimum value in a given direction (x,y,z) from G-Code
    :param max_val: maximum value in a given direction (x,y,z) from G-Code
    :param precision: number of decimal places to round up

    :return: space needed to fit the maximum length of characters including sign and space
    """
    abs_vals = [abs(min_val), abs(max_val)]
    number_width = max(len(f"{v:.{precision}f}") for v in abs_vals)
    return number_width + 2  # 1 for sign, 1 for space


def krl_format(
    gcode: list[dict[str, str | float | int | None]],
    type_mapping: dict[str, int],
    a: int,
    b: int,
    c: int,
    vel_cp: float,
    vel_tvl: float,
    pump_control: bool,
    precision: int,
    axis_min: dict[str, float],
    axis_max: dict[str, float],
    timer: int,
    mlt: int,
    split_layers: bool,
    project_name: str,
) -> list[list[str]] | list[str]:
    """
    DESCRIPTION
    Formatting given values from a list of dictionaries into strings matching krl format

    :param gcode: list of necessary information on coordinates Nullframe orientation and flow (for external axis E1)
    :param type_mapping: dictionary mapping written types to integers specified in setup.Robot.type_number.json
    :param a: orientation of Nullframe around z-axis in robot convention
    :param b: orientation of Nullframe around y-axis in robot convention
    :param c: orientation of Nullframe around x-axis in robot convention
    :param vel_cp: printing velocity annotated in krl before each extrusion move (ready to be updated to linetype specific velocity in the future)
    :param vel_tvl: travel velocity annotated in krl before each non-extrusion move
    :param pump_control: specifies if the pump is controlled on the external axis via rpm or voltage
    :param precision: specifies the amount of digits exported
    :param axis_min: to determine the amount of space needed for each coordinate X,Y,Z such that the decimal placed match in columns
    :param axis_max: to determine the amount of space needed for each coordinate X,Y,Z such that the decimal placed match in columns
    :param timer: specifies which timer is used to track minimum layer time
    :param mlt: minimum layer time in ms (robot waits till timer > mlt before starting new layer)
    :param split_layers: specifies if .src file is split into multiple layers
    :param project_name: project name with a maximum length of 25 characters in total

    :return: list or nested list of .src lines depending on if file is split or not
    """

    # Setup of initial values
    previous_layer = None
    previous_type = None
    position = -1

    krl_lines = []
    layer_blocks = []
    current_block = []

    max_lengths = {
        "X": calc_field_width(axis_min["x"], axis_max["x"], precision),
        "Y": calc_field_width(axis_min["y"], axis_max["y"], precision),
        "Z": calc_field_width(axis_min["z"], axis_max["z"], precision),
        "Flow": calc_field_width(
            min(entry["Flow"] for entry in gcode),
            max(entry["Flow"] for entry in gcode),
            precision,
        ),
        "Voltage": calc_field_width(
            min(entry["Voltage"] for entry in gcode),
            max(entry["Voltage"] for entry in gcode),
            precision,
        ),
        "A": calc_field_width(a, a, precision),
        "B": calc_field_width(b, b, precision),
        "C": calc_field_width(c, c, precision),
    }

    for entry in gcode:
        current_layer = entry["Layer"]
        current_type = entry["Type"]
        type_number = type_mapping.get(current_type, 0)

        # Saves all code lines of a layer into a temporary list to prepare for splitting of .src file
        line_buffer = []

        # Layer und Timer Handling
        if current_layer == 0 and previous_layer is None:
            line_buffer.append(f"\nLAYER = {current_layer}")
            previous_layer = current_layer
        # Insert wait for mlt and stop as well as reset timer
        elif current_layer != previous_layer:
            line_buffer.append(f"\nWAIT FOR $TIMER[{timer}] > {mlt}")
            line_buffer.append(f"\nLAYER = {current_layer}")
            line_buffer.append(f"\n$TIMER_STOP[{timer}] = TRUE")
            line_buffer.append(f"$TIMER[{timer}] = 0")
            line_buffer.append(f"$TIMER_STOP[{timer}] = FALSE\n")
            previous_layer = current_layer

            # append "END" to current block for a layer change if split layers is active and current block has values
            if split_layers and current_block:
                current_block.append("END")
                layer_blocks.append(current_block)
                current_block = []

        # Path Type & Velocity Handling
        # translate current type to type_numer from setup.json and append velocity (vel_cp for print moves; vel_tvl for travel moves)
        if current_type != previous_type:
            line_buffer.append(f"\nPATH_TYPE = {type_number}")
            velocity = vel_tvl if current_type == "travel" else vel_cp
            line_buffer.append(f"$VEL.CP={velocity:.{precision}f}")
            previous_type = current_type

        x = format_value(entry["X"], max_lengths["X"])
        y = format_value(entry["Y"], max_lengths["Y"])
        z = format_value(entry["Z"], max_lengths["Z"])

        # Set flow values depending on given Type
        if current_type == "retract":  # Set E1 to -1
            e1 = format_value(
                -1, max_lengths["Flow"] if pump_control else max_lengths["Voltage"]
            )
        elif current_type == "protract":  # Set E1 to 0
            e1 = format_value(
                0, max_lengths["Flow"] if pump_control else max_lengths["Voltage"]
            )
        elif (
            entry["Move"] == "G1"
        ):  # Set E1 to "Flow" or "RPM" depending on pump control
            e1 = format_value(
                entry["Flow"] if pump_control else entry["Voltage"],
                max_lengths["Flow"] if pump_control else max_lengths["Voltage"],
            )
        else:  # Set anything else to 0
            e1 = format_value(
                0, max_lengths["Flow"] if pump_control else max_lengths["Voltage"]
            )

        a_str = format_value(a, max_lengths["A"])
        b_str = format_value(b, max_lengths["B"])
        c_str = format_value(c, max_lengths["C"])

        # Compose position string
        position_string = (
            f"X {x}, Y {y}, Z {z}, "
            f"A {a_str}, B {b_str}, C {c_str}, "
            f"E1 {e1}, E2 + 0, E3 + 0, E4 + 0"
        )

        # keep track of position (lines)
        position += 1

        # First move as PTP
        if position == 0:
            line_buffer.append(f"PTP {{{position_string}}} C_PTP")
        # Last move as C_DIS with mlt timer
        elif position == len(gcode) - 1:
            line_buffer.append(f"PTP {{{position_string}}} C_DIS")
            line_buffer.append(f"\nWAIT FOR $TIMER[{timer}] > {mlt}")
        # Everything else as C_DIS
        else:
            line_buffer.append(f"LIN {{{position_string}}} C_DIS")

        # Append only line_buffer to block if split layers
        if split_layers:
            current_block.extend(line_buffer)
        # Append everything to krl_lines if not split_layers
        else:
            krl_lines.extend(line_buffer)

    if split_layers:
        # Append END to block if last block
        if current_block:
            current_block.append("END")
            layer_blocks.append(current_block)
        # Set filename in the first line of the block
        return [
            [f"DEF {project_name}_{i+1:03d} ()"] + block
            for i, block in enumerate(layer_blocks)
        ]
    else:
        return krl_lines


if __name__ == "__main__":
    sample_gcode = [
        {
            "Move": "G1",
            "X": 1150.0,
            "Y": 2250.0,
            "Z": 105.0,
            "E_Rel": 57.29578,
            "Layer": 0,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 25.0,
            "Flow": 131250.0,
            "RPM": 78.75,
            "Voltage": 0.7875,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": -934.78,
            "Y": 270.82,
            "Z": 813.89,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
    ]
    type_map = {"wall_outer": 1, "travel": 0}
    a_min = {"x": -1000, "y": -500, "z": 0}
    a_max = {"x": 1200, "y": 2500, "z": 1000}

    split = True
    result = krl_format(
        sample_gcode,
        type_map,
        0,
        0,
        180,
        0.35,
        1.0,
        True,
        2,
        a_min,
        a_max,
        timer=4,
        mlt=10000,
        split_layers=split,
        project_name="DEMO",
    )

    if split:
        for p, blocks in enumerate(result):
            print(f"\n--- File {p:03d} ---")
            print("\n".join(blocks))

    else:
        print(result)
