import pyvista as pv
import numpy as np
import re
from typing import List


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
    plotter = pv.Plotter()  # TODO: Ursprung mit RGB hinzufügen

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


def plot_gcode_path(plotter: pv.Plotter, gcode_lines: List[str], layers: str = "all"):
    """
    Adds a G-code path to an existing PyVista plotter instance, with options for filtering by layer.
    G0 moves are displayed in green, and G1 moves in blue.

    :param plotter: A PyVista plotter object that contains the print bed.
    :param gcode_lines: List of G-code lines representing the path.
    :param layers: Specify layers to plot as "all", a single layer number (e.g., "1"),
                   or a range of layers (e.g., "1-5").
    """
    # Determine layer filter based on user input
    layer_range = None
    if layers != "all":
        if "-" in layers:
            start, end = map(int, layers.split("-"))
            layer_range = range(start, end + 1)
        else:
            layer_range = {int(layers)}  # Single layer as a set for easy checking

    # Initialize lists for coordinates and command types
    x_coords, y_coords, z_coords = [], [], []
    gcode_commands = []  # Track whether each line is a G0 or G1 command
    current_layer = -1  # Initialize layer counter
    pattern = r"(G[01])\s+X\s*([-?\d\.]+)\s*,\s*Y\s*([-?\d\.]+)\s*,\s*Z\s*([-?\d\.]+)"

    # Extract coordinates and command type (G0 or G1) from G-code lines
    for line in gcode_lines:
        # Check for layer comment to update the current layer
        layer_match = re.match(r";LAYER:(\d+)", line)
        if layer_match:
            current_layer = int(layer_match.group(1))
            continue  # Move to the next line after updating the current layer

        # Skip lines if they're outside the specified layer range
        if layer_range is not None and current_layer not in layer_range:
            continue

        # Match G-code coordinates
        match = re.search(pattern, line)
        if match:
            command = match.group(1)  # G0 or G1 command
            x_val = float(match.group(2)) if match.group(2) else None
            y_val = float(match.group(3)) if match.group(3) else None
            z_val = float(match.group(4)) if match.group(4) else None

            if x_val is not None and y_val is not None:
                x_coords.append(x_val)
                y_coords.append(y_val)
                z_coords.append(
                    z_val if z_val is not None else (z_coords[-1] if z_coords else 0)
                )
                gcode_commands.append(command)  # Store the command type

    # Check if points are found
    if not x_coords or not y_coords:
        print("No G-code coordinates found.")
        return

    # Convert coordinates into an array of points
    points = np.column_stack((x_coords, y_coords, z_coords))

    # Separate the line segments for G0 and G1 commands
    lines_g0, lines_g1 = [], []
    for i in range(len(points) - 1):
        if gcode_commands[i] == "G0" and gcode_commands[i + 1] == "G0":
            lines_g0.extend([2, i, i + 1])  # G0 move
        else:
            lines_g1.extend([2, i, i + 1])  # G1 move

    # Plot G0 moves in green
    if lines_g0:
        polyline_g0 = pv.PolyData()
        polyline_g0.points = points
        polyline_g0.lines = np.array(lines_g0)
        plotter.add_mesh(polyline_g0, color="green", line_width=2)

    # Plot G1 moves in blue
    if lines_g1:
        polyline_g1 = pv.PolyData()
        polyline_g1.points = points
        polyline_g1.lines = np.array(lines_g1)
        plotter.add_mesh(polyline_g1, color="blue", line_width=2)

    # Show the plot
    plotter.show()
