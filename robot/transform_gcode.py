from typing import List, Dict, Union
import numpy as np


def transform_tcp_to_base(
    points: List[Dict[str, Union[str, float, int, None]]],
    tool_offset: Dict[str, float],
    base_pose: Dict[str, float],
    acuracy: int,
) -> List[Dict[str, float]]:
    """
    Transforms a list of TCP coordinates from the printer bed frame to the robot base frame.
    """

    def rotation_matrix(a: float, b: float, c: float) -> np.ndarray:
        """
        Generates a rotation matrix from Euler angles (in degrees).

        """
        a, b, c = np.radians([a, b, c])

        rx = np.array(
            [[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]]
        )

        ry = np.array(
            [[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]]
        )

        rz = np.array(
            [[np.cos(c), -np.sin(c), 0], [np.sin(c), np.cos(c), 0], [0, 0, 1]]
        )

        return rz @ ry @ rx

    # Extract base position and orientation
    base_position = np.array([base_pose["X"], base_pose["Y"], base_pose["Z"]])
    base_orientation = rotation_matrix(base_pose["A"], base_pose["B"], base_pose["C"])

    # Inverse transformation matrix from printer bed to robot base
    transform_bed_to_base = np.eye(4)
    transform_bed_to_base[:3, :3] = base_orientation
    transform_bed_to_base[:3, 3] = base_position

    # Inverse matrix for transformation
    transform_base_to_bed = np.linalg.inv(transform_bed_to_base)

    transformed_points = []

    for point in points:
        # Extract TCP position in the printer bed frame
        tcp_position_bed = np.array([point["X"], point["Y"], point["Z"], 1.0])

        # Transform to the robot base frame
        tcp_position_base = transform_base_to_bed @ tcp_position_bed

        # Adjust for tool offset
        tool_offset_vector = np.array(
            [tool_offset["X"], tool_offset["Y"], tool_offset["Z"], 1.0]
        )
        flange_position_base = tcp_position_base - tool_offset_vector

        # Round results and ensure Python float type
        transformed_points.append(
            {
                "X": round(float(flange_position_base[0]), acuracy),
                "Y": round(float(flange_position_base[1]), acuracy),
                "Z": round(float(flange_position_base[2]), acuracy),
                "A": round(
                    float(base_pose["A"]), acuracy
                ),  # Assume same orientation for now
                "B": round(float(base_pose["B"]), acuracy),
                "C": round(float(base_pose["C"]), acuracy),
            }
        )

    return transformed_points
