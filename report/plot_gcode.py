import pyvista as pv
import numpy as np
import os
from typing import List, Dict, Union


def plot_bed(
    bed_size_x: float,
    bed_size_y: float,
    bed_size_z: float,
    line_thickness: float = 0,
    tick_font_size: float = 0,
):
    """
    DESCRIPTION:
    Creates and displays a 3D printing bed with the specified dimensions and visualization details.

    :param bed_size_x: Size of the print bed along the X-axis.
    :param bed_size_y: Size of the print bed along the Y-axis.
    :param bed_size_z: Size of the print volume along the Z-axis.
    :param line_thickness: Thickness of the outline lines for the volume edges.
    :param tick_font_size: Font size of the tick labels.

    :return: A PyVista plotter object containing the rendered print bed visualization.
    """

    # define width of plot
    width_px = int((6.5 / 2.54) * 300)
    height_px = int((3.5 / 2.54) * 300)
    plotter = pv.Plotter(window_size=[width_px, height_px], off_screen=True)

    # define grid
    grid_x, grid_y = np.meshgrid(
        np.arange(0, bed_size_x, 50, dtype=np.float32),
        np.arange(0, bed_size_y + 1, 50, dtype=np.float32),
    )
    grid_z = np.zeros_like(grid_x)
    # Add printbed as light grey plane
    bed_surface = pv.StructuredGrid(grid_x, grid_y, grid_z)
    plotter.add_mesh(bed_surface, color="lightgrey", opacity=0.5)

    # Function to add 3-dimensional borders to the plot
    def add_tube_line(start, stop, color="grey", radius=line_thickness):
        line = pv.Line(start, stop)
        tube = line.tube(radius=radius)
        plotter.add_mesh(tube, color=color)

    # Add Corner lines surrounding build volume
    for beginning, end in [
        ([0, 0, 0], [0, 0, bed_size_z]),
        ([bed_size_x, 0, 0], [bed_size_x, 0, bed_size_z]),
        ([0, bed_size_y, 0], [0, bed_size_y, bed_size_z]),
        ([bed_size_x, bed_size_y, 0], [bed_size_x, bed_size_y, bed_size_z]),
        ([0, 0, bed_size_z], [bed_size_x, 0, bed_size_z]),
        ([0, 0, bed_size_z], [0, bed_size_y, bed_size_z]),
        ([bed_size_x, 0, bed_size_z], [bed_size_x, bed_size_y, bed_size_z]),
        ([0, bed_size_y, bed_size_z], [bed_size_x, bed_size_y, bed_size_z]),
    ]:
        add_tube_line(beginning, end)

    plotter.set_background("white")
    # align picture such, that the longest axis is always in cross direction (to fit .docx file)
    if bed_size_x >= bed_size_y:
        # Long side along x-axis
        plotter.camera.position = (bed_size_x / 2, bed_size_y / 2, bed_size_z * 3)
        plotter.camera.focal_point = (bed_size_x / 2, bed_size_y / 2, 0)
        plotter.camera.up = (0, 1, 0)
    else:
        # long side along y-axis
        plotter.camera.position = (bed_size_x / 2, bed_size_y / 2, bed_size_z * 3)
        plotter.camera.focal_point = (bed_size_x / 2, bed_size_y / 2, 0)
        plotter.camera.up = (1, 0, 0)

    plotter.show_bounds(
        bounds=(0, bed_size_x, 0, bed_size_y, 0, bed_size_z),
        grid="back",
        xtitle="",
        ytitle="",
        ztitle="",
        location="outer",
        all_edges=True,
        font_size=tick_font_size,
    )

    # Plot origin in rgb colors
    origin = pv.PolyData()
    origin.points = np.array([[0, 0, 0]])
    length_xy = min(bed_size_x, bed_size_y)
    plotter.add_lines(
        np.array([[0, 0, 0], [length_xy / 4, 0, 0]]), color="red", width=5
    )
    plotter.add_lines(
        np.array([[0, 0, 0], [0, length_xy / 4, 0]]), color="green", width=5
    )
    plotter.add_lines(
        np.array([[0, 0, 0], [0, 0, bed_size_z / 4]]), color="blue", width=5
    )
    plotter.add_mesh(origin, color="red", point_size=15, render_points_as_spheres=True)

    return plotter


def plot_gcode(
    plotter: pv.Plotter,
    points: List[Dict[str, Union[str, float, int, None]]],
    layers: str,
    line_types_color: Dict[str, str],
):
    """
    DESCRIPTION:
    Adds a G-code path visualization to an existing PyVista plotter instance with color-coded types.

    :param plotter: A PyVista plotter object where the G-code visualization will be added.
    :param points: List of dictionaries representing processed G-code lines.
    :param layers: Specify layers to visualize. Use "all" for all layers, a single layer number (e.g., "1"),
            or a range of layers (e.g., "1-5").
    :param line_types_color: Dictionary of colors to use for each line type.

    :return: the PyVista plotter updated with the G-code visualization.
    """
    # Extract color mapping from line_types, defaulting to travel for retract/protract
    from collections import defaultdict

    color_mapping = line_types_color.copy()
    color_mapping.setdefault("retract", color_mapping.get("travel", "#808080"))
    color_mapping.setdefault("protract", color_mapping.get("travel", "#808080"))
    color_mapping.setdefault("unknown", "#000000")

    # Parse layer range selection
    layer_range = None
    if layers != "all":
        if "-" in layers:
            start, end = map(int, layers.split("-"))
            layer_range = range(start, end + 1)
        else:
            layer_range = {int(layers)}

    grouped_lines = defaultdict(list)
    previous_point = None

    # Iterate over the G-code data and group line segments by type
    for entry in points:
        if layer_range and entry["Layer"] not in layer_range:
            continue
        if None not in (entry["X"], entry["Y"], entry["Z"]):
            current_point = [entry["X"], entry["Y"], entry["Z"]]
            current_type = entry["Type"] or "unknown"
            # Normalize movement type (merge retract/protract into travel)
            if current_type in {"retract", "protract"}:
                current_type = "travel"
            # Store segment if there is a valid previous point
            if previous_point:
                grouped_lines[current_type].append([previous_point, current_point])
            previous_point = current_point

    # Render each group of lines with the assigned color
    for type_name, segments in grouped_lines.items():
        if segments:
            points, lines = [], []
            for i, (start, end) in enumerate(segments):
                points.extend(start)
                points.extend(end)
                lines.extend([2, i * 2, i * 2 + 1])
            polyline = pv.PolyData()
            polyline.points = np.array(points).reshape(-1, 3)
            polyline.lines = np.array(lines, dtype=np.int32)
            plotter.add_mesh(
                polyline, color=color_mapping.get(type_name, "grey"), line_width=5
            )

    # Set the output image size to 6.5 x 3.5 cm at 300 dpi
    width_px = int((6.5 / 2.54) * 300)
    height_px = int((3.5 / 2.54) * 300)
    plotter.window_size = [width_px, height_px]

    # Save the plot as a PNG image in the working directory
    image_path = os.path.join(os.getcwd(), "gcode_plot.png")

    plotter.screenshot(image_path)
    plotter.close()
