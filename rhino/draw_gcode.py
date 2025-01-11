from matplotlib.colors import to_rgb
import Rhino.Geometry as rg
import Rhino.DocObjects as rdo
import Rhino.FileIO as rfi
from System.Drawing import Color
from System.Collections.Generic import List as NetList


def color_name_to_rgb(color_name):
    """
    Converts a HEX color name to an RGB tuple (0-255).
    :param color_name: The name or HEX value of the color.
    :return: RGB tuple.
    """
    if color_name.startswith("#") and len(color_name) in {7, 9}:  # #RRGGBB or #RRGGBBAA
        return tuple(int(c * 255) for c in to_rgb(color_name))
    else:
        print(f"Invalid HEX color: {color_name}. Defaulting to black.")
        return (0, 0, 0)


def create_geometry(points_list, filepath, line_width, type_values):
    """
    Creates geometry in a Rhino file: polylines and colored points.
    :param points_list: List of points with attributes (Layer, poly_num, Type, Move, etc.).
    :param filepath: Path to the existing Rhino file.
    :param line_width: Line width for printing in mm.
    """
    # Load the existing Rhino file
    rhino_file = rfi.File3dm.Read(str(filepath))
    if rhino_file is None:
        print(f"Error: Could not open the Rhino file at {filepath}.")
        return False

    print("Creating polylines...")
    _create_polylines(points_list, rhino_file, line_width, type_values)

    print("Creating points...")
    _create_points(points_list, rhino_file, include_all_points=False)

    # Save the updated file
    rhino_file.Write(str(filepath), 8)
    print(f"Updated Rhino file saved to {filepath}.")
    return True


def _create_polylines(points_list, rhino_file, line_width, type_values):
    """
    Internal function to create polylines in the Rhino file.
    """
    polylines = {}

    for point_data in points_list:
        # Extract values from point_data
        layer = f"{point_data['Layer']:04d}"
        poly_num = f"{point_data['poly_num']:04d}"
        point = rg.Point3d(point_data["X"], point_data["Y"], point_data["Z"])
        type = point_data["Type"]
        move_command = point_data["Move"]

        # Use (Layer, poly_num) as the key for grouping
        key = (layer, poly_num)
        if key not in polylines:
            polylines[key] = {
                "points": [],
                "type": type,
                "move": move_command,
            }

        polylines[key]["points"].append(point)

    # Create and add polylines to the Rhino file
    for (layer, poly_num), data in polylines.items():
        points = data["points"]
        type = data["type"]
        move_command = data["move"]

        # Determine extrusion value based on move_command
        extrusion = "1" if move_command == "G1" else "0"

        if len(points) < 2:
            print(f"Skipping polyline {layer}/{poly_num} due to insufficient points.")
            continue

        # Create the polyline
        net_points = NetList[rg.Point3d]()
        for point in points:
            net_points.Add(point)

        polyline_curve = rg.PolylineCurve(net_points)

        # Determine the sublayer name and layer index
        sublayer_name = layer
        layer_index = next(
            (l.Index for l in rhino_file.Layers if l.Name == sublayer_name), None
        )

        if layer_index is None:
            print(
                f"ERROR: Layer '{sublayer_name}' not found for polyline {layer}/{poly_num}."
            )
            continue

        # Assign attributes
        attributes = rdo.ObjectAttributes()
        attributes.LayerIndex = layer_index
        attributes.Name = f"{sublayer_name}/{poly_num}"
        attributes.SetUserString("Layer", sublayer_name)
        attributes.SetUserString("Line", poly_num)
        attributes.SetUserString("type", type)
        attributes.SetUserString("extrusion", extrusion)

        # Assign color based on type_values
        line_type_color = type_values.get(type, {}).get("Color", "black")
        color = Color.FromArgb(*color_name_to_rgb(line_type_color))
        attributes.ObjectColor = color
        attributes.ColorSource = rdo.ObjectColorSource.ColorFromObject

        # Set plot color to match the object color
        attributes.PlotColorSource = rdo.ObjectPlotColorSource.PlotColorFromObject
        attributes.PlotColor = attributes.ObjectColor

        # Set line width (except for Travel)
        if type != "TRAVEL":
            attributes.PlotWeightSource = (
                rdo.ObjectPlotWeightSource.PlotWeightFromObject
            )
            attributes.PlotWeight = float(line_width)  # Line width in mm

        # Assign linetype based on type_values
        linetype_name = type_values.get(type, {}).get("Linetype", "Continuous")
        linetype_index = next(
            (lt.Index for lt in rhino_file.AllLinetypes if lt.Name == linetype_name),
            None,
        )

        if linetype_index is not None:
            attributes.LinetypeSource = rdo.ObjectLinetypeSource.LinetypeFromObject
            attributes.LinetypeIndex = linetype_index
        else:
            print(f"Linetype '{linetype_name}' not found. Using default 'Continuous'.")

        # print(
        #     f"Polyline '{attributes.Name}': Type '{type}', Extrusion {extrusion}, "
        #     f"Color {line_type_color}, Linetype '{linetype_name}'"
        # )

        # Add the polyline to the Rhino file
        rhino_file.Objects.AddCurve(polyline_curve, attributes)
        # print(f"Added polyline {attributes.Name} to Layer '{sublayer_name}'.")


def _create_points(points_list, rhino_file, include_all_points=True):
    """
    Internal function to create points in the Rhino file.
    """
    for point_data in points_list:
        # Skip points that are not "start" or "stop" if only start/stop points are to be included
        if not include_all_points and point_data["point_info"] not in {"start", "stop"}:
            continue

        # Extract values from point_data
        layer = f"{point_data['Layer']:04d}"
        poly_num = f"{point_data['poly_num']:04d}"
        point_num = f"{point_data['point_num']:04d}"
        point_info = point_data["point_info"]
        x, y, z = point_data["X"], point_data["Y"], point_data["Z"]

        # Create the point object
        point = rg.Point3d(x, y, z)

        # Assign color based on point_info
        color = {
            "start": Color.FromArgb(0, 255, 0),  # Neon Green for Start
            "stop": Color.FromArgb(255, 0, 0),  # Neon Red for Stop
            "1": Color.FromArgb(128, 128, 128),  # Darker Gray for Extrusion
        }.get(
            point_info, Color.FromArgb(0, 0, 0)
        )  # Default to Black

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
        attributes.Name = f"{layer}/{poly_num}/{point_num}"
        attributes.SetUserString("Layer", layer)
        attributes.SetUserString("Line", poly_num)
        attributes.SetUserString("Point", point_num)
        attributes.SetUserString("extrusion", point_info)

        # Add the point to the Rhino file
        rhino_file.Objects.AddPoint(point, attributes)
        print(f"Added point {attributes.Name} at {point} with color {color}.")
