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
            "Linetype": "Continuous",
        },
        "WALL_OUTER": {
            "CURA": ["WALL-OUTER"],
            "ORCA": ["Outer wall", "Overhang wall"],
            "Color": "blue",
            "Linetype": "Continuous",
        },
        "WALL_INNER": {
            "CURA": ["WALL-INNER"],
            "ORCA": ["Inner wall"],
            "Color": "cyan",
            "Linetype": "Continuous",
        },
        "SURFACE": {
            "CURA": ["SKIN"],
            "ORCA": ["Bottom surface", "Top surface"],
            "Color": "yellow",
            "Linetype": "Continuous",
        },
        "INFILL": {
            "CURA": ["FILL"],
            "ORCA": ["Internal solid infill", "Spars infill"],
            "Color": "red",
            "Linetype": "Continuous",
        },
        "CURB": {
            "CURA": ["SKIRT", "BRIM", "RAFT"],
            "ORCA": ["Skirt", "Brim", "Raft"],
            "Color": "magenta",
            "Linetype": "Continuous",
        },
        "BRIDGE": {
            "CURA": [],
            "ORCA": ["Bridge", "Internal Bridge"],
            "Color": "orange",
            "Linetype": "Continuous",
        },
        "UNKNOWN": {
            "Color": "lime",
            "Linetype": "DashDot",
        },
        "TRAVEL": {
            "Color": "grey",
            "Linetype": "Dashed",
        },
    }
    return TYPE_VALUES
