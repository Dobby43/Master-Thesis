from typing import List, Tuple, Union
import numpy as np


class Translation:
    """
    Handles translation-related operations.
    """

    @staticmethod
    def from_coordinates(x: float, y: float, z: float) -> np.ndarray:
        """
        Creates a 4x4 translation matrix from coordinates.
        """
        matrix = np.eye(4)
        matrix[:3, 3] = [x, y, z]
        return matrix

    @staticmethod
    def to_coordinates(matrix: np.ndarray) -> np.ndarray:
        """
        Extracts translation coordinates [x, y, z] from a 4x4 matrix.
        """
        if matrix.shape != (4, 4):
            raise ValueError("Input matrix must be 4x4.")
        return matrix[:3, 3]


class Rotation:
    """
    Handles rotation-related operations.
    """

    @staticmethod
    def from_euler_angles(
        aX: float, aY: float, aZ: float, order: str = "ZYX"
    ) -> np.ndarray:
        """
        Creates a rotation matrix [3x3] from Euler angles (in degrees).
        Supports custom order.
        """
        aX, aY, aZ = np.radians([aX, aY, aZ])

        # Define basic rotations
        rx = np.array(
            [[1, 0, 0], [0, np.cos(aX), -np.sin(aX)], [0, np.sin(aX), np.cos(aX)]]
        )
        ry = np.array(
            [[np.cos(aY), 0, np.sin(aY)], [0, 1, 0], [-np.sin(aY), 0, np.cos(aY)]]
        )
        rz = np.array(
            [[np.cos(aZ), -np.sin(aZ), 0], [np.sin(aZ), np.cos(aZ), 0], [0, 0, 1]]
        )

        rotations = {"X": rx, "Y": ry, "Z": rz}
        try:
            return np.linalg.multi_dot([rotations[axis] for axis in order])
        except KeyError:
            raise ValueError(f"Unsupported rotation order: {order}")

    @staticmethod
    def to_euler_angles(matrix: np.ndarray, order: str = "ZYX") -> np.ndarray:
        """
        Extracts Euler angles from a rotation matrix.
        """
        if matrix.shape != (3, 3):
            raise ValueError("Input matrix must be 3x3.")

        if order == "ZYX":
            # sy = sqrt(R[0,0]^2 + R[1,0]^2)
            sy = np.sqrt(matrix[0, 0] ** 2 + matrix[1, 0] ** 2)
            singular = sy < 1e-6

            if not singular:
                z = np.arctan2(matrix[1, 0], matrix[0, 0])
                y = np.arctan2(-matrix[2, 0], sy)
                x = np.arctan2(matrix[2, 1], matrix[2, 2])
            else:
                # Gimbal lock case
                z = np.arctan2(-matrix[1, 2], matrix[1, 1])
                y = np.arctan2(-matrix[2, 0], sy)
                x = 0

        elif order == "XYZ":
            # sy = sqrt(R[0,2]^2 + R[1,2]^2)
            sy = np.sqrt(matrix[2, 0] ** 2 + matrix[2, 1] ** 2)
            singular = sy < 1e-6

            if not singular:
                x = np.arctan2(matrix[2, 1], matrix[2, 2])
                y = np.arctan2(-matrix[2, 0], sy)
                z = np.arctan2(matrix[1, 0], matrix[0, 0])
            else:
                # Gimbal lock case
                x = np.arctan2(-matrix[1, 2], matrix[1, 1])
                y = np.arctan2(-matrix[2, 0], sy)
                z = 0
        else:
            raise ValueError(f"Unsupported rotation order: {order}")

        return np.degrees([x, y, z])


class Transformation:
    """
    Handles combined rotation and translation transformations.
    """

    @staticmethod
    def from_rotation_and_translation(
        rotation: np.ndarray, translation: Union[np.ndarray, List[float]]
    ) -> np.ndarray:
        """
        Combines rotation and translation into a 4x4 transformation matrix.
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
        Extracts rotation and translation from a 4x4 transformation matrix.
        """
        if matrix.shape != (4, 4):
            raise ValueError("Input matrix must be 4x4.")
        rotation = matrix[:3, :3]
        translation = matrix[:3, 3]
        return rotation, translation

    @staticmethod
    def invert(matrix: np.ndarray) -> np.ndarray:
        """
        Inverts a 4x4 transformation matrix.
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
        Applies a transformation matrix to a point or vector.
        """
        if len(point) != 3:
            raise ValueError("Point must be a 3-element vector.")
        point_homogeneous = np.append(point, 1.0)
        transformed = matrix @ point_homogeneous
        return transformed[:3]


if __name__ == "__main__":
    # Example usage

    # Define rotation and translation
    rotation = Rotation.from_euler_angles(0, 0, 90)
    translation = [10, 0, 0]

    # Create transformation matrix
    transform = Transformation.from_rotation_and_translation(rotation, translation)
    print("Transformation Matrix:")
    print(transform)

    # Apply transformation to a point
    point = [5, -5, 0]
    transformed_point = Transformation.apply(transform, point)
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
