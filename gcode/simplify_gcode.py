import re
from typing import List, Dict, Union


def translate_type(type_name: str, slicer: str, type_values: Dict) -> str:
    """
    Translates a raw type name from the slicer into a unified category.
    """
    for category, slicers in type_values.items():
        if type_name in slicers.get(slicer, []):
            return category.lower()
    return "unknown"


def simplify_gcode(
    gcode: List[str],
    slicer: str,
    type_values: Dict,
    x_min: float,
    y_min: float,
    z_min: float,
) -> List[Dict[str, Union[str, float, int, None]]]:
    """
    Processes G-code and extracts relevant attributes, including layer height.
    Determines layers dynamically based on Z changes, including for travel moves.
    """

    # Step 1: Determine extrusion mode (M82/M83)
    absolute_mode = not any("M83" in line for line in gcode[:300])

    # Step 2: Define regex patterns
    type_pattern = r"(?i)[;$]?TYPE[:\s]*(.+)"
    gcode_pattern = r"(G[01])?(?:\s*F[\d\.]+)?(?:\s*X\s*([-?\d\.]+))?(?:\s*Y\s*([-?\d\.]+))?(?:\s*Z\s*([-?\d\.]+))?(?:\s*E\s*([-?\d\.]+))?"
    feedrate_pattern = r"(G[01])\s*F[\d\.]+$"
    g92_pattern = r"G92\s+E0"  # Matches "G92 E0"

    # Step 3: Initialize state variables
    precision = 3
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
            current_type = translate_type(raw_type, slicer, type_values)
            continue

        # Match G-code coordinates
        if gcode_match := re.match(gcode_pattern, line):
            move_type = gcode_match.group(1) or "G0"
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
            if new_z > last_layer_height_z:
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
                "X": round(current_x, precision),
                "Y": round(current_y, precision),
                "Z": round(current_z, precision),
                "E_Rel": round(e_relative, precision) if move == "G1" else 0,
                "Layer": current_layer,
                "Type": type_,
                "Layer_Height": layer_height,
            }

            processed_gcode.append(gcode_entry)

    return processed_gcode
