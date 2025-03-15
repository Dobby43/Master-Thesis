import numpy as np
import math


def get_linewidth(points: list, flow: dict, diam_fil: float) -> list:
    """
    Berechnet die Linienstärke basierend auf Extrusionswerten.

    :param points: Liste von Dictionaries mit Positions- und Extrusionsdaten
    :param flow: Dictionary mit Flusswerten für verschiedene Drucktypen
    :param diam_fil: Filamentdurchmesser in mm
    :return: Liste mit berechneten Linienstärken
    """

    previous_point_x = 0
    previous_point_y = 0
    line_widths = []

    for i, point in enumerate(points):
        layer_h = point["Layer_Height"]
        current_x = point["X"]
        current_y = point["Y"]
        e_val = point["E_Rel"]
        current_type = point["Type"]

        if point["Move"] == "G1" and previous_point_x is not None:
            distance = math.sqrt(
                (previous_point_x - current_x) ** 2
                + (previous_point_y - current_y) ** 2
            )
            if distance > 0 and layer_h > 0 and flow[current_type] > 0:
                line_width = (np.pi / 4 * diam_fil**2 * e_val) / (
                    layer_h * flow[current_type] * distance
                )
            else:
                line_width = 0

            line_widths.append(line_width)
        else:
            line_widths.append(0)

        # Aktualisiere die vorherige Position
        previous_point_x = current_x
        previous_point_y = current_y

    return line_widths


if __name__ == "__main__":
    points = [
        {
            "Move": "G0",
            "X": 1125.0,
            "Y": 2262.5,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G0",
            "X": 1137.43,
            "Y": 2274.93,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G0",
            "X": 1150.0,
            "Y": 2287.5,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1150.0,
            "Y": 2287.5,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1150.0,
            "Y": 2212.5,
            "Z": 30.0,
            "E_Rel": 57.296,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 875.0,
            "Y": 2212.5,
            "Z": 30.0,
            "E_Rel": 210.085,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 875.0,
            "Y": 2287.5,
            "Z": 30.0,
            "E_Rel": 57.296,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1150.0,
            "Y": 2287.5,
            "Z": 30.0,
            "E_Rel": 210.085,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G0",
            "X": 1150.0,
            "Y": 2287.5,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
    ]

    flow = {
        "wall_outer": 100,
        "wall_inner": 100,
        "surface": 100,
        "infill": 100,
        "bridge": 100,
        "curb": 100,
        "support": 100,
        "unknown": 100,
    }
    diam_fil = 25

    # Berechne die Linienstärken
    linewidths = get_linewidth(points, flow, diam_fil)

    # Ergebnisse ausgeben
    for i, lw in enumerate(linewidths):
        print(f"Punkt {i}: Linienstärke = {lw:.2f} mm")
