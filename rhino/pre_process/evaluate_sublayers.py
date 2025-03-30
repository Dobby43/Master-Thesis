def evaluate_sublayers_printbed(points_list: list[dict]) -> dict[int, int]:
    """
    DESCRIPTION:
    Evaluates how many line-sublayers are needed per print layer.

    :param points_list: List of dictionaries with keys 'Layer' and 'Line'.

    :return: Dictionary mapping Layer -> max number of sublayers needed (line count).
    """
    layer_line_counts = {}

    for point in points_list:
        layer = point["Layer"]
        line = point["Line"]
        # If layer doesn't already exist save layer and line
        if layer not in layer_line_counts:
            layer_line_counts[layer] = line
        # If layer exists save maximum of current line count and saved line count
        else:
            layer_line_counts[layer] = max(layer_line_counts[layer], line)

    return {layer: max_line for layer, max_line in layer_line_counts.items()}


if __name__ == "__main__":
    # Beispielhafte Punktdaten zur Simulation
    test_points = [
        {
            "Move": "G0",
            "X": -934.78,
            "Y": 270.82,
            "Z": 813.89,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
            "Line": 0,
            "Point": 0,
            "Point_Info": "0",
        },
        {
            "Move": "G0",
            "X": 925.0,
            "Y": 2162.5,
            "Z": 15.0,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
            "Line": 0,
            "Point": 1,
            "Point_Info": "0",
        },
        {
            "Move": "G1",
            "X": 925.0,
            "Y": 2162.5,
            "Z": 15.0,
            "E_Rel": -100.0,
            "Layer": 0,
            "Type": "retract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
            "Line": 0,
            "Point": 2,
            "Point_Info": "retract",
        },
        {
            "Move": "G0",
            "X": 1100.0,
            "Y": 2162.5,
            "Z": 15.0,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
            "Line": 0,
            "Point": 3,
            "Point_Info": "0",
        },
        {
            "Move": "G1",
            "X": 1100.0,
            "Y": 2162.5,
            "Z": 15.0,
            "E_Rel": 100.0,
            "Layer": 0,
            "Type": "protract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
            "Line": 0,
            "Point": 4,
            "Point_Info": "protract",
        },
        {
            "Move": "G1",
            "X": 1100.0,
            "Y": 2162.5,
            "Z": 15.0,
            "E_rel": 0,
            "Layer": 0,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0,
            "Line": 1,
            "Point": 0,
            "Point_Info": "start",
        },
    ]

    result = evaluate_sublayers_printbed(test_points)

    print("Ermittelte Sub-Sublayer-Anzahl je Layer:")
    for layers, count in result.items():
        print(f"  Layer {layers:04d}: {count} Linien")
