from pathlib import Path

import Rhino.Geometry as Rg
from Rhino.FileIO import File3dm
from Rhino.DocObjects import ObjectAttributes, ObjectColorSource

from System.Drawing import Color


def add_print_bed(
    file_path: Path, x_max: int, y_max: int, parent_layer: str, sublayer=None
) -> bool:
    """
    DESCRIPTION:
    Adds a print bed surface to a Rhino file under a specified parent or sublayer.

    :param file_path: Path to the Rhino file.
    :param x_max: Maximum X dimension of the print bed.
    :param y_max: Maximum Y dimension of the print bed.
    :param parent_layer: Parent layer name for the print bed.
    :param sublayer: Optional sublayer name. If None, the print bed is added to the parent layer.
    """
    # Load the existing Rhino file
    rhino_file = File3dm.Read(str(file_path))
    if rhino_file is None:
        print(f"[ERROR] Could not open the Rhino file at {file_path}")
        return False

    # Determine the layer to add the print bed to
    layer_name = f"{sublayer}" if sublayer else f"{parent_layer}"

    # Find the specified layer in the rhino file
    layer = next((l for l in rhino_file.Layers if l.Name == layer_name), None)
    if layer is None:
        print(f"[ERROR] Layer '{layer_name}' not found in the file.")
        return False

    # Create the printbed geometry as a 3D rectangle
    rect = Rg.Rectangle3d(Rg.Plane.WorldXY, float(x_max), float(y_max))

    # Convert the rectangle to a polyline curve
    rect_curve = rect.ToPolyline().ToNurbsCurve()

    # Extrude the curve to create a solid
    extrusion = Rg.Extrusion.Create(rect_curve, -50, True)

    # Assign attributes
    attributes = ObjectAttributes()
    attributes.LayerIndex = layer.Index
    attributes.ObjectColor = Color.FromArgb(128, 128, 128)  # Grey color
    attributes.ColorSource = ObjectColorSource.ColorFromObject
    attributes.Name = "printbed"

    # Add the geometry to the Rhino file
    rhino_file.Objects.AddExtrusion(extrusion, attributes)
    print(f"[INFO] Added print bed to layer '{layer_name}'.")

    # Save the updated file
    rhino_file.Write(str(file_path), 8)
    print(f"[INFO]Updated Rhino file saved to {file_path}.")
    return True
