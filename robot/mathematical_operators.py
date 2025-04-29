from typing import List, Tuple, Union
import numpy as np


class Translation:
    """
    DESCRIPTION:
    Handles translation-related operations.
    """

    @staticmethod
    def from_coordinates(x: float, y: float, z: float) -> np.ndarray:
        """
        DESCRIPTION:
        Creates a 4x4 translation matrix from coordinates.

        :param x: translation in x direction
        :param y: translation in y direction
        :param z: translation in z direction

        :return: 4x4 homogeneous transformation matrix with pure translation
        """
        matrix = np.eye(4)
        matrix[:3, 3] = [x, y, z]
        return matrix

    @staticmethod
    def to_coordinates(matrix: np.ndarray) -> np.ndarray:
        """
        DESCRIPTION:
        Extracts translation coordinates [x, y, z] from a 4x4 matrix.

        :param matrix: 4x4 homogeneous transformation matrix
        """
        if matrix.shape != (4, 4):
            raise ValueError("Input matrix must be 4x4.")
        return matrix[:3, 3]


class Rotation:
    """
    DESCRIPTION:
    Handles rotation-related operations.
    """

    @staticmethod
    def from_euler_angles(
        ax: float, ay: float, az: float, order: str = "ZYX"
    ) -> np.ndarray:
        """
        DESCRIPTION:
        Creates a rotation matrix [3x3] from Euler angles (in degrees).
        Supports custom order.

        :param ax: rotation in x direction in degrees
        :param ay: rotation in y direction in degrees
        :param az: rotation in z direction in degrees
        :param order: rotation order (only combinations of XYZ possible)

        :return: 3x3 rotation matrix
        """
        ax, ay, az = np.radians([ax, ay, az])

        # Define basic rotations
        rx = np.array(
            [[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]]
        )
        ry = np.array(
            [[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]]
        )
        rz = np.array(
            [[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]]
        )

        rotations = {"X": rx, "Y": ry, "Z": rz}
        try:
            return np.linalg.multi_dot([rotations[axis] for axis in order])
        except KeyError:
            raise ValueError(f"Unsupported rotation order: {order}")

    @staticmethod
    def to_euler_angles(matrix: np.ndarray, order: str = "ZYX") -> np.ndarray:
        """
        DESCRIPTION:
        Extracts Euler angles [rad] from a rotation matrix.

        :param matrix: 4x4 homogeneous transformation matrix
        :param order: rotation order (only XYZ, ZYX, ZYZ possible)

        :return: angles in degree
        """
        if matrix.shape != (3, 3):
            raise ValueError("Input matrix must be 3x3.")

        if order == "ZYX":
            # sy = sqrt(R[0,0]^2 + R[1,0]^2)
            sy = np.sqrt(matrix[0, 0] ** 2 + matrix[1, 0] ** 2)
            singular = sy < 1e-6

            if not singular:
                a = np.arctan2(matrix[1, 0], matrix[0, 0])
                b = np.arctan2(-matrix[2, 0], sy)
                c = np.arctan2(matrix[2, 1], matrix[2, 2])
            else:
                # Gimbal lock case
                a = np.arctan2(-matrix[1, 2], matrix[1, 1])
                b = np.arctan2(-matrix[2, 0], sy)
                c = 0

        elif order == "XYZ":
            # sy = sqrt(R[0,2]^2 + R[1,2]^2) [length of projection of z axis on xy plane]
            sy = np.sqrt(matrix[2, 0] ** 2 + matrix[2, 1] ** 2)
            singular = sy < 1e-6

            if not singular:
                a = np.arctan2(matrix[2, 1], matrix[2, 2])
                b = np.arctan2(
                    -matrix[2, 0], sy
                )  # due to unambiguous angle identification not arcsin(-[0,2])
                c = np.arctan2(matrix[1, 0], matrix[0, 0])
            else:
                # Gimbal lock case
                a = np.arctan2(-matrix[1, 2], matrix[1, 1])
                b = np.arctan2(-matrix[2, 0], sy)
                c = 0

        elif order == "ZYZ":
            sy = np.sqrt(matrix[0, 2] ** 2 + matrix[1, 2] ** 2)
            singular = sy < 1e-6
            if not singular:
                a = np.arctan2(matrix[1, 2], matrix[0, 2])
                b = np.arctan2(sy, matrix[2, 2])
                c = np.arctan2(matrix[2, 1], -matrix[2, 0])
            else:

                a = np.arctan2(matrix[1, 0], matrix[0, 0])
                b = np.arctan2(sy, matrix[2, 2])
                c = 0
        else:
            raise ValueError(f"Unsupported rotation order: {order}")

        return np.degrees([a, b, c])


class Transformation:
    """
    DESCRIPTION:
    Handles combined rotation and translation transformations.
    """

    @staticmethod
    def from_rotation_and_translation(
        rotation: np.ndarray, translation: Union[np.ndarray, List[float]]
    ) -> np.ndarray:
        """
        DESCRIPTION:
        Combines rotation and translation into a 4x4 transformation matrix.

        :param rotation: 3x3 rotation matrix
        :param translation: translation vector 1x3

        :return: 4x4 homogeneous transformation matrix
        """
        if rotation.shape != (3, 3):
            raise ValueError("Rotation must be a 3x3 matrix.")
        if len(translation) != 3:
            raise ValueError("Translation must be a 3-element vector.")
        matrix = np.eye(4)
        matrix[:3, :3] = rotation
        matrix[:3, 3] = translation
        return matrix

    @staticmethod
    def to_rotation_and_translation(
        matrix: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        DESCRIPTION:
        Extracts rotation and translation from a 4x4 transformation matrix.

        :param matrix: 4x4 homogeneous transformation matrix

        :return: tupel of 3x3 rotation matrix and 3x1 translation vector
        """
        if matrix.shape != (4, 4):
            raise ValueError("Input matrix must be 4x4.")
        rotation = matrix[:3, :3]
        translation = matrix[:3, 3]
        return rotation, translation

    @staticmethod
    def invert(matrix: np.ndarray) -> np.ndarray:
        """
        DESCRIPTION:
        Inverts a 4x4 transformation matrix.

        :param matrix: 4x4 homogeneous transformation matrix

        :return: inverted 4x4 homogeneous transformation matrix
        """
        if matrix.shape != (4, 4):
            raise ValueError("Input matrix must be 4x4.")
        rotation = matrix[:3, :3]
        translation = matrix[:3, 3]

        inverted = np.eye(4)
        inverted[:3, :3] = rotation.T
        inverted[:3, 3] = -rotation.T @ translation
        return inverted

    @staticmethod
    def apply(matrix: np.ndarray, point: Union[np.ndarray, list[float]]) -> np.ndarray:
        """
        DESCRIPTION:
        Applies a transformation matrix to a point or vector.

        :param matrix: 4x4 homogeneous transformation matrix
        :param point: point or vector

        :return: transformed 3x1 vector or point
        """
        if len(point) != 3:
            raise ValueError("Point must be a 3-element vector.")
        point_homogeneous = np.append(point, 1.0)
        transformed = matrix @ point_homogeneous
        return transformed[:3]


if __name__ == "__main__":
    # Example usage

    # Define rotation and translation
    rotate = Rotation.from_euler_angles(0, 0, 90)
    translate = [10, 0, 0]

    # Create transformation matrix
    transform = Transformation.from_rotation_and_translation(rotate, translate)
    print("Transformation Matrix:")
    print(transform)

    # Apply transformation to a point
    p = [5, -5, 0]
    transformed_point = Transformation.apply(transform, p)
    print("Transformed Point:", transformed_point)

    # Invert transformation
    inverted_transform = Transformation.invert(transform)
    print("Inverted Transformation Matrix:")
    print(inverted_transform)

    # Extract rotation and translation
    extracted_rotation, extracted_translation = (
        Transformation.to_rotation_and_translation(transform)
    )
    print("Extracted Rotation:")
    print(extracted_rotation)
    print("Extracted Translation:")
    print(extracted_translation)
