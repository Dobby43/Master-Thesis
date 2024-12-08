def layer_structure(LAYER_MAX):
    """
    Returns a dictionary defining the Rhino layer structure.
    :param LAYER_MAX: Maximum number of dynamic sublayers for the 'toolpath' parent layer.
    :return: Dictionary defining the layer structure.
    """
    return {
        "toolpath": {
            "color": [255, 255, 255],  # White
            "sublayer_color": [0, 0, 255],  # Blue for sublayers
            "dynamic_sublayers": True,
            "max_sublayers": LAYER_MAX,
        },
        "printbed": {
            "color": [128, 128, 128],  # Gray
            "sublayer_color": [128, 128, 128],  # Same color for sublayers
            "sublayers": [],  # No dynamic sublayers
        },
    }
