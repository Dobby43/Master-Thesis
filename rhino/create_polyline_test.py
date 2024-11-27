from pathlib import Path
import rhinoinside
from typing import List, Dict
from gcode.gcode_dictionaries import get_type_values
from matplotlib import colors

rhinoinside.load()

import Rhino.Geometry as rg
import Rhino.FileIO as rfi
import Rhino.DocObjects as rdo
from System.Drawing import Color
from System.Collections.Generic import List as NetList


# Funktion zur Umwandlung von Farbnamen in RGB-Werte
def color_name_to_rgb(color_name):

    try:
        rgb_normalized = colors.to_rgb(color_name)
        return tuple(int(c * 255) for c in rgb_normalized)
    except ValueError:
        print(f"Invalid color name: {color_name}")
        return (0, 0, 0)  # Fallback to black if color is invalid


class RhinoLayerManager:
    def __init__(self, rhino_file: rfi.File3dm):
        self.rhino_file = rhino_file

    def ensure_layers(self, layers_to_create: dict) -> dict:

        layer_indices = {}

        # Versuch, alle Layer zu erstellen
        for layer_name, color_rgb in layers_to_create.items():
            new_layer = rdo.Layer()
            new_layer.Name = layer_name
            r, g, b = color_rgb
            new_layer.Color = Color.FromArgb(r, g, b)

            # print(
            #     f"Attempting to create layer: Name={layer_name}, Color={new_layer.Color}"
            # )
            layer_index = self.rhino_file.Layers.Add(new_layer)

            if layer_index is not None:
                print(
                    f"Layer '{layer_name}' created successfully with index {layer_index}"
                )
                layer_indices[layer_name] = layer_index
            else:
                print(f"Layer '{layer_name}' creation returned None. Verify later.")

        # Verifizieren, ob alle Layer existieren
        print("Verifying all created layers...")
        for layer_name in layers_to_create.keys():
            if layer_name not in layer_indices:
                # Prüfen, ob der Layer jetzt existiert
                existing_layer = next(
                    (l for l in self.rhino_file.Layers if l.Name == layer_name), None
                )
                if existing_layer:
                    print(
                        f"Layer '{layer_name}' found after verification. Index: {existing_layer.Index}"
                    )
                    layer_indices[layer_name] = existing_layer.Index
                else:
                    print(
                        f"ERROR: Layer '{layer_name}' does not exist after verification."
                    )

        return layer_indices


def parse_gcode_to_points(data: list[dict]) -> list[dict]:

    print("Parsing G-Code data...")
    points_list = []

    for entry in data:
        points_list.append(
            {
                "Point": (entry["X"], entry["Y"], entry["Z"]),
                "Layer": entry["Layer"],
                "Type": entry["Type"],
            }
        )

    print(f"Parsed {len(points_list)} points.")
    return points_list


def create_rhino_geometry(points_list, rhino_file, layer_indices):

    # Laden Farbdefinitionen
    TYPE_VALUES = get_type_values()

    # Polylinien gruppieren
    polylines = {}
    for point_data in points_list:
        layer = point_data["Layer"]
        move_type = point_data["Type"]

        key = (layer, move_type)
        if key not in polylines:
            polylines[key] = []

        polylines[key].append(rg.Point3d(*point_data["Point"]))

    # Polylinien zu ihren Layern hinzufügen
    for (layer, move_type), points in polylines.items():
        try:
            print(f"Processing polyline: Layer {layer}, Type {move_type}")
            if len(points) < 2:
                print(
                    f"Skipping polyline creation for Layer {layer}, Type {move_type} due to insufficient points."
                )
                continue

            # Polyline erstellen
            net_points = NetList[rg.Point3d]()
            for point in points:
                net_points.Add(point)

            polyline_curve = rg.PolylineCurve(net_points)
            attributes = rdo.ObjectAttributes()

            # Layer-Name bestimmen
            layer_name = f"Layer_{layer}"
            layer_index = layer_indices.get(layer_name)

            if layer_index is None:
                print(
                    f"ERROR: Layer index for '{layer_name}' not found. Skipping geometry."
                )
                continue

            # Polylinienfarbe aus TYPE_VALUES
            color_name = TYPE_VALUES.get(move_type, {}).get("Color", "black")
            polyline_color_rgb = color_name_to_rgb(color_name)

            # Attribute setzen
            attributes.LayerIndex = layer_index
            attributes.ObjectColor = Color.FromArgb(*polyline_color_rgb)
            attributes.ColorSource = rdo.ObjectColorSource.ColorFromObject
            attributes.SetUserString("Type", move_type)

            # Geometrie hinzufügen
            rhino_file.Objects.AddCurve(polyline_curve, attributes)
            print(
                f"Added polyline to Layer {layer}, Type {move_type}, with Attribute Type={move_type}"
            )
        except Exception as e:
            print(f"Error adding polyline to file: {e}")


def export_rhino(gcode_data: list[dict], export_directory: str, export_filename: str):
    try:
        rhino_file = rfi.File3dm()
        layer_manager = RhinoLayerManager(rhino_file)

        # Parse G-Code
        points_list = parse_gcode_to_points(gcode_data)

        # Alle Layer erstellen
        layers_to_create = {}
        for point_data in points_list:
            layer_name = f"Layer_{point_data['Layer']}"
            layers_to_create[layer_name] = (0, 0, 255)  # Standardfarbe Blau

        # Layer erstellen, Indizes abrufen
        layer_indices = layer_manager.ensure_layers(layers_to_create)

        # Geometrie erstellen
        create_rhino_geometry(points_list, rhino_file, layer_indices)

        # Datei speichern
        output_path = Path(export_directory) / f"{export_filename}.3dm"
        rhino_file.Write(str(output_path), 8)
        print(f"File saved successfully to {output_path}")
    except Exception as e:
        print(f"Error exporting Rhino file: {e}")
