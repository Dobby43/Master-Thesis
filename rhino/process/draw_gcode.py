from pathlib import Path
from matplotlib.colors import to_rgb

import rhinoinside

# Load Rhino.Inside
rhinoinside.load()

import Rhino.Geometry as Rg
import Rhino.DocObjects as Rdo
import Rhino.FileIO as Rfi

import System as Sys
from System.Drawing import Color


def color_name_to_rgb(color_name: str) -> tuple:
    """
    DESCRIPTION:
    Converts a HEX color name to an RGB tuple (0-255).

    :param color_name: HEX color name
    return: (R, G, B) tuple
    """
    if color_name.startswith("#") and len(color_name) in {7, 9}:  # #RRGGBB or #RRGGBBAA
        return tuple(int(c * 255) for c in to_rgb(color_name))
    else:
        print(f"Invalid HEX color: {color_name}. Defaulting to black.")
        return 0, 0, 0


def create_geometry(
    points: list[dict],
    filepath: Path,
    linetype_dict: dict[str, str],
    line_color_dict: dict[str, str],
    line_widths: dict[str, float],
    point_color: dict[str, str],
    point_print: bool,
    precision: int,
):
    """
    DESCRIPTION:
    Creates geometry in a Rhino file: polylines and colored points.

    :param points: List of points.
    :param filepath: Path to the Rhino file.
    :param linetype_dict: Dictionary of line types from setup.Rhino.line_style_line.json
    :param line_color_dict: Dictionary of color names from setup.Rhino.line_types_color.json
    :param line_widths: Dictionary of line widths from setup.Rhino.line_width.json
    :param point_color: Dictionary of color names from setup.Rhino.point_color.json
    :param point_print: Bool if all points in should be visible in the Rhino file (if False only start, stop, retract, protract, end, beginning ar visible)
    :param precision: Precision of values displayed in Attribute User Text Strings.

    :return: bool if file was written successfully
    """
    # Load the existing Rhino file
    rhino_file = Rfi.File3dm.Read(str(filepath))
    if rhino_file is None:
        print(f"Error: Could not open the Rhino file at {filepath}.")
        return False

    print("[INFO] Creating lines...")
    create_lines(
        points, rhino_file, linetype_dict, line_color_dict, line_widths, precision
    )

    print("[INFO] Creating points...")
    create_points(points, rhino_file, point_color, point_print)

    # Save the updated file
    rhino_file.Write(str(filepath), 8)
    print(f"[INFO] Updated Rhino file saved to {filepath}.")
    return True


def get_layer_index(rhino_file: Rfi.File3dm, layer_id: str, line_id: str) -> int | None:
    """
    DESCRIPTION:
    Finds the layer index for a line with the name line_id inside layer_id in parent layer toolpath

    param rhino_file: Rhino file
    param layer_id: Layer ID
    param line_id: Line ID
    """
    # 1. Get 'toolpath'
    toolpath_layer = next(
        (
            l
            for l in rhino_file.Layers
            if l.Name == "toolpath" and l.ParentLayerId == Sys.Guid.Empty
        ),
        None,
    )
    if not toolpath_layer:
        print("[ERROR] 'toolpath'-Layer nicht gefunden.")
        return None

    # 2. Get Layer e.g. '0003'
    layer_obj = next(
        (
            l
            for l in rhino_file.Layers
            if l.Name == layer_id and l.ParentLayerId == toolpath_layer.Id
        ),
        None,
    )
    if not layer_obj:
        print(f"[ERROR] Layer '{layer_id}' unter 'toolpath' nicht gefunden.")
        return None

    # 3. Get Line-Layer e.g. '0127'
    line_layer = next(
        (
            l
            for l in rhino_file.Layers
            if l.Name == line_id and l.ParentLayerId == layer_obj.Id
        ),
        None,
    )
    if not line_layer:
        print(f"[ERROR] Line '{line_id}' unter '{layer_id}' nicht gefunden.")
        return None

    return line_layer.Index


def create_lines(
    points: list[dict],
    rhino_file: Rfi.File3dm,
    linetype_dict: dict[str, str],
    line_color_dict: dict[str, str],
    line_widths: dict[str, float],
    precision: int,
) -> None:
    """
    DESCRIPTION:
    Creates line segments from pairs of points. For some type changes a travel line is created

    :param rhino_file: Rhino file
    :param points: List of points.
    :param linetype_dict: Dictionary of line types from setup.Rhino.line_types_line.json
    :param line_color_dict: Dictionary of color names from setup.Rhino.line_types_color.json
    :param line_widths: Dictionary of line widths from setup.Rhino.line_width.json
    :param precision: Precision of values displayed in Attribute User Text Strings.
    """

    # no new line created if type transitions within blocked
    blocked = {
        ("travel", "retract"),
        ("retract", "travel"),
        ("travel", "protract"),
        ("protract", "travel"),
        ("retract", "protract"),
        ("protract", "retract"),
    }

    prev_layer = None
    prev_line = None
    segment_index = 0

    # iterate over points till second to last
    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]

        if p0["Layer"] != p1["Layer"] or p0["Line"] != p1["Line"]:
            continue

        # Segment Id consisting of Layer/Line/Segment (Example: Segment 0001/0002/0123)
        layer_id = f"{p1['Layer']:04d}"
        line_id = f"{p1['Line']:04d}"

        # Reset Segment Id counter
        if layer_id != prev_layer or line_id != prev_line:
            segment_index = 0

        segment_id = f"{segment_index:04d}"
        segment_index += 1

        prev_layer = layer_id
        prev_line = line_id

        # Check for change in Type
        # Plot retract and protract as travel
        type_pair = (p0["Type"], p1["Type"])
        if type_pair in blocked:
            visual_type = "travel"
            forced_type = "travel"
        else:
            visual_type = (
                "travel" if p1["Type"] in {"retract", "protract"} else p1["Type"]
            )
            forced_type = p1["Type"]

        # Geometrie
        start = Rg.Point3d(p0["X"], p0["Y"], p0["Z"])
        end = Rg.Point3d(p1["X"], p1["Y"], p1["Z"])
        line = Rg.Line(start, end)

        # Get layer to save line segment to
        layer_id = f"{p1['Layer']:04d}"
        line_id = f"{p1['Line']:04d}"
        layer_index = get_layer_index(rhino_file, layer_id, line_id)
        if layer_index is None:
            print(f"[WARNING] Layer {layer_id}/{line_id}  not found; Skipping line")
            continue

        # Object attributes
        attr = Rdo.ObjectAttributes()
        attr.LayerIndex = layer_index
        attr.Name = f"Segment {layer_id}/{line_id}/{segment_id}"
        attr.SetUserString("Layer", layer_id)
        attr.SetUserString("Line", line_id)
        attr.SetUserString("Type", forced_type)
        attr.SetUserString(
            "Extrusion", "1" if p1.get("Point_Info", "0") != "0" else "0"
        )
        attr.SetUserString("Linewidth [mm]", str(round(p1["Linewidth"], precision)))
        attr.SetUserString("Flow [mm^3/s]", str(round(p1["Flow"], precision)))
        attr.SetUserString("RPM [1/min]", str(round(p1["RPM"], precision)))
        attr.SetUserString("Voltage [V]", str(round(p1["Voltage"], precision)))
        attr.SetUserString("Velocity [m/s]", str(round(p1["Vel_CP_Max"], precision)))

        # Set linetype
        color_hex = line_color_dict.get(visual_type, "#FFFFFF")
        linetype_name = linetype_dict.get(visual_type, "Continuous")

        # PRINT VIEW
        # Color
        color_rgb = Color.FromArgb(*color_name_to_rgb(color_hex))
        attr.ObjectColor = color_rgb
        attr.ColorSource = Rdo.ObjectColorSource.ColorFromObject
        attr.PlotColorSource = Rdo.ObjectPlotColorSource.PlotColorFromObject
        attr.PlotColor = attr.ObjectColor

        # Linewidth for Print View determined either by Flow (Linewidth) for G1 or setup.Rhino.line_width.json
        if p1["Move"] == "G1":
            plot_weight = round(p1["Linewidth"], precision)
        else:
            plot_weight = line_widths.get(linetype_name.lower(), 0.5)

        attr.PlotWeightSource = Rdo.ObjectPlotWeightSource.PlotWeightFromObject
        attr.PlotWeight = float(plot_weight)

        # Try to find stated linetype in rhino file. Else use Continuous
        linetype_index = next(
            (
                lt.Index
                for lt in rhino_file.AllLinetypes
                if lt.Name.lower() == linetype_name.lower()
            ),
            None,
        )
        if linetype_index is not None:
            attr.LinetypeSource = Rdo.ObjectLinetypeSource.LinetypeFromObject
            attr.LinetypeIndex = linetype_index
        else:
            print(
                f"[WARNING] Linientyp '{linetype_name}' not found, using 'Continuous' as default"
            )

        rhino_file.Objects.AddLine(line, attr)
        print(f"    Line {layer_id}/{line_id}/{segment_id} added")


def create_points(
    points: list[dict],
    rhino_file: Rfi.File3dm,
    point_color: dict[str, str],
    point_print: bool,
) -> None:
    """
    DESCRIPTION:
    Creates points in the Rhino file on the correct sub-sub-layer with colors and attributes.

    :param points: List of points.
    :param rhino_file: Rhino file.
    :param point_color: Dictionary of color names from setup.Rhino.line_types_color.json
    :param point_print: States if all points are visible in rhino file (true) or only (start, stop, retract, protract, beginning, end) with false
    """

    for point_data in points:
        if not point_print and point_data["Point_Info"] not in {
            "start",
            "stop",
            "retract",
            "protract",
            "beginning",
            "end",
        }:
            continue

        # formating point info
        layer_id = f"{point_data['Layer']:04d}"
        line_id = f"{point_data['Line']:04d}"
        point_id = f"{point_data['Point']:04d}"
        point_info = point_data["Point_Info"]
        x, y, z = point_data["X"], point_data["Y"], point_data["Z"]

        # Create geometry
        point = Rg.Point3d(x, y, z)

        # Set color
        color_hex = point_color.get(point_info, "#000000")
        color_rgb = Color.FromArgb(*color_name_to_rgb(color_hex))

        # Get layer index of current point
        layer_index = get_layer_index(rhino_file, layer_id, line_id)
        if layer_index is None:
            print(
                f"[WARNING] No Layer found for point {layer_id}/{line_id}/{point_id}. Skipping point"
            )
            continue

        # Object attributes for Attribute User Text
        attr = Rdo.ObjectAttributes()
        attr.LayerIndex = layer_index
        attr.ObjectColor = color_rgb
        attr.ColorSource = Rdo.ObjectColorSource.ColorFromObject
        attr.PlotColorSource = Rdo.ObjectPlotColorSource.PlotColorFromObject
        attr.PlotColor = attr.ObjectColor
        attr.Name = f"Point {layer_id}/{line_id}/{point_id}"
        attr.SetUserString("Layer", layer_id)
        attr.SetUserString("Line", line_id)
        attr.SetUserString("Point", point_id)
        attr.SetUserString("Point_Info", point_info)

        # Add point to rhino file
        rhino_file.Objects.AddPoint(point, attr)
        print(f"    Point {layer_id}/{line_id}/{point_id} added")
