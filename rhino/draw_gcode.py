from matplotlib import colors
import Rhino.Geometry as rg
import Rhino.DocObjects as rdo
import Rhino.FileIO as rfi
from System.Drawing import Color
from System.Collections.Generic import List as NetList
from gcode.slicer_keywordmanager import get_type_values

type_values = get_type_values()


def color_name_to_rgb(color_name):
    """
    Converts a color name (e.g., 'red') to an RGB tuple (0-255).
    :param color_name: The name of the color.
    :return: RGB tuple.
    """
    try:
        rgb_normalized = colors.to_rgb(color_name)
        return tuple(int(c * 255) for c in rgb_normalized)
    except ValueError:
        print(f"Invalid color name: {color_name}. Defaulting to black.")
        return (0, 0, 0)  # Default to black if invalid


def create_geometry(points_list, filepath, line_width):
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
    _create_polylines(points_list, rhino_file, line_width)

    print("Creating points...")
    _create_points(points_list, rhino_file, include_all_points=False)

    # Save the updated file
    rhino_file.Write(str(filepath), 8)
    print(f"Updated Rhino file saved to {filepath}.")
    return True


def _create_polylines(points_list, rhino_file, line_width):
    """
    Internal function to create polylines in the Rhino file.
    """
    polylines = {}

    for point_data in points_list:
        layer = point_data["Layer"]
        poly_num = point_data["poly_num"]
        point = rg.Point3d(point_data["X"], point_data["Y"], point_data["Z"])
        type = point_data["Type"]
        move_command = point_data["Move"]

        # Use (Layer, poly_num) as the key for grouping
        key = (layer, poly_num)
        if key not in polylines:
            polylines[key] = {"points": [], "type": type, "move": move_command}

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
        attributes = rdo.ObjectAttributes()

        # Determine the sublayer name
        sublayer_name = f"{layer:04d}"  # Format layer as 4-digit number
        layer_index = next(
            (l.Index for l in rhino_file.Layers if l.Name == sublayer_name), None
        )

        if layer_index is None:
            print(
                f"ERROR: Layer '{sublayer_name}' not found for polyline {layer}/{poly_num}."
            )
            continue

        # Assign attributes
        polyline_name = f"{sublayer_name}/{poly_num:04d}"  # Name as "0001/0012"
        attributes.LayerIndex = layer_index
        attributes.Name = polyline_name
        attributes.SetUserString("name", polyline_name)
        attributes.SetUserString("type", type)
        attributes.SetUserString("extrusion", extrusion)  # Save extrusion value

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

        print(
            f"Polyline {polyline_name}: Type '{type}', Extrusion {extrusion}, "
            f"Color {line_type_color}"
        )

        # Add the polyline to the Rhino file
        rhino_file.Objects.AddCurve(polyline_curve, attributes)
        print(f"Added polyline {polyline_name} to Layer '{sublayer_name}'.")


def _create_points(points_list, rhino_file, include_all_points=True):
    """
    Internal function to create points in the Rhino file.
    :param points_list: List of points with attributes to process.
    :param rhino_file: The Rhino file where points will be added.
    :param include_all_points: If True, adds all points. If False, adds only start and stop points of extrusion moves.
    """
    for point_data in points_list:
        # Skip points that are not "start" or "stop" if only start/stop points are to be included
        if not include_all_points and point_data["point_info"] not in {"start", "stop"}:
            continue

        # Extract point data
        point = rg.Point3d(point_data["X"], point_data["Y"], point_data["Z"])
        layer = point_data["Layer"]
        poly_num = point_data["poly_num"]
        point_num = point_data["point_num"]
        point_info = point_data["point_info"]

        # Determine the color based on point_info
        if point_info == "start":
            color = Color.FromArgb(0, 255, 0)  # Neon Green for Start
        elif point_info == "stop":
            color = Color.FromArgb(255, 0, 0)  # Neon Red for Stop
        elif point_info == "1":
            color = Color.FromArgb(128, 128, 128)  # Darker Gray for Extrusion
        else:
            color = Color.FromArgb(0, 0, 0)  # Black for everything else

        # Assign name to the point
        point_name = f"{layer:04d}/{poly_num:04d}/{point_num:04d}"

        # Add the point to the Rhino file
        attributes = rdo.ObjectAttributes()
        attributes.LayerIndex = next(
            (l.Index for l in rhino_file.Layers if l.Name == f"{layer:04d}"), None
        )
        attributes.ObjectColor = color
        attributes.ColorSource = rdo.ObjectColorSource.ColorFromObject
        attributes.PlotColorSource = rdo.ObjectPlotColorSource.PlotColorFromObject
        attributes.PlotColor = attributes.ObjectColor
        attributes.Name = point_name
        attributes.SetUserString("name", point_name)
        attributes.SetUserString("extrusion", point_info)

        rhino_file.Objects.AddPoint(point, attributes)
        print(f"Added point {point_name} at {point} with color {color}.")


# def get_linetype_index(rhino_file, linetype_name):
#     for linetype in rhino_file.Linetypes:
#         if linetype.Name == linetype_name:
#             return linetype.Index
#     print(f"Linetype '{linetype_name}' not found. Using default 'Continuous'.")
#     return 0  # Default linetype index for "Continuous"
#
#
# # inside create_polyline
# # Assign linetype based on type_values
# linetype_name = type_values.get(type, {}).get("Linetype", "Continuous")
# linetype_index = get_linetype_index(rhino_file, linetype_name)
#
# # Ensure linetype is taken from object and assign index
# attributes.LinetypeSource = rdo.ObjectLinetypeSource.LinetypeFromObject
# attributes.LinetypeIndex = linetype_index
