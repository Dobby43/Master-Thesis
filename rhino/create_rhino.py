import rhinoinside

rhinoinside.load()
import time
from pathlib import Path
from Rhino.FileIO import File3dm
from Rhino.DocObjects import Layer
from System.Drawing import Color


def initialize_and_save_rhino_file(max_layer, output_directory, filename):
    """
    Initializes a Rhino file, creates sublayers from 0 to max_layer, and saves the file.
    :param max_layer: Maximum layer value, creates sublayers from 0 to max_layer.
    :param output_directory: Directory where the file will be saved.
    :param filename: Name of the file without extension.
    :return: Path to the saved file.
    """
    rhino_file = File3dm()

    # Create parent layer
    parent_layer_name = "toolpath"
    if not create_parent_layer(rhino_file, parent_layer_name):
        print("Parent layer could not be created. Aborting.")
        return None

    # Create sublayers
    if not create_sublayers(rhino_file, parent_layer_name, max_layer):
        print("Sublayers could not be created. Aborting.")
        return None

    # Add timestamp to the filename
    current_time = time.strftime("%H_%M_%S")
    timestamped_filename = f"{current_time}_{filename}"

    # Save the file
    output_path = save_rhino_file(rhino_file, output_directory, timestamped_filename)
    return output_path


def create_parent_layer(rhino_file, parent_layer_name) -> bool:
    """
    Creates the parent layer and immediately checks if it was successfully added.
    :param rhino_file: The Rhino file instance.
    :param parent_layer_name: Name of the parent layer.
    :return: True if the parent layer was created successfully, False otherwise.
    """
    # Create parent layer
    new_layer = Layer()
    new_layer.Name = parent_layer_name
    new_layer.Color = Color.FromArgb(255, 255, 255)  # White
    rhino_file.Layers.Add(new_layer)
    print(f"Attempting to create parent layer '{parent_layer_name}'.")

    # Check if parent layer is successfully created
    if any(layer.Name == parent_layer_name for layer in rhino_file.Layers):
        print(f"Parent layer '{parent_layer_name}' created successfully.")
        return True

    print(f"Failed to create parent layer '{parent_layer_name}'.")
    return False


def create_sublayers(rhino_file, parent_layer_name, max_layer):
    """
    Creates sublayers from 0 to max_layer under the specified parent layer.
    :param rhino_file: The Rhino file instance.
    :param parent_layer_name: Name of the parent layer.
    :param max_layer: Maximum layer value.
    :return: True if all sublayers were successfully created, False otherwise.
    """
    if max_layer < 0:
        print("Invalid maximum layer value. Aborting.")
        return False

    # Find the parent layer
    parent_layer = next(
        (l for l in rhino_file.Layers if l.Name == parent_layer_name), None
    )
    if not parent_layer:
        print(f"Parent layer '{parent_layer_name}' not found.")
        return False

    parent_layer_id = parent_layer.Id

    # Create sublayers from 0 to max_layer
    for i in range(max_layer + 1):  # Including max_layer
        sublayer_name = f"{i:04d}"

        # Create the sublayer
        new_layer = Layer()
        new_layer.Name = sublayer_name
        new_layer.ParentLayerId = parent_layer_id
        new_layer.Color = Color.FromArgb(0, 0, 255)  # Blue

        rhino_file.Layers.Add(new_layer)
        print(f"Sublayer '{sublayer_name}' created.")

    print("All sublayers successfully created.")
    return True


def save_rhino_file(rhino_file, output_directory, filename):
    """
    Saves the Rhino file to the specified directory.
    :param rhino_file: The Rhino file instance.
    :param output_directory: Directory to save the file.
    :param filename: Name of the file to save (with timestamp added).
    :return: Path to the saved file.
    """
    output_path = Path(output_directory) / f"{filename}.3dm"
    rhino_file.Write(str(output_path), 8)
    print(f"File saved successfully to {output_path}")
    return output_path
