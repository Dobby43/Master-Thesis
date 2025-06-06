from typing import Any


def layer_structure(layer_max: int) -> dict[str, dict[str, Any]]:
    """
    DESCRIPTION:
    Returns a dictionary defining the Rhino layer structure.
    Dynamic sublayers enables you to create n sublayers with a 4-digit number starting from 0000
    If dynamic sublayers is disabled a list[str] of sublayer names can be given

    :param layer_max: maximum layer number for print

    :return: dictionary defining the Rhino layer structure
    """
    return {
        "toolpath": {
            "color": [255, 255, 255],
            "dynamic_sublayers": True,
            "max_sublayers": layer_max,
            "sublayer_color": [0, 0, 255],
        },
        "printbed": {
            "color": [128, 128, 128],  # Gray
            "dynamic_sublayers": False,
            "sublayers": [],
            "sublayer_color": [128, 128, 128],
        },
        "robot": {
            "color": [242, 92, 25],
            "dynamic_sublayers": False,
            "sublayers": [],
            "sublayer_color": [242, 92, 25],
        },
    }
