import re
from typing import List, Dict, Union
from gcode import slicer_keywordmanager

# Define dictionaries for different slicers
SLICER_PATTERNS = slicer_keywordmanager.get_slicer_pattern()


def translate_type(type_name: str, slicer: str, type_values: Dict) -> str:
    """
    DESCRIPTION:
    Translates a raw type name from the slicer into a unified category.

    ARGUMENTS:
    type_name: The raw type name from the slicer.
    slicer: The slicer name (e.g., "CURA").
    type_values: A dictionary mapping slicer types to unified categories.

    RETURNS:
    A string representing the unified type category or "UNKNOWN" if no match is found.
    """
    slicer = slicer.upper()
    for category, slicers in type_values.items():
        if type_name in slicers.get(slicer, []):
            return category
    return "UNKNOWN"


def process_gcode(
    gcode: List[str], slicer: str, type_values: Dict
) -> List[Dict[str, Union[str, float, int, None]]]:
    """
    DESCRIPTION:
    Processes G-code lines to extract attributes and filter only meaningful G0 or G1 moves.
    Updates missing Z values, infers layer and type information, and maintains the current state.

    ARGUMENTS:
    gcode: List of G-code lines as strings.
    slicer: The slicer name (e.g., "CURA").
    type_values: Dictionary containing mappings of slicer types and attributes.

    RETURNS:
    A list of dictionaries, each containing processed G-code attributes, including:
    - Move type (G0 or G1)
    - X, Y, Z coordinates
    - Layer
    - Type
    """
    # Select patterns for the given slicer
    slicer = slicer.upper()
    if slicer not in SLICER_PATTERNS:
        raise ValueError(f"Unsupported slicer: {slicer}")
    slicer_patterns = SLICER_PATTERNS[slicer]
    layer_pattern = slicer_patterns.get("Layer", r";LAYER:(\d+)")
    type_pattern = slicer_patterns.get("Type", r";TYPE:(.+)")
    gcode_pattern = r"(G[01])?(?:\s*F[\d\.]+)?(?:\s*X\s*([-?\d\.]+))?(?:\s*Y\s*([-?\d\.]+))?(?:\s*Z\s*([-?\d\.]+))?(?:\s*E[-?\d\.]+)?"

    processed_gcode = []
    current_layer = None
    current_type = None

    # Initialize current X, Y, Z values
    current_x, current_y, current_z = None, None, None

    for line in gcode:
        line = line.strip()
        gcode_entry = {
            "Move": None,
            "X": None,
            "Y": None,
            "Z": None,
            "Layer": current_layer,
            "Type": current_type,
        }

        # Match Layer and update
        layer_match = re.match(layer_pattern, line)
        if layer_match:
            current_layer = int(layer_match.group(1))
            continue

        # Match Type and translate
        type_match = re.match(type_pattern, line)
        if type_match:
            raw_type = type_match.group(1)
            current_type = translate_type(raw_type, slicer, type_values)
            continue

        # Match G-code coordinates and decide move type
        gcode_match = re.match(gcode_pattern, line)
        if gcode_match:
            gcode_entry["Move"] = gcode_match.group(1)

            # Check if the line contains an extrusion value (E)
            has_extrusion = "E" in line

            # Determine move type
            gcode_entry["Move"] = "G1" if has_extrusion else "G0"

            # Extract and update coordinates
            new_x = float(gcode_match.group(2)) if gcode_match.group(2) else current_x
            new_y = float(gcode_match.group(3)) if gcode_match.group(3) else current_y
            new_z = float(gcode_match.group(4)) if gcode_match.group(4) else current_z

            # Skip if the coordinates haven't changed
            if new_x == current_x and new_y == current_y and new_z == current_z:
                continue

            # Update the current coordinates
            current_x, current_y, current_z = new_x, new_y, new_z

            # Assign current coordinates to the entry
            gcode_entry["X"] = current_x
            gcode_entry["Y"] = current_y
            gcode_entry["Z"] = current_z

            # Update Layer and Type
            gcode_entry["Layer"] = current_layer
            gcode_entry["Type"] = (
                "TRAVEL" if gcode_entry["Move"] == "G0" else current_type
            )

            processed_gcode.append(gcode_entry)

    return processed_gcode
