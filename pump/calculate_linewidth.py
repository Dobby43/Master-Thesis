import numpy as np
import math
from typing import Any


def get_linewidth(
    points: list, flow: dict, diam_fil: float
) -> tuple[list[float | int | Any], int | Any]:
    """
    DESCRIPTION:
    Calculation of linewidth and total volume based on extrusion value and flow

    :param points: list of dicts of positional data and extrusion values
    :param flow: Dictionary of flow for specific line type
    :param diam_fil: diameter of filament/hose in mm

    :return: tuple of list of calculated linewidth and total volume
    """

    # Set Zero values for initial calculation (as points always starts with a travel this ia valid)
    previous_point_x = 0
    previous_point_y = 0
    volume = 0
    line_widths = []

    # Get necessary information from point
    for i, point in enumerate(points):
        layer_h = point["Layer_Height"]
        current_x = point["X"]
        current_y = point["Y"]
        e_val = point["E_Rel"]
        current_type = point["Type"]

        # Calculate flow only for non travel moves
        if (
            point["Move"] == "G1"
            and previous_point_x is not None
            and current_type not in ("retract", "protract")
        ):
            length = math.sqrt(
                (previous_point_x - current_x) ** 2
                + (previous_point_y - current_y) ** 2
            )
            # Calculation of linewidth assuming a rectangular cross-section and round filament
            line_width = (np.pi / 4 * diam_fil**2 * e_val) / (
                layer_h * flow[current_type] / 100 * length
            )
            line_widths.append(line_width)
            # Sum up individual volumes to find the total filament volume used
            volume += length * line_width * layer_h
        else:
            line_widths.append(0)

        # Set previous position to current position
        previous_point_x = current_x
        previous_point_y = current_y

    return line_widths, volume


if __name__ == "__main__":
    p = [
        {
            "Move": "G1",
            "X": 1150.0,
            "Y": 2287.5,
            "Z": 105.0,
            "E_Rel": 0,
            "Layer": 6,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Line": 5,
            "Point": 0,
            "Point_Info": "start",
        },
        {
            "Move": "G1",
            "X": 1150.0,
            "Y": 2212.5,
            "Z": 105.0,
            "E_Rel": 57.296,
            "Layer": 6,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Line": 5,
            "Point": 1,
            "Point_Info": "1",
        },
        {
            "Move": "G1",
            "X": 1075.0,
            "Y": 2212.5,
            "Z": 105.0,
            "E_Rel": 57.296,
            "Layer": 6,
            "Type": "retract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Line": 5,
            "Point": 2,
            "Point_Info": "1",
        },
        {
            "Move": "G1",
            "X": 1075.0,
            "Y": 2287.5,
            "Z": 105.0,
            "E_Rel": 57.296,
            "Layer": 6,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Line": 5,
            "Point": 3,
            "Point_Info": "1",
        },
        {
            "Move": "G1",
            "X": 1150.0,
            "Y": 2287.5,
            "Z": 105.0,
            "E_Rel": 57.296,
            "Layer": 6,
            "Type": "protract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Line": 5,
            "Point": 4,
            "Point_Info": "stop",
        },
        {
            "Move": "G0",
            "X": 1150.0,
            "Y": 2287.5,
            "Z": 105.0,
            "E_Rel": -100,
            "Layer": 6,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Line": 5,
            "Point": 4,
            "Point_Info": "stop",
        },
    ]

    f = {
        "wall_outer": 100,
        "wall_inner": 100,
        "surface": 100,
        "infill": 100,
        "bridge": 100,
        "curb": 100,
        "support": 100,
        "unknown": 100,
    }
    diam_filament = 25

    # Berechne die Linienstärken
    linewidths, volumetric = get_linewidth(p, f, diam_filament)

    # Ergebnisse ausgeben
    for p, lw in enumerate(linewidths):
        print(f"Punkt {p}: Linienstärke = {lw:.2f} mm")

    print(volumetric)
