import rhinoinside

# Load Rhino.Inside
rhinoinside.load()

import Rhino
import Rhino.DocObjects as rdo
import Rhino.FileIO as rfi
import System.Drawing as sd
from pathlib import Path
from rhino.pre_process.rhino_layermanager import layer_structure
from rhino.pre_process.rhino_linemanager import linetype_patterns


def initialize_rhino_file(output_directory, filename, max_layers):
    """
    Initializes a Rhino file, creates a custom layer structure, adds linetypes, and saves the file.
    """
    rhino_file = rfi.File3dm()

    # Generate the layer structure dynamically
    layers = layer_structure(max_layers)

    # Create the layer structure
    create_layer_structure(rhino_file, layers)

    # Add custom linetypes to the file
    create_linetypes(rhino_file)

    # Save the Rhino file
    output_path = Path(output_directory) / f"{filename}"
    rhino_file.Write(str(output_path), 8)  # version of Rhino
    print(f"Rhino file saved to {output_path}")
    return output_path


def create_layer_structure(rhino_file, layers):
    """
    Creates a layer structure in the Rhino file based on the provided dictionary.
    """
    for parent_name, layer_info in layers.items():
        # Create parent layer
        parent_layer = rdo.Layer()
        parent_layer.Name = parent_name
        parent_layer.Color = sd.Color.FromArgb(*layer_info["color"])
        rhino_file.Layers.Add(parent_layer)
        print(f"Parent layer '{parent_name}' created.")

        # Find the parent layer in the Rhino file
        parent_layer_obj = next(
            (l for l in rhino_file.Layers if l.Name == parent_name), None
        )
        if not parent_layer_obj:
            print(f"Error: Parent layer '{parent_name}' not found after creation.")
            continue  # Skip creating sublayers

        parent_layer_id = parent_layer_obj.Id

        # Create dynamic sublayers if specified
        if layer_info.get("dynamic_sublayers"):
            max_sublayers = layer_info.get("max_sublayers", 0)
            for i in range(max_sublayers + 1):
                sublayer_name = f"{i:04d}"
                sublayer = rdo.Layer()
                sublayer.Name = sublayer_name
                sublayer.ParentLayerId = parent_layer_id
                sublayer.Color = sd.Color.FromArgb(*layer_info["sublayer_color"])
                rhino_file.Layers.Add(sublayer)
                print(f"  Sublayer '{sublayer_name}' added under '{parent_name}'.")

        # Create static sublayers if provided
        elif "sublayers" in layer_info:
            for sublayer_name in layer_info["sublayers"]:
                sublayer = rdo.Layer()
                sublayer.Name = sublayer_name
                sublayer.ParentLayerId = parent_layer_id
                sublayer.Color = sd.Color.FromArgb(*layer_info["sublayer_color"])
                rhino_file.Layers.Add(sublayer)
                print(f"  Sublayer '{sublayer_name}' added under '{parent_name}'.")


def create_linetypes(rhino_file):
    """
    Creates linetypes in the Rhino file using patterns from rhino_linemanager
    and applies line widths from the provided dictionary.
    """
    patterns = linetype_patterns()  # Retrieve patterns from the linetype manager

    for i, (name, pattern) in enumerate(patterns.items()):
        linetype = rdo.Linetype()
        linetype.Name = name

        # Apply the pattern
        for segment_length, is_gap in pattern:
            linetype.AppendSegment(segment_length, is_gap)

        # Add to the Rhino file
        rhino_file.AllLinetypes.Add(linetype)
        print(f"linetype '{name}' created with pattern {pattern}.")
