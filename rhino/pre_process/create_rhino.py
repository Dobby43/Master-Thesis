from typing import Any
from pathlib import Path

import rhinoinside

# Load Rhino.Inside
rhinoinside.load()

import Rhino.DocObjects as Rdo
import Rhino.FileIO as Rfi

# Pycharm IDE does not recognize System
import System as Sys
import System.Drawing as Sd


from rhino.pre_process.rhino_layermanager import layer_structure
from rhino.pre_process.rhino_linemanager import linetype_patterns


def initialize_rhino_file(
    directory: str, filename: str, max_layers: int, sublayers: dict[int, int]
) -> Path:
    """
    DESCRIPTION:
    Initializes a Rhino file, creates a custom layer structure, adds linetypes, and saves the file.

    :param directory: The directory to save the Rhino file to.
    :param filename: The name of the Rhino file.
    :param max_layers: The maximum number of layers for the parent-layer toolpath to create.
    :param sublayers: A Dictionary of sublayers (for each line in the layer) to add to the Rhino file.

    :return: Path to rhino file
    """
    rhino_file = Rfi.File3dm()

    # Generate the layer structure dynamically
    layers = layer_structure(max_layers)

    # Create the layer structure
    create_layer_structure(rhino_file, layers, sublayers)

    # Add custom linetypes to the file
    create_linetypes(rhino_file)

    # Save the Rhino file
    output_path = Path(directory) / f"{filename}"
    rhino_file.Write(str(output_path), 8)  # version of Rhino
    print(f"[INFO] Rhino file saved to {output_path}")
    return output_path


def create_linetypes(rhino_file: Rfi.File3dm):
    """
    DESCRIPTION:
    Creates linetypes in the Rhino file using patterns from rhino_linemanager
    and applies line widths from the provided dictionary.

    :param rhino_file: The Rhino file to add the linetypes to
    """
    # Retrieve patterns from the linetype manager
    patterns = linetype_patterns()

    for i, (name, pattern) in enumerate(patterns.items()):
        linetype = Rdo.Linetype()
        linetype.Name = name

        # Apply the pattern
        for segment_length, is_gap in pattern:
            linetype.AppendSegment(segment_length, is_gap)

        # Add to the Rhino file
        rhino_file.AllLinetypes.Add(linetype)
        print(f"[INFO] linetype '{name}' created with pattern {pattern}.")


def create_layer_structure(
    rhino_file: Rfi.File3dm(),
    layer_structure_dict: dict[str, dict[str, Any]],
    sublayer_counts: dict[int, int],
):
    """
    DESCRIPTION:
    Builds a layer structure inside the Rhino file
    toolpath/
        0000/  <- Layer 0
            0000 <-  Line 0
            0001 <-  Line 1
        0001/
            0000
            ...
    printbed/
    robot/

    :param rhino_file: The Rhino file to work in
    :param layer_structure_dict: Dictionary with layer colors and parent names (toolpath, printbed, robot)
    :param sublayer_counts: Dictionary linking the maximum needed sub_layers to the parent layer (from printing layers in toolpath)
    """
    for parent_name, info in layer_structure_dict.items():
        # Create parent layer
        parent_layer = Rdo.Layer()
        parent_layer.Name = parent_name
        parent_layer.Color = Sd.Color.FromArgb(*info["color"])
        rhino_file.Layers.Add(parent_layer)
        print(f"[INFO] Parent Layer '{parent_name}' created")

        # find Parent Layer Objekt
        parent_layer_obj = next(
            (
                l
                for l in rhino_file.Layers
                if l.Name == parent_name and l.ParentLayerId == Sys.Guid.Empty
            ),
            None,
        )
        if not parent_layer_obj:
            print(f"[ERROR] Parent Layer '{parent_name}' could not be found.")
            continue

        parent_layer_id = parent_layer_obj.Id

        # Only for parent layer toolpath sub-sub-layers are created
        if parent_name == "toolpath":
            for layer_num, max_line in sublayer_counts.items():
                layer_name = f"{layer_num:04d}"
                sublayer = Rdo.Layer()
                sublayer.Name = layer_name
                sublayer.ParentLayerId = parent_layer_id
                sublayer.Color = Sd.Color.FromArgb(*info["sublayer_color"])
                rhino_file.Layers.Add(sublayer)

                # Find sub-layer object
                sublayer_obj = next(
                    (
                        l
                        for l in rhino_file.Layers
                        if l.Name == layer_name and l.ParentLayerId == parent_layer_id
                    ),
                    None,
                )
                if not sublayer_obj:
                    print(
                        f"[ERROR] Sublayer '{layer_name}' under '{parent_name}' could not be found"
                    )
                    continue

                sublayer_id = sublayer_obj.Id

                # Create line sub-sub-layers under layer toolpath.layer
                for line_num in range(max_line + 1):
                    line_name = f"{line_num:04d}"
                    line_layer = Rdo.Layer()
                    line_layer.Name = line_name
                    line_layer.ParentLayerId = sublayer_id
                    line_layer.Color = Sd.Color.FromArgb(*info["sublayer_color"])
                    rhino_file.Layers.Add(line_layer)
