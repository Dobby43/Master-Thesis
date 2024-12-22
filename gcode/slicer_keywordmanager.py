def get_slicer_pattern() -> dict:
    """
    DESCRIPTION:
    Provides slicer-specific regular expression patterns for parsing G-code files.

    RETURNS:
    A dictionary containing slicer patterns for different slicers, such as CURA and ORCA.
    Each slicer key contains sub-patterns for identifying layers and types in the G-code.
    """
    slicer_patterns = {
        "CURA": {
            "Layer": r";LAYER:(\d+)",  # Pattern to identify layers in CURA
            "Type": r";TYPE:(.+)",  # Pattern to identify types in CURA
        },
        "ORCA": {
            "Layer": r";LAYER:(\d+)",  # Pattern to identify layers in ORCA
            "Type": r";TYPE:(.+)",  # Pattern to identify types in ORCA
        },
    }

    return slicer_patterns
