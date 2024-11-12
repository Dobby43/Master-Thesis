import pyvista as pv
import numpy as np
from typing import List, Dict, Union


def plot_bed(
    bed_size_x: float,
    bed_size_y: float,
    bed_size_z: float,
    line_thickness: float = 0,
    tick_font_size: float = 12.0,
):
    """
    Creates and displays the 3D printing bed with specified dimensions.

    :param bed_size_x: Size of the print bed along the X-axis.
    :param bed_size_y: Size of the print bed along the Y-axis.
    :param bed_size_z: Size of the print volume along the Z-axis.
    :param line_thickness: Thickness of the outline lines for the volume edges.
    :param tick_font_size: Font size for the axis ticks.
    :return: A PyVista plotter object containing the print bed.
    """
    # Initialize PyVista plotter
    plotter = pv.Plotter()

    # Create a gray XY-plane grid at Z = 0
    grid_x, grid_y = np.meshgrid(
        np.arange(0, bed_size_x, 100, dtype=np.float32),  # Steps of 100 mm along X
        np.arange(0, bed_size_y + 1, 100, dtype=np.float32),  # Steps of 100 mm along Y
    )
    grid_z = np.zeros_like(grid_x)  # XY plane at Z=0
    bed_surface = pv.StructuredGrid(grid_x, grid_y, grid_z)
    plotter.add_mesh(bed_surface, color="lightgrey", opacity=0.5)

    # Function to add a tube (thicker line) for outline edges
    def add_tube_line(start, end, color="grey", radius=line_thickness):
        line = pv.Line(start, end)
        tube = line.tube(radius=radius)
        plotter.add_mesh(tube, color=color)

    # Add corner lines for the Z volume and height at Z=Z_max
    corner_points = [
        ([0, 0, 0], [0, 0, bed_size_z]),
        ([bed_size_x, 0, 0], [bed_size_x, 0, bed_size_z]),
        ([0, bed_size_y, 0], [0, bed_size_y, bed_size_z]),
        ([bed_size_x, bed_size_y, 0], [bed_size_x, bed_size_y, bed_size_z]),
    ]
    for start, end in corner_points:
        add_tube_line(start, end, color="grey")

    # Add top edges at Z=Z_max
    top_edges = [
        ([0, 0, bed_size_z], [bed_size_x, 0, bed_size_z]),
        ([0, 0, bed_size_z], [0, bed_size_y, bed_size_z]),
        ([bed_size_x, 0, bed_size_z], [bed_size_x, bed_size_y, bed_size_z]),
        ([0, bed_size_y, bed_size_z], [bed_size_x, bed_size_y, bed_size_z]),
    ]
    for start, end in top_edges:
        add_tube_line(start, end, color="grey")

    # Set plot area and background color
    plotter.set_background("white")

    # Center the camera and set the focal point to the middle of the print bed
    plotter.camera.focal_point = (bed_size_x / 2, bed_size_y / 2, bed_size_z / 2)
    plotter.camera.position = (bed_size_x * 1.5, -bed_size_y / 2, bed_size_z / 2)

    # Set visible bounds with show_bounds, without axis titles
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

    return plotter  # Return plotter object


def plot_gcode(
    plotter: pv.Plotter,
    processed_gcode: List[Dict[str, Union[str, float, int, None]]],
    layers: str,
):
    """
    Adds a G-code path to an existing PyVista plotter instance, with colors for different line types.

    :param plotter: A PyVista plotter object that contains the print bed.
    :param processed_gcode: List of processed G-code dictionaries.
    :param layers: Specify layers to plot as "all", a single layer number (e.g., "1"),
                   or a range of layers (e.g., "1-5").
    """
    # Define color mapping for types
    color_mapping = {
        "SUPPORT": "green",
        "WALL_OUTER": "blue",
        "WALL_INNER": "cyan",
        "SURFACE": "yellow",
        "INFILL": "red",
        "CURB": "magenta",
        "UNKNOWN": "grey",
        "TRAVEL": "grey",
    }

    # Determine layer filter based on user input
    layer_range = None
    if layers != "all":
        if "-" in layers:
            start, end = map(int, layers.split("-"))
            layer_range = range(start, end + 1)
        else:
            layer_range = {int(layers)}  # Single layer as a set for easy checking

    # Initialize storage for line data grouped by type
    grouped_lines = {type_name: [] for type_name in color_mapping.keys()}
    previous_point = None
    previous_type = None

    # Build lines grouped by type
    for entry in processed_gcode:
        if layer_range is not None and entry["Layer"] not in layer_range:
            continue  # Skip entries outside the specified layer range

        if entry["X"] is not None and entry["Y"] is not None and entry["Z"] is not None:
            current_point = [entry["X"], entry["Y"], entry["Z"]]
            current_type = entry["Type"] or "UNKNOWN"

            if entry["Move"] == "G0":
                # If Move is G0, set Type to TRAVEL
                current_type = "TRAVEL"

            if previous_point is not None:
                grouped_lines[current_type].append([previous_point, current_point])

            previous_point = current_point
            previous_type = current_type

    # Plot each type in a single batch
    for type_name, line_segments in grouped_lines.items():
        if not line_segments:
            continue  # Skip if no lines for this type

        # Combine all line segments into a single PolyData object
        points = []
        lines = []
        for i, (start, end) in enumerate(line_segments):
            points.extend(start)
            points.extend(end)
            lines.extend([2, i * 2, i * 2 + 1])  # Line structure for PolyData

        points = np.array(points).reshape(-1, 3)
        lines = np.array(lines, dtype=np.int32)

        polyline = pv.PolyData()
        polyline.points = points
        polyline.lines = lines
        plotter.add_mesh(polyline, color=color_mapping[type_name], line_width=2)

    # Show the plot
    plotter.show()
