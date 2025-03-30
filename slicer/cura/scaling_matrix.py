import numpy as np
from typing import Dict
from robot import mathematical_operators as math


def compute_scaling_and_rotation_matrix(scaling_input: Dict[str, float]) -> str:
    """
    DESCRIPTION:
    Computes a transformation matrix for the slicer configuration.
    First applies rotation, then scaling.

    :param scaling_input: user input for scaling in [%] and rotation in [deg]

    :return: string consisting of the combined rotation and scaling matrix
    (Example: [[2.0, 0.0, 0.0], [0.0, 0.9996242168594817, -0.027412133592044294], [0.0, 0.027412133592044294, 0.9996242168594817]])
    """
    # Extract scaling and rotation parameters
    sx = scaling_input.get("sX", 100) / 100  # Default scaling is 1.0 (no scaling)
    sy = scaling_input.get("sY", 100) / 100
    sz = scaling_input.get("sZ", 100) / 100
    rx = np.radians(scaling_input.get("rX", 0.0))  # Convert degrees to radians
    ry = np.radians(scaling_input.get("rY", 0.0))
    rz = np.radians(scaling_input.get("rZ", 0.0))

    # Calculation of Rotation Matrix
    rotation_matrix = math.Rotation.from_euler_angles(rx, ry, rz, order="ZYX")

    # Scaling matrix
    scaling_matrix = np.diag([sx, sy, sz])

    # Combined transformation matrix: First rotate, then scale
    transformation_matrix = rotation_matrix @ scaling_matrix

    # Format the transformation matrix as a string
    transformation_string = str(transformation_matrix.tolist())

    return transformation_string


# Example usage
if __name__ == "__main__":
    scaling = {
        "sX": 200,  # Scale 120% along X
        "sY": 100,  # Scale 100% along Y
        "sZ": 100,  # Scale 90% along Z
        "rX": 90,  # Rotate 45 degrees around X-axis
        "rY": 0,  # Rotate 30 degrees around Y-axis
        "rZ": 0,  # Rotate 15 degrees around Z-axis
    }

    matrix = compute_scaling_and_rotation_matrix(scaling)
    print("Scaling and Rotation Transformation Matrix for Slicer:")
    print(matrix)
