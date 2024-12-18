def linetype_patterns():
    """
    Returns a dictionary of linetype patterns.
    """
    return {
        "Continuous": [(10.0, True)],
        "Dashed": [(10.0, False), (5.0, True), (10.0, False)],
        "Dotted": [(2.0, False), (2.0, True)],
        "DashDot": [(10.0, False), (5.0, True), (2.0, False), (5.0, True)],
    }
