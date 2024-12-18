def layer_structure(LAYER_MAX):
    """
    Returns a dictionary defining the Rhino layer structure.
    """
    return {
        "toolpath": {
            "color": [255, 255, 255],
            "sublayer_color": [0, 0, 255],
            "dynamic_sublayers": True,
            "max_sublayers": LAYER_MAX,
        },
        "printbed": {
            "color": [128, 128, 128],  # Gray
            "sublayer_color": [128, 128, 128],
            "sublayers": [],
        },
    }
