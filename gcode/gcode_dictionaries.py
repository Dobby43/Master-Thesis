def get_slicer_pattern():
    """
    Returns the translation and slicer patterns used for G-code processing.
    :return: A tuple containing TRANSLATION_PATTERNS and SLICER_PATTERNS.
    """
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

    return SLICER_PATTERNS


def get_type_values():
    TYPE_VALUES = {
        "SUPPORT": {
            "CURA": ["SUPPORT", "SUPPORT-INTERFACE"],
            "ORCA": ["Support", "Support interface"],
            "Color": "green",
        },
        "WALL_OUTER": {
            "CURA": ["WALL-OUTER"],
            "ORCA": ["Outer wall", "Overhang wall"],
            "Color": "blue",
        },
        "WALL_INNER": {
            "CURA": ["WALL-INNER"],
            "ORCA": ["Inner wall"],
            "Color": "cyan",
        },
        "SURFACE": {
            "CURA": ["SKIN"],
            "ORCA": ["Bottom surface", "Top surface"],
            "Color": "yellow",
        },
        "INFILL": {
            "CURA": ["FILL"],
            "ORCA": ["Internal solid infill", "Spars infill"],
            "Color": "red",
        },
        "CURB": {
            "CURA": ["SKIRT", "BRIM", "RAFT"],
            "ORCA": ["Skirt", "Brim", "Raft"],
            "Color": "magenta",
        },
        "BRIDGE": {
            "CURA": [],
            "ORCA": ["Bridge", "Internal Bridge"],
            "Color": "orange",
        },
        "UNKNOWN": {
            "Color": "lime",
        },
        "TRAVEL": {
            "Color": "grey",
        },
    }
    return TYPE_VALUES
