def add_point_info(points: list[dict]) -> list[dict]:

    points_processed = process_points(points)

    points_counted = assign_count_info(points_processed)

    points_info = assign_extrusion_info(points_counted)

    return points_info


def process_points(data: list[dict]) -> list[dict]:
    """
    Processes points, inserts transition points based on type changes, assigns numbering, and determines point roles.
    Transition points copy coordinates and other values from the previous point,
    but 'Move', 'Layer', 'Layer_Height', and 'Type' are updated based on the current point.
    """
    processed_points = []
    previous_point = None  # Keeps track of the previous point for comparison

    for i, current_point in enumerate(data):
        current_type = current_point["Type"]
        current_move = current_point["Move"]

        # Übergangspunkte nur einfügen, wenn sich der Typ ändert (außer in definierten Ausnahmen)
        if previous_point:
            previous_type = previous_point["Type"]

            # Definierte Ausnahmen, bei denen KEIN Übergangspunkt eingefügt wird
            no_transition_cases = {
                ("travel", "retract"),
                ("retract", "travel"),
                ("travel", "protract"),
                ("protract", "travel"),
            }

            # Falls der Typ sich nicht ändert, KEIN Übergangspunkt einfügen
            if previous_type == current_type:
                processed_points.append(current_point)
                previous_point = current_point
                continue

            # Falls Wechsel in einer der definierten Ausnahmen, KEIN Übergangspunkt einfügen
            if (previous_type, current_type) in no_transition_cases:
                processed_points.append(current_point)
                previous_point = current_point
                continue

            # Falls ein gültiger Typ-Wechsel stattfindet, Übergangspunkt hinzufügen
            transition_point = {
                "Move": current_move,  # Move vom aktuellen Punkt übernehmen
                "X": previous_point["X"],  # Koordinaten vom vorherigen Punkt übernehmen
                "Y": previous_point["Y"],
                "Z": previous_point["Z"],
                "E_rel": 0,  # Immer 0 setzen für den Übergangspunkt
                "Layer": current_point["Layer"],  # Layer vom aktuellen Punkt übernehmen
                "Type": current_type,  # Typ vom aktuellen Punkt übernehmen
                "Layer_Height": current_point[
                    "Layer_Height"
                ],  # Layerhöhe vom aktuellen Punkt übernehmen
                "Reachable": previous_point["Reachable"],
            }
            processed_points.append(transition_point)

        # Aktuellen Punkt hinzufügen
        processed_points.append(current_point)
        previous_point = (
            current_point  # Vorherigen Punkt für nächste Iteration aktualisieren
        )

    # Nummerierung und Rollen zuweisen
    return processed_points


def assign_count_info(processed_points: list[dict]) -> list[dict]:
    """
    Assigns 'Line' and 'Point' numbers based on type changes and layer transitions.
    Regeln:
    - Line zählt durchgehend hoch.
    - Point zählt innerhalb einer Line hoch.
    - Travel, Retract, Protract werden als derselbe Typ behandelt.
    - Bei Layerwechsel werden Line und Point auf 0 gesetzt.
    - Bei Typwechsel (außer Travel/Protract/Retract) wird Line +1 gesetzt und Point auf 0 zurückgesetzt.

    """

    counted_points = []
    previous_layer = 0
    previous_type = None
    line_counter = -1
    point_counter = 0

    # Typen, die als eine Einheit behandelt werden
    ignored_type_transitions = {"travel", "retract", "protract"}

    for entry in processed_points:
        current_layer = entry["Layer"]
        current_type = entry["Type"]

        # Falls Layer wechselt, alles auf 0 zurücksetzen
        if previous_layer != current_layer:
            line_counter = -1
            point_counter = 0
            previous_layer = current_layer
            previous_type = None

        # Prüfe, ob aktueller oder vorheriger Typ ignoriert werden soll
        is_current_ignored = current_type in ignored_type_transitions
        is_previous_ignored = (
            previous_type in ignored_type_transitions if previous_type else False
        )

        # Wenn der Typ wechselt
        if previous_type != current_type:
            if is_previous_ignored and not is_current_ignored:
                # Wechsel von travel/retract/protract → echter Typ (z.B. wall_outer)
                line_counter += 1
                point_counter = 0
            elif not is_previous_ignored and is_current_ignored:
                # Wechsel von echtem Typ → travel/retract/protract
                line_counter += 1
                point_counter = 0
            elif not is_previous_ignored and not is_current_ignored:
                # Wechsel zwischen zwei echten Typen (z.B. wall_outer → infill)
                line_counter += 1
                point_counter = 0

        # Werte zuweisen
        counted_point = entry.copy()
        counted_point["Line"] = line_counter
        counted_point["Point"] = point_counter
        counted_points.append(counted_point)

        # Point-Counter erhöhen
        point_counter += 1
        previous_type = current_type

    return counted_points


def assign_extrusion_info(counted_points: list[dict]) -> list[dict]:
    """
    Assigns 'Point_Info' based on movement type and position within a line.

    Regeln:
    - Travel → Point_Info = "0"
    - Protract → Point_Info = "1" (immer!)
    - Retract → Point_Info = "retract"
    - Falls Point == 0 → "start"
    - Falls letzter Punkt in der Linie oder Typwechsel → "stop" (außer bei Protract)
    - Sonst:
      - Move == G1 → "1"
      - Move == G0 → "0"
    """

    ignored_type_transitions = {"travel", "retract", "protract"}

    # Iteration mit zip() + enumerate(), um gleichzeitig auf den aktuellen und nächsten Punkt zuzugreifen
    for current_entry, next_entry in zip(counted_points, counted_points[1:] + [None]):
        move = current_entry["Move"]
        type = current_entry["Type"]
        point = current_entry["Point"]

        # Standardwerte für Point_Info setzen
        if type == "travel":
            point_info = "0"
        elif type == "protract":
            point_info = "protract"
        elif type == "retract":
            point_info = "retract"
        elif point == 0:
            point_info = "start"
        elif (
            next_entry is not None  # Stelle sicher, dass es einen nächsten Punkt gibt!
            and type
            not in ignored_type_transitions  # Kein travel, retract oder protract
            and next_entry["Type"] != type  # Typwechsel liegt vor
        ):
            point_info = "stop"

        else:
            point_info = "1" if move == "G1" else "0"

        # Point_Info speichern
        current_entry["Point_Info"] = point_info

    return counted_points


if __name__ == "__main__":

    points = [
        {
            "Move": "G0",
            "X": 512.5,
            "Y": 2250.0,
            "Z": 15.0,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 512.5,
            "Y": 2250.0,
            "Z": 15.0,
            "E_rel": 0,
            "Layer": 0,
            "Type": "retract",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G0",
            "X": 512.5,
            "Y": 2250.0,
            "Z": 15.0,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 512.5,
            "Y": 2250.0,
            "Z": 15.0,
            "E_rel": 0,
            "Layer": 1,
            "Type": "protract",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 687.5,
            "Y": 2250.0,
            "Z": 15.0,
            "E_Rel": 10287.023,
            "Layer": 1,
            "Type": "wall_outer",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 667.5,
            "Y": 2250.0,
            "Z": 15.0,
            "E_Rel": 10287.023,
            "Layer": 1,
            "Type": "wall_inner",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 667.5,
            "Y": 2230.0,
            "Z": 15.0,
            "E_Rel": 10287.023,
            "Layer": 1,
            "Type": "wall_inner",
            "Layer_Height": 15.0,
        },
    ]

    processed_points = process_points(points)

    numbered_points = assign_count_info(processed_points)

    info_points = assign_extrusion_info(numbered_points)

    for entry in points:
        print(entry)

    print(f"processed_points\n")
    for entry in processed_points:
        print(entry)

    print(f"numbered_points\n")
    for entry in numbered_points:
        print(entry)

    print(f"info_points\n")
    for entry in info_points:
        print(entry)
