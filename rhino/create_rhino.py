import rhinoinside

rhinoinside.load()
import time
from pathlib import Path
from Rhino.FileIO import File3dm
from Rhino.DocObjects import Layer
from System.Drawing import Color
from rhino.rhino_layermanager import layer_structure


def initialize_rhino_file(output_directory, filename, max_layers):
    """
    Initializes a Rhino file, creates a custom layer structure, and saves the file.
    :param output_directory: Directory to save the file.
    :param filename: Name of the file without extension.
    :param max_layers: Maximum number of dynamic sublayers to create.
    :return: Path to the saved file.
    """
    rhino_file = File3dm()

    # Generate the layer structure dynamically
    layers = layer_structure(max_layers)

    # Create the layer structure
    create_layer_structure(rhino_file, layers)

    # Save the Rhino file
    current_time = time.strftime("%H_%M_%S")
    output_path = Path(output_directory) / f"{current_time}_{filename}.3dm"
    rhino_file.Write(str(output_path), 8)
    print(f"Rhino file saved to {output_path}.")
    return output_path


def create_layer_structure(rhino_file, layers):
    """
    Creates a layer structure in the Rhino file based on the provided dictionary.
    :param rhino_file: The Rhino file instance.
    :param layers: Dictionary defining the layer structure.
    """
    for parent_name, layer_info in layers.items():
        # Create parent layer
        parent_layer = Layer()
        parent_layer.Name = parent_name
        parent_layer.Color = Color.FromArgb(*layer_info["color"])
        rhino_file.Layers.Add(parent_layer)
        print(f"Parent layer '{parent_name}' created.")

        # Create sublayers
        if layer_info.get("dynamic_sublayers"):
            max_sublayers = layer_info.get("max_sublayers", 0)
            for i in range(max_sublayers + 1):
                sublayer_name = f"{i:04d}"
                sublayer = Layer()
                sublayer.Name = sublayer_name
                sublayer.ParentLayerId = parent_layer.Id
                sublayer.Color = Color.FromArgb(*layer_info["sublayer_color"])
                rhino_file.Layers.Add(sublayer)
                print(f"  Sublayer '{sublayer_name}' added under '{parent_name}'.")
        elif "sublayers" in layer_info:
            for sublayer_name in layer_info["sublayers"]:
                sublayer = Layer()
                sublayer.Name = sublayer_name
                sublayer.ParentLayerId = parent_layer.Id
                sublayer.Color = Color.FromArgb(*layer_info["sublayer_color"])
                rhino_file.Layers.Add(sublayer)
                print(f"  Sublayer '{sublayer_name}' added under '{parent_name}'.")
