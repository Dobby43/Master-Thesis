import numpy as np
from typing import Dict


def compute_scaling_and_rotation_matrix(scaling_params: Dict[str, float]) -> str:
    """
    Computes a transformation matrix for the slicer configuration.
    First applies rotation, then scaling.

    Arguments:
    scaling_params: Dictionary with the following keys:
        - sX, sY, sZ: Scaling factors along X, Y, Z axes (percentages).
        - rX, rY, rZ: Rotation angles in degrees around X, Y, Z axes.

    Returns:
    Transformation matrix as a string suitable for the slicer.
    """
    # Extract scaling and rotation parameters
    sX = scaling_params.get("sX", 100) / 100  # Default scaling is 1.0 (no scaling)
    sY = scaling_params.get("sY", 100) / 100
    sZ = scaling_params.get("sZ", 100) / 100
    rX = np.radians(scaling_params.get("rX", 0.0))  # Convert degrees to radians
    rY = np.radians(scaling_params.get("rY", 0.0))
    rZ = np.radians(scaling_params.get("rZ", 0.0))

    # Rotation matrices
    rotation_x = np.array(
        [[1, 0, 0], [0, np.cos(rX), -np.sin(rX)], [0, np.sin(rX), np.cos(rX)]]
    )

    rotation_y = np.array(
        [[np.cos(rY), 0, np.sin(rY)], [0, 1, 0], [-np.sin(rY), 0, np.cos(rY)]]
    )

    rotation_z = np.array(
        [[np.cos(rZ), -np.sin(rZ), 0], [np.sin(rZ), np.cos(rZ), 0], [0, 0, 1]]
    )

    # Combined rotation matrix: Rz * Ry * Rx
    rotation_matrix = rotation_z @ rotation_y @ rotation_x

    # Scaling matrix
    scaling_matrix = np.diag([sX, sY, sZ])

    # Combined transformation matrix: First rotate, then scale
    transformation_matrix = rotation_matrix @ scaling_matrix

    # Format the transformation matrix as a string
    transformation_string = str(transformation_matrix.tolist())

    return transformation_string


# Example usage
if __name__ == "__main__":
    scaling_params = {
        "sX": 120,  # Scale 120% along X
        "sY": 100,  # Scale 100% along Y
        "sZ": 90,  # Scale 90% along Z
        "rX": 45,  # Rotate 45 degrees around X-axis
        "rY": 30,  # Rotate 30 degrees around Y-axis
        "rZ": 15,  # Rotate 15 degrees around Z-axis
    }

    matrix = compute_scaling_and_rotation_matrix(scaling_params)
    print("Scaling and Rotation Transformation Matrix for Slicer:")
    print(matrix)
