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
    return f"{sign} {abs_number.rjust(width - 2)}"  # 2 spaces for sign + space


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
    Formatting given values from a list of dictionaries into strings matching KRL (.src) format.

    :param gcode: list of dictionaries containing G-code information (coordinates, nullframe orientation, flow rates for external axis E1).
    :param type_mapping: dictionary mapping written movement types to integers as defined in setup.Robot.type_number.json.
    :param a: orientation of the nullframe around the Z-axis in robot convention.
    :param b: orientation of the nullframe around the Y-axis in robot convention.
    :param c: orientation of the nullframe around the X-axis in robot convention.
    :param vel_tvl: travel velocity (non-extrusion moves) annotated before travel commands.
    :param pump_control: specifies if the pump is controlled via RPM (True) or Voltage (False) on the external axis E1.
    :param precision: number of decimal places for all numerical values (coordinates, speeds, flow rates).
    :param axis_min: minimum values for X, Y, Z axes to calculate field width for formatting.
    :param axis_max: maximum values for X, Y, Z axes to calculate field width for formatting.
    :param timer: index of the timer used to track the minimum layer time.
    :param mlt: minimum layer time in milliseconds (robot waits until timer exceeds this value before starting next layer).
    :param split_layers: specifies if the output should be split into separate .src files per layer (True) or kept as a single file (False).
    :param project_name: project name used for output files (maximum 25 characters).

    :return: list of formatted .src lines or list of nested .src line blocks (one block per layer if split_layers is True).
    """

    # --- Initialization ---
    previous_layer = None
    previous_type = None
    position = -1
    krl_lines = []
    layer_blocks = []
    current_block = []

    # Calculate maximum field widths for formatting
    max_lengths = {
        "X": calc_field_width(axis_min["x"], axis_max["x"], precision),
        "Y": calc_field_width(axis_min["y"], axis_max["y"], precision),
        "Z": calc_field_width(axis_min["z"], axis_max["z"], precision),
        "RPM": calc_field_width(
            min(entry["RPM"] for entry in gcode),
            max(entry["RPM"] for entry in gcode),
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

    # --- Helper blocks ---

    def start_layer(layer_idx):
        return [
            f"\nLAYER = {layer_idx}",
            f"$TIMER[{timer}] = 0",
            f"$TIMER_STOP[{timer}] = FALSE\n",
        ]

    def end_layer():
        return [
            f"\nWAIT FOR $TIMER[{timer}] > {mlt}",
            f"$TIMER_STOP[{timer}] = TRUE\n",
        ]

    def set_path_type_and_velocity(type_number, velocity):
        return [
            f"\nPATH_TYPE = {type_number}",
            f"$VEL.CP={velocity:.{precision}f}",
        ]

    def format_motion(position_string, is_first, is_last):
        if is_first:
            return f"PTP {{{position_string}}} C_PTP"
        elif is_last:
            return [
                f"PTP {{{position_string}}} C_DIS",
                f"\nWAIT FOR $TIMER[{timer}] > {mlt}",
            ]
        else:
            return f"LIN {{{position_string}}} C_DIS"

    # --- Main loop ---
    for idx, entry in enumerate(gcode):
        current_layer = entry["Layer"]
        current_type = entry["Type"]
        current_velocity = entry["Vel_CP_Max"]
        type_number = type_mapping.get(current_type, 0)
        line_buffer = []

        # Handle layer change
        if current_layer != previous_layer:
            if previous_layer is not None:
                if not split_layers:
                    krl_lines.extend(end_layer())
                else:
                    current_block.extend(end_layer())
                    current_block.append("END")
                    layer_blocks.append(current_block)
                    current_block = []

            if split_layers and idx != 0:
                current_block = [f"DEF {project_name}_{len(layer_blocks):03d} ()"]

            line_buffer.extend(start_layer(current_layer))
            previous_layer = current_layer

        # Handle type change (path type and velocity)
        if current_type != previous_type:
            velocity = vel_tvl if current_type == "travel" else current_velocity
            line_buffer.extend(set_path_type_and_velocity(type_number, velocity))
            previous_type = current_type

        # Format position
        x = format_value(entry["X"], max_lengths["X"])
        y = format_value(entry["Y"], max_lengths["Y"])
        z = format_value(entry["Z"], max_lengths["Z"])

        if current_type == "retract":
            e1_value = -1
        elif current_type == "protract":
            e1_value = 0
        elif entry["Move"] == "G1":
            e1_value = entry["RPM"] if pump_control else entry["Voltage"]
        else:
            e1_value = -1

        e1 = format_value(
            e1_value,
            max_lengths["RPM"] if pump_control else max_lengths["Voltage"],
        )

        a_str = format_value(a, max_lengths["A"])
        b_str = format_value(b, max_lengths["B"])
        c_str = format_value(c, max_lengths["C"])

        position_string = (
            f"X {x}, Y {y}, Z {z}, "
            f"A {a_str}, B {b_str}, C {c_str}, "
            f"E1 {e1}, E2 + 0, E3 + 0, E4 + 0"
        )

        position += 1
        move_command = format_motion(
            position_string, position == 0, position == len(gcode) - 1
        )

        if isinstance(move_command, list):
            line_buffer.extend(move_command)
        else:
            line_buffer.append(move_command)

        # Store lines
        if split_layers:
            current_block.extend(line_buffer)
        else:
            krl_lines.extend(line_buffer)

    # Final handling for split layers
    if split_layers:
        if current_block:
            current_block.append(f"\n$TIMER_STOP[{timer}] = TRUE")
            current_block.append("END")
            layer_blocks.append(current_block)
        return layer_blocks
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
        gcode=sample_gcode,
        type_mapping=type_map,
        a=0,
        b=0,
        c=180,
        vel_tvl=0.35,
        pump_control=True,
        precision=2,
        axis_min=a_min,
        axis_max=a_max,
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
