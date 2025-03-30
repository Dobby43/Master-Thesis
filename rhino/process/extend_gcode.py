def add_point_info(points: list[dict]) -> list[dict]:
    """
    DESCRIPTION:
    Function to bundle the expansion of the point list

    :param points: List of dictionaries with pint information

    :return: extended list of dictionaries with transition points and additional information on point numbering
    """

    points_processed = process_points(points)

    points_counted = assign_count_info(points_processed)

    points_info = assign_extrusion_info(points_counted)

    return points_info


def process_points(points: list[dict]) -> list[dict]:
    """
    DESCRIPTION:
    Processes points, inserts transition points based on type changes, assigns numbering, and determines point roles.
    Transition points copy coordinates and other values from the previous point,
    but 'Move', 'Layer', 'Layer_Height', and 'Type' are updated based on the current point.

    :param points: List of Dict of point information

    :return: List of Dict of points with additional points (duplicates for drawing separate lines for each given type)
    """
    processed_points = []
    previous_point = None  # Keeps track of the previous point for comparison

    for i, current_point in enumerate(points):
        current_type = current_point["Type"]
        current_move = current_point["Move"]

        # Add transition point if type changed (exclude defined exceptions)
        if previous_point:
            previous_type = previous_point["Type"]

            # If the type does not change, don't insert transition point
            if previous_type == current_type:
                processed_points.append(current_point)
                previous_point = current_point
                continue

            # No transition point added, if type change to retract or defined cases in list
            if current_type == "retract" or (previous_type, current_type) in {
                ("travel", "protract"),
                ("retract", "travel"),
                ("retract", "protract"),
            }:
                processed_points.append(current_point)
                previous_point = current_point
                continue

            # If valid type change; append point
            transition_point = {
                "Move": current_move,  # Move from current point
                "X": previous_point["X"],  # Coordinates of the previous point
                "Y": previous_point["Y"],
                "Z": previous_point["Z"],
                "E_rel": 0,  # Allways set to zero for transitional point as it's the start of a line
                "Layer": current_point["Layer"],  # layer of current point
                "Type": current_type,  # Type of current point
                "Layer_Height": current_point[
                    "Layer_Height"
                ],  # layerhight of current point
                "Reachable": previous_point["Reachable"],
                "Linewidth": 0,
                "Flow": 0,
                "RPM": 0,
                "Voltage": 0,
                "Vel_CP_Max": current_point["Vel_CP_Max"],
            }
            processed_points.append(transition_point)

        # Append current point
        processed_points.append(current_point)
        previous_point = current_point  # Update previous point info with current point

    return processed_points


def assign_count_info(processed_points: list[dict]) -> list[dict]:
    """
    DESCRIPTION:
    Assigns 'Line' and 'Point' numbers based on type changes and layer transitions.

    Rules:
    - Line count allways increases
    - Point count increases if line count doesn't change
    - Travel, Retract, Protract get handled as the same type.
    - For a change in layer both line and point counter get set to zero.
    - For a change in type (except Travel/Protract/Retract) line counter is increased by +1 and point counter is reset to zero.

    :param processed_points: List of Dict of point information (with point duplicates)

    :return: List of Dict of points with transition points and additional information on point numbering (Layer/line/Point)
    """

    previous_layer = 0
    previous_type = None
    line_counter = -1
    point_counter = 0

    # types handled as non-line-type changes
    ignored_type_transitions = {"travel", "retract", "protract"}

    for entry in processed_points:
        current_layer = entry["Layer"]
        current_type = entry["Type"]

        # If layer changes reset to zero
        if previous_layer != current_layer:
            line_counter = -1
            point_counter = 0
            previous_layer = current_layer
            previous_type = None

        # checks if type change can be ignored
        is_current_ignored = current_type in ignored_type_transitions
        is_previous_ignored = (
            previous_type in ignored_type_transitions if previous_type else False
        )

        # Wenn der Typ wechselt
        if previous_type != current_type:
            if is_previous_ignored and not is_current_ignored:
                # Change from travel/retract/protract -> counted type (e.g. wall_outer)
                line_counter += 1
                point_counter = 0
            elif not is_previous_ignored and is_current_ignored:
                # Change from counted type -> travel/retract/protract
                line_counter += 1
                point_counter = 0
            elif not is_previous_ignored and not is_current_ignored:
                # Change in between to counted types (e.g. wall_outer -> infill)
                line_counter += 1
                point_counter = 0

        # Directly update the entry
        entry.update({"Line": line_counter, "Point": point_counter})

        point_counter += 1
        previous_type = current_type

    return processed_points


def assign_extrusion_info(counted_points: list[dict]) -> list[dict]:
    """
    DESCRIPTION:
    Assigns 'Point_Info' based on movement type and position within a line.

    Rules:
    - Travel -> Point_Info = "0"
    - Protract -> Point_Info = "protract""
    - Retract -> Point_Info = "retract"
    - If Point == 0 -> "start"
    - If last point of line or change in line-type → "stop" (except for current line type being in ignored line-types)
    - Else:
      - Move == G1 -> "1"
      - Move == G0 -> "0"

    :param counted_points: List of Dict of point information with already count info added

    :return: List of Dict of points with additional information on extrusion info
    """

    ignored_type_transitions = {"travel", "retract", "protract"}

    # Iteration with zip to access both current and next point (+[None] to iterate over the last point as well)
    for current_entry, next_entry in zip(counted_points, counted_points[1:] + [None]):
        move = current_entry["Move"]
        line_type = current_entry["Type"]
        point = current_entry["Point"]

        # Set information for different types
        if line_type == "travel":
            point_info = "0"
        elif line_type == "protract":
            point_info = "protract"
        elif line_type == "retract":
            point_info = "retract"
        elif point == 0:
            point_info = "start"
        elif (
            next_entry is not None  # Assures there is a next point available
            and line_type
            not in ignored_type_transitions  # line_type != travel, retract oder protract
            and next_entry["Type"] != line_type  # Checks if type change is made
        ):
            point_info = "stop"

        else:
            point_info = "1" if move == "G1" else "0"

        current_entry.update({"Point_Info": point_info})
    if counted_points:
        counted_points[0].update({"Point_Info": "beginning"})
        counted_points[-1].update({"Point_Info": "end"})

    return counted_points


if __name__ == "__main__":

    p = [
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
        },
        {
            "Move": "G0",
            "X": 462.5,
            "Y": 2250.0,
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
        },
        {
            "Move": "G1",
            "X": 462.5,
            "Y": 2250.0,
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
        },
        {
            "Move": "G1",
            "X": 462.5,
            "Y": 2250.0,
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
        },
        {
            "Move": "G1",
            "X": 737.5,
            "Y": 2250.0,
            "Z": 15.0,
            "E_Rel": 210.08452,
            "Layer": 0,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 24.999999419126436,
            "Flow": 131249.9969504138,
            "RPM": 78.74999817024828,
            "Voltage": 1.5749999634049656,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 737.5,
            "Y": 2250.0,
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
        },
        {
            "Move": "G0",
            "X": 737.5,
            "Y": 2250.0,
            "Z": 30.0,
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
        },
        {
            "Move": "G0",
            "X": 737.5,
            "Y": 2267.54,
            "Z": 30.0,
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
        },
        {
            "Move": "G0",
            "X": 462.5,
            "Y": 2267.54,
            "Z": 30.0,
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
        },
        {
            "Move": "G0",
            "X": 462.5,
            "Y": 2250.0,
            "Z": 30.0,
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
        },
        {
            "Move": "G1",
            "X": 462.5,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": 100.0,
            "Layer": 1,
            "Type": "protract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 537.5,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": 57.29578,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 25.000000212457916,
            "Flow": 131250.00111540404,
            "RPM": 78.75000066924243,
            "Voltage": 1.5750000133848487,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 537.5,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": -100.0,
            "Layer": 1,
            "Type": "retract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 555.04,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 644.96,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 662.5,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 662.5,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": 100.0,
            "Layer": 1,
            "Type": "protract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 737.5,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": 57.29578,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 25.000000212457916,
            "Flow": 131250.00111540404,
            "RPM": 78.75000066924243,
            "Voltage": 1.5750000133848487,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 737.5,
            "Y": 2250.0,
            "Z": 30.0,
            "E_Rel": -100.0,
            "Layer": 1,
            "Type": "retract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 737.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 737.5,
            "Y": 2267.54,
            "Z": 45.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 462.5,
            "Y": 2267.54,
            "Z": 45.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 462.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 0,
            "Layer": 1,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 462.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 100.0,
            "Layer": 2,
            "Type": "protract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 537.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 57.29578,
            "Layer": 2,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 25.000000212457916,
            "Flow": 131250.00111540404,
            "RPM": 78.75000066924243,
            "Voltage": 1.5750000133848487,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 537.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": -100.0,
            "Layer": 2,
            "Type": "retract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 555.04,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 0,
            "Layer": 2,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 644.96,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 0,
            "Layer": 2,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 662.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 0,
            "Layer": 2,
            "Type": "travel",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 662.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 100.0,
            "Layer": 2,
            "Type": "protract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 737.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": 57.29578,
            "Layer": 2,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 25.000000212457916,
            "Flow": 131250.00111540404,
            "RPM": 78.75000066924243,
            "Voltage": 1.5750000133848487,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G1",
            "X": 737.5,
            "Y": 2250.0,
            "Z": 45.0,
            "E_Rel": -100.0,
            "Layer": 2,
            "Type": "retract",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
        {
            "Move": "G0",
            "X": 0.0,
            "Y": 0.0,
            "Z": 0.0,
            "E_Rel": 0,
            "Layer": 2,
            "Type": "travel",
            "Layer_Height": 0,
            "Reachable": False,
            "Linewidth": 0,
            "Flow": 0.0,
            "RPM": 0.0,
            "Voltage": 0.0,
            "Vel_CP_Max": 0.35,
        },
    ]

    processed_p = process_points(p)

    numbered_points = assign_count_info(processed_p)

    info_points = assign_extrusion_info(numbered_points)

    for entries in p:
        print(entries)

    print(f"processed_points\n")
    for entries in processed_p:
        print(entries)

    print(f"numbered_points\n")
    for entries in numbered_points:
        print(entries)

    print(f"info_points\n")
    for entries in info_points:
        print(entries)
