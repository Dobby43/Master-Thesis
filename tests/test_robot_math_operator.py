import numpy as np
from robot.pre_calculation.mathematical_operators import (
    Transformation,
    Rotation,
    Translation,
)


def test_identity_transformation():
    # Identity matrix should not change a point
    identity_matrix = np.eye(4)
    point = np.array([1.0, 2.0, 3.0])
    transformed_point = Transformation.apply(identity_matrix, point)
    np.testing.assert_array_almost_equal(transformed_point, point, decimal=6)


def test_translation():
    # Test a pure translation
    translation_vector = [10.0, 20.0, 30.0]  # from old to new frame -> T(old,new)
    translation_matrix = Translation.from_coordinates(
        translation_vector[0], translation_vector[1], translation_vector[2]
    )

    point = np.array([1.0, 2.0, 3.0])  # in new frame p(new)
    transformed_point = Transformation.apply(translation_matrix, point)
    expected_point = np.array([11.0, 22.0, 33.0])  # in old frame p(old)
    np.testing.assert_array_almost_equal(transformed_point, expected_point, decimal=6)


def test_rotation_z_180():
    # Test rotation of 90 degrees around X-axis
    rotation_matrix = Rotation.from_euler_angles(
        0, 0, 180
    )  # from old to new frame -> R(old,new)
    point = np.array([1.0, 0.0, 0.0])  # in new frame p(new)
    transformed_point = Transformation.apply(
        Transformation.from_rotation_and_translation(rotation_matrix, [0.0, 0.0, 0.0]),
        point,
    )
    expected_point = np.array([-1.0, 0.0, 0.0])  # in old frame p(old)
    np.testing.assert_array_almost_equal(transformed_point, expected_point, decimal=6)


def test_combined_transformation():
    # Test combination of translation and rotation
    rotation_matrix = Rotation.from_euler_angles(
        90, 0, 0
    )  # from old to new frame -> R(old,new)
    translation_vector = [5.0, 0.0, 0.0]  # from old to new frame-> T(old,new)
    transformation_matrix = Transformation.from_rotation_and_translation(
        rotation_matrix, translation_vector
    )
    point = np.array([1.0, 0.0, 0.0])  # in new frame p(new)
    transformed_point = Transformation.apply(transformation_matrix, point)
    expected_point = np.array([6.0, 0.0, 0.0])  # Rotated and translated p(old)
    np.testing.assert_array_almost_equal(transformed_point, expected_point, decimal=6)


def test_inversion():
    # Test inversion of a transformation
    rotation_matrix = Rotation.from_euler_angles(
        90, 0, 90
    )  # from old to new frame -> R(old,new)
    translation_vector = [5.0, 0.0, 0.0]  # from old to new frame
    transformation_matrix = Transformation.from_rotation_and_translation(
        rotation_matrix, translation_vector
    )  # T(old,new)
    inverted_matrix = Transformation.invert(transformation_matrix)  # T(new,old)

    point = np.array([6, 0, 0])  # in old frame p(old)
    transformed_point = Transformation.apply(inverted_matrix, point)
    expected_point = np.array([0, 0, 1.0])
    np.testing.assert_array_almost_equal(transformed_point, expected_point, decimal=6)
