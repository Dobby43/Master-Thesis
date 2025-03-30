def linetype_patterns():
    """
    DESCRIPTION:
    Function to store custom linetypes

    :return: Dictionary of custom linetypes;
    line defined as list of segments (float [mm] defining the length of segment, bool defining if visible [True] or not [False]),
    """
    return {
        "solid": [(10.0, True)],
        "dashed": [(10.0, False), (5.0, True), (10.0, False)],
        "dotted": [(2.0, False), (2.0, True)],
        "dash_dot": [(10.0, False), (5.0, True), (2.0, False), (5.0, True)],
    }
