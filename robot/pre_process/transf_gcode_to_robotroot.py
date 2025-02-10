from typing import List, Dict, Union
import numpy as np
from robot.pre_process.mathematical_operators import Rotation, Transformation


def calculate_frame_to_tcp(tool_orientation: Dict[str, float]) -> np.ndarray:
    """
    Calculates the transformation matrix from $FRAME to $TCP.
    """
    R_FRAME_TCP = Rotation.from_euler_angles(
        aX=tool_orientation["C"], aY=tool_orientation["B"], aZ=tool_orientation["A"]
    )
    return Transformation.from_rotation_and_translation(R_FRAME_TCP, [0, 0, 0])


def transform_tool_offset_to_frame(
    tool_offset: Dict[str, float], T_FRAME_TCP: np.ndarray
) -> np.ndarray:
    """
    Transforms the tool offset from $TCP to $FRAME.
    """
    p_nullframe_TCP = [-tool_offset["X"], -tool_offset["Y"], -tool_offset["Z"]]
    return Transformation.apply(T_FRAME_TCP, p_nullframe_TCP)


def calculate_base_to_robotroot(robot_base: Dict[str, float]) -> np.ndarray:
    """
    Calculates the transformation matrix from $BASE to $ROBOTROOT.
    """
    R_BASE_ROBOTROOT = Rotation.from_euler_angles(
        aX=robot_base["C"], aY=robot_base["B"], aZ=robot_base["A"]
    )
    return Transformation.from_rotation_and_translation(
        R_BASE_ROBOTROOT, [robot_base["X"], robot_base["Y"], robot_base["Z"]]
    )


def transform_gcode_point(
    point: Dict[str, Union[str, float, int]],
    tool_orientation: Dict[str, float],
    tool_offset: Dict[str, float],
    robot_base: Dict[str, float],
) -> np.ndarray:
    """
    Transforms a single point from $FRAME to $ROBOTROOT while accounting for tool offset.
    """

    # Step 1: Pre-calculate transformations
    T_FRAME_TCP = calculate_frame_to_tcp(tool_orientation)
    p_nullframe_FRAME = transform_tool_offset_to_frame(tool_offset, T_FRAME_TCP)
    T_BASE_ROBOTROOT = calculate_base_to_robotroot(robot_base)
    T_ROBOTROOT_BASE = np.linalg.inv(T_BASE_ROBOTROOT)

    # Step 2: Transform the point
    # a) transform tool_offset_FRAME to $BASE
    T_BASE_FRAME = Transformation.from_rotation_and_translation(
        np.eye(3), [point["X"], point["Y"], point["Z"]]
    )
    tool_offset_BASE = Transformation.apply(T_BASE_FRAME, p_nullframe_FRAME)

    # b) add tool offset to point to get to p_nullframe_BASE
    p_nullframe_BASE = [point["X"], point["Y"], point["Z"]] + tool_offset_BASE

    # c) transform p_nullframe_BASE to p_nullframe_ROBOTROOT
    p_nullframe_ROBOTROOT = Transformation.apply(T_ROBOTROOT_BASE, p_nullframe_BASE)

    # d) calculate R(ROBOTROOT,NULLFRAME)
    R_ROBOTROOT_BASE = T_BASE_ROBOTROOT[:3, :3].T
    R_ROBOTROOT_NULLFRAME = R_ROBOTROOT_BASE @ T_FRAME_TCP[:3, :3]

    # Resulting transformation
    T_ROBOTROOT_NULLFRAME = Transformation.from_rotation_and_translation(
        R_ROBOTROOT_NULLFRAME, p_nullframe_ROBOTROOT
    )

    # test
    # alpha_ROBOTROOT_NULLFRAME = Rotation.to_euler_angles(
    #     R_ROBOTROOT_NULLFRAME
    # )  # to go from ROBOTROOT to NULLFRAME
    # print(f"alpha_ROBOTROOT_NULLFRAME = {alpha_ROBOTROOT_NULLFRAME}")

    return T_ROBOTROOT_NULLFRAME


if __name__ == "__main__":
    # Example data
    points = [
        {
            "Move": "G0",
            "X": 0,
            "Y": 0,
            "Z": 0,
            "Layer": 0,
            "Type": "TRAVEL",
        }
    ]

    tool_orientation = {"A": 90, "B": 0, "C": 180}
    tool_offset = {"X": 0, "Y": 0, "Z": 50}
    robot_base = {"X": -10, "Y": 10, "Z": 0, "A": 0, "B": 0.0, "C": 0.0}

    # [6.1232340e-17     1.0000000e+00     1.2246468e-16     1.0000000e+01]
    # [1.00000000e+00  - 6.12323400e-17  - 7.49879891e-33  - 1.00000000e+01]
    # [0.0000000e+00     1.2246468e-16   - 1.0000000e+00     5.0000000e+01]
    # [0.                0.                0.                1.]

    nullframes_ROBOTROOT = transform_gcode_points(
        points, tool_orientation, tool_offset, robot_base
    )
    for line in nullframes_ROBOTROOT:
        print(line)
