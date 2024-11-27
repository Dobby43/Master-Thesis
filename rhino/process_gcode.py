def process_points(data: list[dict]) -> list[dict]:

    print("Processing G-Code points...")

    # Übergangspunkte einfügen
    processed_points = []
    current_layer = None
    current_type = None

    for i, entry in enumerate(data):
        layer = entry["Layer"]
        move_type = entry["Type"]
        x, y, z = entry["X"], entry["Y"], entry["Z"]

        if current_layer != layer or current_type != move_type:
            if processed_points:
                # Füge den letzten Punkt erneut ein, um den Übergang zu markieren
                last_point = processed_points[-1]
                transition_point = {
                    "X": last_point["X"],
                    "Y": last_point["Y"],
                    "Z": last_point["Z"],
                    "Layer": layer,  # neuer Layer
                    "Type": move_type,  # neuer Typ
                }
                processed_points.append(transition_point)
                print(
                    f"Added transition point for Layer={layer}, Type={move_type} at {transition_point['X']}, {transition_point['Y']}, {transition_point['Z']}"
                )

            current_layer = layer
            current_type = move_type

        processed_points.append(
            {"X": x, "Y": y, "Z": z, "Layer": layer, "Type": move_type}
        )

    # Nummerierung
    numbered_points = []
    current_layer = None
    current_type = None
    poly_num = 0  # Polyline-Nummer, wird bei neuem Layer zurückgesetzt
    point_num = 0  # Punktnummer innerhalb der aktuellen Polyline

    for i, entry in enumerate(processed_points):
        layer = entry["Layer"]
        move_type = entry["Type"]

        # Wenn sich der Layer ändert, setze die Polyline-Nummer zurück
        if current_layer != layer:
            poly_num = 0  # Bei neuem Layer zurücksetzen
            current_layer = layer
            current_type = None  # Typ ebenfalls zurücksetzen

        # Wenn sich der Typ ändert, starte eine neue Polyline
        if current_type != move_type:
            if current_type is not None:  # Nicht beim ersten Punkt
                poly_num += 1  # Neue Polyline für Typwechsel
            current_type = move_type
            point_num = 0  # Punktzähler zurücksetzen

        # Punkt mit Nummerierung versehen
        numbered_point = entry.copy()
        numbered_point["poly_num"] = poly_num
        numbered_point["point_num"] = point_num

        reordered_point = {
            key: numbered_point[key]
            for key in ["X", "Y", "Z", "Layer", "poly_num", "point_num", "Type"]
        }
        numbered_points.append(reordered_point)

        # Punktzähler für aktuelle Polyline hochzählen
        point_num += 1

    print(f"Processed {len(numbered_points)} points.")
    return numbered_points
