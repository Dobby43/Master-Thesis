def process_points(data: list[dict]) -> list[dict]:
    """
    Processes points, inserts transition points, assigns numbering, and determines point roles.
    Transition points copy position from the previous point and 'Move' from the next point.
    :param data: List of dictionaries with point data ('Move', 'X', 'Y', 'Z', 'Layer', 'Type').
    :return: List of processed points with additional attributes ('poly_num', 'point_num', 'point_info').
    """
    processed_points = []
    current_layer = None
    current_type = None

    # Insert transition points
    for i, entry in enumerate(data):
        layer = entry["Layer"]
        move_type = entry["Type"]

        # Add a transition point if layer or type changes
        if current_layer != layer or current_type != move_type:
            if processed_points:
                last_point = processed_points[-1]
                transition_point = {
                    "Move": entry["Move"],
                    "X": last_point["X"],
                    "Y": last_point["Y"],
                    "Z": last_point["Z"],
                    "Layer": layer,
                    "Type": move_type,
                }
                processed_points.append(transition_point)

            current_layer = layer
            current_type = move_type

        # Add the current point
        processed_points.append(entry)

    # Assign numbering and determine roles
    numbered_points = []
    current_layer = None
    current_type = None
    poly_num = 0  # Polyline counter
    point_num = 0  # Point counter within polyline

    for i, entry in enumerate(processed_points):
        layer = entry["Layer"]
        move_type = entry["Type"]
        move_command = entry["Move"]

        # Reset polyline number when the layer changes
        if current_layer != layer:
            poly_num = 0
            current_layer = layer
            current_type = None

        # Increment polyline number on type change
        if current_type != move_type:
            if current_type is not None:
                poly_num += 1
            current_type = move_type
            point_num = 0  # Reset point number

        # Determine the point role ("start", "stop", "0", "1")
        if move_command == "G1" and point_num == 0:  # Start of an extrusion
            point_info = "start"
        elif move_command == "G1" and (
            i + 1 == len(processed_points) or processed_points[i + 1]["Move"] != "G1"
        ):  # End of an extrusion
            point_info = "stop"
        elif move_command == "G0":  # Non-extrusion travel
            point_info = "0"
        else:  # Default extrusion point
            point_info = "1"

        # Assign numbering and point_info
        numbered_point = entry.copy()
        numbered_point["poly_num"] = poly_num
        numbered_point["point_num"] = point_num
        numbered_point["point_info"] = point_info
        numbered_points.append(numbered_point)

        point_num += 1  # Increment point counter

    return numbered_points
