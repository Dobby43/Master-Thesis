def linetype_patterns():
    """
    Returns a dictionary of linetype patterns.
    """
    return {
        "solid": [(10.0, True)],
        "dashed": [(10.0, False), (5.0, True), (10.0, False)],
        "dotted": [(2.0, False), (2.0, True)],
        "dash_dot": [(10.0, False), (5.0, True), (2.0, False), (5.0, True)],
    }
