import re
from typing import List, Dict, Union

# Define dictionaries for different slicers
SLICER_PATTERNS = {
    "CURA": {
        "Layer": r";LAYER:(\d+)",
        "Type": r";TYPE:(.+)",
    },
    "ORCA": {
        "Layer": r";LAYER:(\d+)",
        "Type": r";TYPE:(.+)",
    },
}

TRANSLATION_PATTERNS = {
    "CURA": {
        "SUPPORT": "SUPPORT",
        "SUPPORT-INTERFACE": "SUPPORT",
        "WALL-OUTER": "WALL_OUTER",
        "WALL-INNER": "WALL_INNER",
        "SKIN": "SURFACE",
        "FILL": "INFILL",
        "SKIRT": "CURB",
        "BRIM": "CURB",
        "RAFT": "CURB",
    },
    "ORCA": {
        "Support": "SUPPORT",
        "Support interface": "SUPPORT",
        "Outer wall": "WALL_OUTER",
        "Overhang wall": "WALL_OUTER",
        "Bridge": "WALL_OUTER",
        "Inner wall": "WALL_INNER",
        "Bottom surface": "SURFACE",
        "Top surface": "SURFACE",
        "Internal solid infill": "INFILL",
        "Spars infill": "INFILL",
        "Skirt": "CURB",
        "Brim": "CURB",
        "Raft": "CURB",
    },
}


def process_gcode(
    gcode: List[str],
    slicer: str,
) -> List[Dict[str, Union[str, float, int, None]]]:
    """
    Processes G-code lines to extract attributes and keep only lines with meaningful G0 or G1 moves.
    Updates missing Z values and Type with the last known value and maintains Layer information.

    :param gcode: List of G-code lines.
    :type gcode: List[str]
    :param slicer: The slicer used to generate the G-code (e.g., "CURA", "ORCA").
    :type slicer: str
    :returns: Processed G-code lines containing only meaningful G0 or G1 moves with attributes.
    :rtype: List[Dict[str, Union[str, float, int, None]]]
    """
    # Select patterns and translations for the given slicer
    slicer = slicer.upper()
    if slicer not in SLICER_PATTERNS:
        raise ValueError(f"Unsupported slicer: {slicer}")
    slicer_patterns = SLICER_PATTERNS[slicer]
    translation_patterns = TRANSLATION_PATTERNS.get(slicer, {})

    # Patterns for Layer, Type, and G-code commands
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

        # Step 1: Match Layer and update
        layer_match = re.match(layer_pattern, line)
        if layer_match:
            current_layer = int(layer_match.group(1))
            continue  # Skip to the next line after updating Layer

        # Step 2: Match Type and update current_type
        type_match = re.match(type_pattern, line)
        if type_match:
            raw_type = type_match.group(1)
            current_type = translation_patterns.get(raw_type, "UNKNOWN")
            continue  # Skip to the next line after updating Type

        # Step 3: Match G-code commands (Move and coordinates)
        gcode_match = re.match(gcode_pattern, line)
        if gcode_match:
            # Update Move (G0 or G1)
            gcode_entry["Move"] = gcode_match.group(1)

            # Skip lines without valid G0/G1 moves
            if not gcode_entry["Move"]:
                continue

            # Extract coordinates and update current values
            if gcode_match.group(2):
                current_x = float(gcode_match.group(2))
            if gcode_match.group(3):
                current_y = float(gcode_match.group(3))
            if gcode_match.group(4):
                current_z = float(gcode_match.group(4))

            # Assign current coordinates to the entry
            gcode_entry["X"] = current_x
            gcode_entry["Y"] = current_y
            gcode_entry["Z"] = current_z

            # Assign the current Layer and Type
            gcode_entry["Layer"] = current_layer
            if gcode_entry["Move"] == "G0":
                gcode_entry["Type"] = "TRAVEL"
            else:
                gcode_entry["Type"] = current_type

            # Append the processed entry
            processed_gcode.append(gcode_entry)

    return processed_gcode
