from matplotlib.colors import to_rgb
import rhinoinside

# Load Rhino.Inside
rhinoinside.load()

import Rhino.Geometry as rg
import Rhino.DocObjects as rdo
import Rhino.FileIO as rfi
from System.Drawing import Color
from System.Collections.Generic import List as NetList


def color_name_to_rgb(color_name):
    """
    Converts a HEX color name to an RGB tuple (0-255).
    """
    if color_name.startswith("#") and len(color_name) in {7, 9}:  # #RRGGBB or #RRGGBBAA
        return tuple(int(c * 255) for c in to_rgb(color_name))
    else:
        print(f"Invalid HEX color: {color_name}. Defaulting to black.")
        return (0, 0, 0)


def create_geometry(points_list, filepath, type_values, line_widths):
    """
    Creates geometry in a Rhino file: polylines and colored points.
    """
    # Load the existing Rhino file
    rhino_file = rfi.File3dm.Read(str(filepath))
    if rhino_file is None:
        print(f"Error: Could not open the Rhino file at {filepath}.")
        return False

    print("Creating polylines...")
    create_polylines(points_list, rhino_file, type_values, line_widths)

    print("Creating points...")
    create_points(points_list, rhino_file, include_all_points=False)

    # Save the updated file
    rhino_file.Write(str(filepath), 8)
    print(f"Updated Rhino file saved to {filepath}.")
    return True


def create_polylines(points_list, rhino_file, type_values, line_widths):
    """
    Erstellt Polylinien in der Rhino-Datei und setzt Attribute basierend auf `type_values` und `line_widths`.

    :param points_list: Liste von Punkten mit Attributen (X, Y, Z, Type, Move, etc.).
    :param rhino_file: Die Rhino-Datei, in der die Polylinien gespeichert werden.
    :param type_values: Dictionary mit Darstellungsoptionen für jeden Typ.
    :param line_widths: Dictionary mit Plot-Weights für verschiedene Linientypen.
    """
    grouped_polylines = {}

    # Gruppiere Punkte nach Layer und Linie
    for point_data in points_list:
        layer_id = f"{point_data['Layer']:04d}"
        line_id = f"{point_data['Line']:04d}"
        point = rg.Point3d(point_data["X"], point_data["Y"], point_data["Z"])
        move_command = point_data["Move"]
        point_info = point_data["Point_Info"]
        line_type = str(point_data["Type"])  # Sicherstellen, dass es ein String ist

        polyline_key = (layer_id, line_id)

        if polyline_key not in grouped_polylines:
            grouped_polylines[polyline_key] = {
                "points": [],
                "type": line_type,
                "move": move_command,
                "point_info": point_info,
            }

        grouped_polylines[polyline_key]["points"].append(point)

    for (layer_id, line_id), polyline_data in grouped_polylines.items():
        points = polyline_data["points"]
        line_type = polyline_data["type"]
        extrusion_value = polyline_data["point_info"]

        if len(points) < 2:
            print(f"Skipping polyline {layer_id}/{line_id}, not enough points.")
            continue

        # Erzeuge Rhino-Polyline
        rhino_points = NetList[rg.Point3d]()
        for point in points:
            rhino_points.Add(point)

        polyline_curve = rg.PolylineCurve(rhino_points)

        # Layer-Index abrufen
        layer_index = next(
            (l.Index for l in rhino_file.Layers if l.Name == layer_id), None
        )

        if layer_index is None:
            print(
                f"Error: Layer '{layer_id}' not found. Skipping polyline {layer_id}/{line_id}."
            )
            continue

        # Rhino-Objektattribute setzen
        attributes = rdo.ObjectAttributes()
        attributes.LayerIndex = layer_index
        attributes.Name = f"{layer_id}/{line_id}"
        attributes.SetUserString("Layer", layer_id)
        attributes.SetUserString("Line", line_id)
        attributes.SetUserString("Type", line_type)
        attributes.SetUserString("Extrusion", "1" if extrusion_value != "0" else "0")

        # Extraktion der Attribute aus `type_values`
        line_type_info = type_values.get(line_type, {})
        color_hex = line_type_info.get("color", "#FFFFFF")
        linetype_name = line_type_info.get("linetype", "Continuous")

        # Farbe setzen
        color_rgb = Color.FromArgb(*color_name_to_rgb(color_hex))
        attributes.ObjectColor = color_rgb
        attributes.ColorSource = rdo.ObjectColorSource.ColorFromObject
        attributes.PlotColorSource = rdo.ObjectPlotColorSource.PlotColorFromObject
        attributes.PlotColor = attributes.ObjectColor

        # Setze die Linienbreite basierend auf `line_widths`
        plot_weight = line_widths.get("value", {}).get(linetype_name.lower(), 0.5)
        attributes.PlotWeightSource = rdo.ObjectPlotWeightSource.PlotWeightFromObject
        attributes.PlotWeight = float(plot_weight)

        # Linientyp setzen
        linetype_index = next(
            (
                lt.Index
                for lt in rhino_file.AllLinetypes
                if lt.Name.lower() == linetype_name.lower()
            ),
            None,
        )

        if linetype_index is not None:
            attributes.LinetypeSource = rdo.ObjectLinetypeSource.LinetypeFromObject
            attributes.LinetypeIndex = linetype_index
        else:
            print(f"Linetype '{linetype_name}' not found. Using default 'continuous'.")

        # Polylinie zu Rhino-Datei hinzufügen
        rhino_file.Objects.AddCurve(polyline_curve, attributes)
        print(
            f"Polyline {layer_id}/{line_id} created "
            f"(Type: {line_type}, Color: {color_hex}, Linetype: {linetype_name}, "
            f"PlotWeight: {attributes.PlotWeight}mm)."
        )


def create_points(points_list, rhino_file, include_all_points=False):
    """
    Internal function to create points in the Rhino file.
    """
    for point_data in points_list:
        # Skip points that are not "start" or "stop" if only start/stop points are to be included
        if not include_all_points and point_data["Point_Info"] not in {
            "start",
            "stop",
            "retract",
            "protract",
        }:
            continue

        # Extract values from point_data
        layer = f"{point_data['Layer']:04d}"
        line_num = f"{point_data['Line']:04d}"
        point_num = f"{point_data['Point']:04d}"
        point_info = point_data["Point_Info"]
        x, y, z = point_data["X"], point_data["Y"], point_data["Z"]

        # Create the point object
        point = rg.Point3d(x, y, z)

        # Assign color based on point_info
        color_mapping = {
            "start": Color.FromArgb(0, 255, 0),  # Green for Start
            "stop": Color.FromArgb(255, 0, 0),  # Red for Stop
            "retract": Color.FromArgb(0, 0, 255),  # Blue for Retract
            "protract": Color.FromArgb(173, 216, 230),  # Light Blue for Protract
            "1": Color.FromArgb(128, 128, 128),  # Gray for Extrusion
            "0": Color.FromArgb(0, 0, 0),  # Black for Travel
        }
        color = color_mapping.get(point_info, Color.FromArgb(0, 0, 0))

        # Assign attributes
        attributes = rdo.ObjectAttributes()
        attributes.LayerIndex = next(
            (l.Index for l in rhino_file.Layers if l.Name == layer),
            None,
        )
        attributes.ObjectColor = color
        attributes.ColorSource = rdo.ObjectColorSource.ColorFromObject
        attributes.PlotColorSource = rdo.ObjectPlotColorSource.PlotColorFromObject
        attributes.PlotColor = attributes.ObjectColor
        attributes.Name = f"{layer}/{line_num}/{point_num}"
        attributes.SetUserString("Layer", layer)
        attributes.SetUserString("Line", line_num)
        attributes.SetUserString("Point", point_num)
        attributes.SetUserString("Point_Info", point_info)

        # Add the point to the Rhino file
        rhino_file.Objects.AddPoint(point, attributes)
        print(f"Added point {attributes.Name} at {point} with color {color}.")
