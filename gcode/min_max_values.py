import re
from typing import List, Dict, Union, Any


def get_max_values(gcode: List[str]) -> Dict[str, Union[float, None, Any]]:
    """
    Searches G-Code for maximum values of X, Y, and Z.

    :param gcode: Original list of G-code lines.
    :type gcode: List[str]
    :returns: Dictionary containing the maximum values for X, Y, and Z coordinates.
    :rtype: dict[str, Union[float, None]]
    """

    x_max, y_max, z_max = None, None, None

    # Updated pattern to match optional blocks in G-code lines
    pattern = r"(G[01])?(?:\s*F\d+)?(?:\s*X([-?\d\.]+))?(?:\s*Y([-?\d\.]+))?(?:\s*Z([-?\d\.]+))?(?:\s*E[-?\d\.]+)?"

    for line in gcode:
        match = re.search(pattern, line)

        if match:
            x_val = float(match.group(2)) if match.group(2) else None
            y_val = float(match.group(3)) if match.group(3) else None
            z_val = float(match.group(4)) if match.group(4) else None

            # Update maximum values for X, Y, and Z
            if x_val is not None:
                x_max = x_val if x_max is None else max(x_max, x_val)
            if y_val is not None:
                y_max = y_val if y_max is None else max(y_max, y_val)
            if z_val is not None:
                z_max = z_val if z_max is None else max(z_max, z_val)

    return {"x_max": x_max, "y_max": y_max, "z_max": z_max}


def get_min_values(gcode: List[str]) -> dict[str, float | None | Any]:
    """
    searches G-Code for minimum value of X, Y and Z
    :param gcode: Original list of G-code lines.
    :type gcode: List[str]
    :returns: Dictionary containing the minimum values for X, Y, and Z coordinates.
    :rtype: dict[str, float | None]
    """

    x_min, y_min, z_min = None, None, None
    pattern = r"(G[01])?(?:\s*F\d+)?(?:\s*X([-?\d\.]+))?(?:\s*Y([-?\d\.]+))?(?:\s*Z([-?\d\.]+))?(?:\s*E[-?\d\.]+)?"

    for line in gcode:
        match = re.search(pattern, line)

        if match:
            x_val = float(match.group(2)) if match.group(2) else None
            y_val = float(match.group(3)) if match.group(3) else None
            z_val = float(match.group(4)) if match.group(4) else None

            # Aktualisiere Min-Werte
            if x_val is not None:
                x_min = x_val if x_min is None else min(x_min, x_val)
            if y_val is not None:
                y_min = y_val if y_min is None else min(y_min, y_val)
            if z_val is not None:
                z_min = z_val if z_min is None else min(z_min, z_val)

    return {"x_min": x_min, "y_min": y_min, "z_min": z_min}
