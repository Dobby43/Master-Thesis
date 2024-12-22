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
