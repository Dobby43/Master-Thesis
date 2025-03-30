import re
from typing import List, Dict, Union


def translate_type(
    line_type_name: str, slicer: str, line_type_dict: Dict[str, list[str]]
) -> str:
    """
    DESCRIPTION:
    Translates a raw type name into a unified category using a flat type_dict.

    :param line_type_name: The raw type string found in the G-code.
    :param slicer: name of the used slicer defined in setup.Slicer.slicer_name.json
    :param line_type_dict: A dictionary containing the raw type names and unified names.

    :return:  The matching category (lowercase) or "unknown" if not found.
    """
    for category, raw_types in line_type_dict.items():
        if line_type_name in raw_types:
            return category.lower()

    print(f"[WARNING] Type '{line_type_name}' not recognized.")
    print(f"[INFO] Check setup.{slicer}.line_types_dict.json for linetypes.")
    print(f"[INFO] Type '{line_type_name}' named as 'unknown'.")
    return "unknown"


def simplify_gcode(
    gcode: List[str],
    slicer: str,
    type_dict: Dict,
    x_min: float,
    y_min: float,
    z_min: float,
) -> List[Dict[str, Union[str, float, int, None]]]:
    """
    DESCRIPTION:
    Processes G-code and extracts relevant attributes, including layer height.
    Determines layers dynamically based on Z changes, excluding z-height changes for travel moves.

    :param gcode: The raw G-code.
    :param slicer: name of the used slicer defined in setup.Slicer.slicer_name.json
    :param type_dict: A dictionary containing the raw type names and unified names.
    :param x_min: The minimum x-coordinate of the gcode (as start value)
    :param y_min: The minimum y-coordinate of the gcode (as start value)
    :param z_min: The minimum z-coordinate of the gcode (as start value)

    :return: A list of dictionaries containing the extracted attributes.
    [{"Move":,"X":,"Y":,"Z":, "E_Rel":, "Layer":, "Type":, "Layer_Height":},]

    """

    # Step 1: Determine extrusion mode (M82/M83)
    absolute_mode = not any("M83" in line for line in gcode[:300])

    # Step 2: Define regex patterns
    type_pattern = r"(?i)[;$]?TYPE[:\s]*(.+)"
    gcode_pattern = r"(G[01])?(?:\s*F[\d\.]+)?(?:\s*X\s*([-?\d\.]+))?(?:\s*Y\s*([-?\d\.]+))?(?:\s*Z\s*([-?\d\.]+))?(?:\s*E\s*([-?\d\.]+))?"
    feedrate_pattern = r"(G[01])\s*F[\d\.]+$"
    g92_pattern = r"G92\s+E0"  # Matches "G92 E0"

    # Step 3: Initialize state variables
    current_x, current_y, current_z = x_min, y_min, z_min
    last_extrusion = 0.0
    retract_value = None
    current_layer = 0  # Layer starts at 0 and increases with each Z change
    current_type = None

    # Initialize layer height with z_min
    last_layer_height_z = z_min
    layer_height = z_min

    processed_gcode = []

    # Step 4: Process each line
    for line in gcode:
        line = line.strip()

        # Skip feedrate-only lines
        if re.match(feedrate_pattern, line):
            continue

        # Handle G92 E0 (reset extrusion)
        if re.match(g92_pattern, line):
            last_extrusion = 0.0  # Reset last_extrusion for absolute mode
            continue

        # Match type and translate to unified category
        if type_match := re.match(type_pattern, line):
            raw_type = type_match.group(1)
            current_type = translate_type(raw_type, slicer, type_dict)
            continue

        # Match G-code coordinates
        if gcode_match := re.match(gcode_pattern, line):
            new_x = float(gcode_match.group(2)) if gcode_match.group(2) else current_x
            new_y = float(gcode_match.group(3)) if gcode_match.group(3) else current_y
            new_z = float(gcode_match.group(4)) if gcode_match.group(4) else current_z
            new_e = (
                float(gcode_match.group(5)) if gcode_match.group(5) else last_extrusion
            )

            # Calculate relative extrusion
            e_relative = new_e - last_extrusion if absolute_mode else new_e
            last_extrusion = new_e if absolute_mode else last_extrusion

            # Update coordinates
            current_x, current_y, current_z = new_x, new_y, new_z

            # Increase layer count if z-value changes
            if e_relative > 0 and new_z > last_layer_height_z:
                current_layer += 1
                layer_height = abs(new_z - last_layer_height_z)
                last_layer_height_z = new_z

            # Skip bis alle Koordinaten validiert sind
            if current_x is None or current_y is None or current_z is None:
                continue

            # Determine Move and Type
            if e_relative < 0:  # Retract
                retract_value = e_relative
                move = "G1"
                type_ = "retract"
            elif (
                retract_value and abs(e_relative - abs(retract_value)) <= 0.1
            ):  # Protract
                # tolerance for difference between retract and protract value
                move = "G1"
                type_ = "protract"
                retract_value = None
            else:
                move = "G1" if e_relative > 0 else "G0"
                type_ = current_type if move == "G1" else "travel"

            # Skip redundant entries
            if (
                processed_gcode
                and processed_gcode[-1]["X"] == current_x
                and processed_gcode[-1]["Y"] == current_y
                and processed_gcode[-1]["Z"] == current_z
                and e_relative == 0
            ):
                continue

            # Build the processed G-code entry
            gcode_entry = {
                "Move": move,
                "X": current_x,
                "Y": current_y,
                "Z": current_z,
                "E_Rel": e_relative if move == "G1" else 0,
                "Layer": current_layer,
                "Type": type_,
                "Layer_Height": layer_height,
            }

            processed_gcode.append(gcode_entry)

    return processed_gcode
