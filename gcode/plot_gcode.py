from pathlib import Path
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
    DESCRIPTION:
    Creates and displays a 3D printing bed with the specified dimensions and visualization details.

    ARGUMENTS:
    bed_size_x: Size of the print bed along the X-axis.
    bed_size_y: Size of the print bed along the Y-axis.
    bed_size_z: Size of the print volume along the Z-axis.
    line_thickness: Thickness of the outline lines for the volume edges.
    tick_font_size: Font size for the axis ticks.

    RETURNS:
    A PyVista plotter object containing the rendered print bed visualization.
    """
    # Initialize PyVista plotter
    plotter = pv.Plotter()

    # Create a gray XY-plane grid at Z = 0
    grid_x, grid_y = np.meshgrid(
        np.arange(0, bed_size_x, 50, dtype=np.float32),  # Steps of 100 mm along X
        np.arange(0, bed_size_y + 1, 50, dtype=np.float32),  # Steps of 100 mm along Y
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
    line_types: Dict[str, Dict[str, Union[List[str], str]]],
):
    """
    DESCRIPTION:
    Adds a G-code path visualization to an existing PyVista plotter instance with color-coded types.

    ARGUMENTS:
    plotter: A PyVista plotter object where the G-code visualization will be added.
    processed_gcode: List of dictionaries representing processed G-code lines.
    layers: Specify layers to visualize. Use "all" for all layers, a single layer number (e.g., "1"),
            or a range of layers (e.g., "1-5").
    line_types: Dictionary defining type mappings and attributes (e.g., colors and linetypes).

    RETURNS:
    None. Updates the PyVista plotter with the G-code visualization.
    """
    # Extract color mapping from line_types, defaulting to travel for retract/protract
    color_mapping = {key: value["color"] for key, value in line_types.items()}
    color_mapping.setdefault("retract", color_mapping.get("travel", "grey"))
    color_mapping.setdefault("protract", color_mapping.get("travel", "grey"))

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

    # Build lines grouped by type
    for entry in processed_gcode:
        if layer_range is not None and entry["Layer"] not in layer_range:
            continue  # Skip entries outside the specified layer range

        if entry["X"] is not None and entry["Y"] is not None and entry["Z"] is not None:
            current_point = [entry["X"], entry["Y"], entry["Z"]]
            current_type = entry["Type"] or "unknown"

            # Treat retract and protract as travel if they are not in the dictionary
            if current_type in {"retract", "protract"}:
                current_type = "travel"

            if previous_point is not None:
                grouped_lines[current_type].append([previous_point, current_point])

            previous_point = current_point

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
        plotter.add_mesh(
            polyline, color=color_mapping.get(type_name, "grey"), line_width=2
        )

    # Show the plot
    plotter.show()
