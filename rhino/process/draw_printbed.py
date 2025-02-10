import Rhino.Geometry as rg
from Rhino.FileIO import File3dm
from Rhino.DocObjects import ObjectAttributes, ObjectColorSource
from System.Drawing import Color


def add_print_bed(filename, x_max, y_max, parent_layer, sublayer=None):
    """
    Adds a print bed surface to a Rhino file under a specified parent or sublayer.
    :param filename: Path to the Rhino file.
    :param x_max: Maximum X dimension of the print bed.
    :param y_max: Maximum Y dimension of the print bed.
    :param parent_layer: Parent layer name for the print bed.
    :param sublayer: Optional sublayer name. If None, the print bed is added to the parent layer.
    """
    # Load the existing Rhino file
    rhino_file = File3dm.Read(str(filename))
    if rhino_file is None:
        print(f"Error: Could not open the Rhino file at {filename}.")
        return False

    # Determine the layer to add the print bed to
    layer_name = f"{sublayer}" if sublayer else f"{parent_layer}"

    # Find the specified layer
    layer = next((l for l in rhino_file.Layers if l.Name == layer_name), None)
    if layer is None:
        print(f"Error: Layer '{layer_name}' not found in the file.")
        return False

    # Create the print bed geometry
    rect = rg.Rectangle3d(rg.Plane.WorldXY, x_max, y_max)

    # Convert the rectangle to a polyline curve
    rect_curve = rect.ToPolyline().ToNurbsCurve()

    # Extrude the curve to create a solid
    extrusion = rg.Extrusion.Create(rect_curve, -50, True)

    # Assign attributes
    attributes = ObjectAttributes()
    attributes.LayerIndex = layer.Index
    attributes.ObjectColor = Color.FromArgb(128, 128, 128)  # Gray color
    attributes.ColorSource = ObjectColorSource.ColorFromObject
    attributes.Name = "printbed"

    # Add the geometry to the Rhino file
    rhino_file.Objects.AddExtrusion(extrusion, attributes)
    print(f"Added print bed to layer '{layer_name}'.")

    # Save the updated file
    rhino_file.Write(str(filename), 8)
    print(f"Updated Rhino file saved to {filename}.")
    return True
