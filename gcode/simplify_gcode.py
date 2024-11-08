import re
from typing import List, Dict, Union, Any

# Define necessary G-code commands to keep
DICTIONARY = [
    "G0",
    "G1",
    ";LAYER",
    ";TYPE",
]

import re
from typing import List, Dict, Union


def process_gcode(
    gcode: List[str],
) -> List[Dict[str, Union[str, float, int, None]]]:
    """
    Processes G-code lines and extracts attributes for Move (G0/G1), X, Y, Z values, Layer, and Type.
    Updates missing Z values and Type with the last known value and maintains Layer information.

    :param gcode: List of G-code lines.
    :type gcode: List[str]
    :returns: Processed G-code with attributes.
    :rtype: List[Dict[str, Union[str, float, int, None]]]
    """
    processed_gcode = []
    current_layer = None
    current_z = None  # Store the last known Z value
    current_type = None  # Store the last known Type

    # Regular expressions
    layer_pattern = r";LAYER:(\d+)"
    type_pattern = r";TYPE:(.+)"  # Matches ;TYPE comments
    gcode_pattern = r"(G[01])?(?:\s*F[\d\.]+)?(?:\s*X\s*([-?\d\.]+))?(?:\s*Y\s*([-?\d\.]+))?(?:\s*Z\s*([-?\d\.]+))?(?:\s*E[-?\d\.]+)?"

    for line in gcode:
        line = line.strip()  # Remove leading/trailing whitespaces
        gcode_entry = {
            "Move": None,
            "X": None,
            "Y": None,
            "Z": None,
            "Layer": current_layer,
            "Type": current_type,
        }

        # Update layer if layer pattern is found
        layer_match = re.match(layer_pattern, line)
        if layer_match:
            current_layer = (
                int(layer_match.group(1)) + 1
            )  # Convert to integer and increment for 1-based indexing
            gcode_entry["Layer"] = current_layer
            processed_gcode.append(gcode_entry)
            continue

        # Match ;TYPE comments
        type_match = re.match(type_pattern, line)
        if type_match:
            current_type = type_match.group(1)  # Update the current Type
            gcode_entry["Type"] = current_type
            processed_gcode.append(gcode_entry)
            continue

        # Match G0/G1 lines and extract attributes
        gcode_match = re.match(gcode_pattern, line)
        if gcode_match:
            gcode_entry["Move"] = gcode_match.group(1)  # Extract Move (G0/G1)

            # Extract X, Y, Z values if present
            if gcode_match.group(2):
                gcode_entry["X"] = float(gcode_match.group(2))
            if gcode_match.group(3):
                gcode_entry["Y"] = float(gcode_match.group(3))
            if gcode_match.group(4):
                current_z = float(gcode_match.group(4))  # Update current Z value
            gcode_entry["Z"] = current_z  # Use the last known Z value

            # Update Type and Layer in the entry
            gcode_entry["Layer"] = current_layer
            gcode_entry["Type"] = current_type

            # Add entry to processed G-code list
            processed_gcode.append(gcode_entry)

    return processed_gcode
