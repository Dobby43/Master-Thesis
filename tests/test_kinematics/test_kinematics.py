import pytest
import os
from pathlib import Path

from robot.mathematical_operators import Rotation
from tests.test_kinematics import setup_kinematics_test as roset


# Directory with all test data
BASE_DIR = str(Path(__file__).parent / "kinematics_test_cases")

tolerance_ik_deg = 0.02  # tolerance for ik
tolerance_fk_mm = 0.01  # positional tolerance for fk
tolerance_fk_deg = 0.01  # rotational tolerance for fk


@pytest.fixture(scope="session")
def robot():
    """
    DESCRIPTION:
    Fixture for initializing the robot class. Runs once for the entire test session.

    :return: instance of the loaded robot class
    """
    return roset.load_robot()


@pytest.fixture(
    params=[
        os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if f.endswith(".json")
    ]
)
def test_data(request) -> dict:
    """
    DESCRIPTION:
    Loads a single test case from the provided request parameter.

    :param request: fixture parameter containing the path to the JSON file
    :return: dictionary containing the loaded test case data
    """
    return roset.load_json_file(request.param)


def test_forward_kinematics(robot, test_data: dict) -> None:
    """
    DESCRIPTION:
    Tests if the forward kinematics function of the robot correctly calculates the expected position and orientation.

    :param robot: instance of the robot class used for kinematic calculations
    :param test_data: dictionary containing the joint angles and the expected position and orientation from the test case

    :return: None
    """

    # Extracts the joint angles from .json
    if "J" not in test_data or len(test_data["J"]) < 6:
        raise ValueError("[ERROR] No joint angles given in .json data")

    # converts the first solution inside the .json file into a dictionary
    joint_angles = {f"A{i+1}": test_data["J"][i][0] for i in range(6)}

    # Extracts the expected position for given joint angles from json
    expected_x = test_data["X"]
    expected_y = test_data["Y"]
    expected_z = test_data["Z"]

    expected_a = test_data["A"]
    expected_b = test_data["B"]
    expected_c = test_data["C"]

    # Calculating the forward kinematik for robot setup
    fk_matrix, reachable = robot.forward_kinematics(joint_angles)  # unpacks tuple

    if not reachable:
        print(
            "[WARNING] Given position is outside of working radius or leads to self-collision"
        )
        return

    # Extracting calculated position
    calculated_position = fk_matrix[:3, 3]
    calculated_orientation = fk_matrix[:3, :3]

    calculated_angles = Rotation.to_euler_angles(calculated_orientation)

    print(
        f"solution calculated: X: {calculated_position[0]}, Y: {calculated_position[1]}, Z: {calculated_position[2]}, A: {calculated_angles[0]}, B: {calculated_angles[1]}, C: {calculated_angles[2]}"
    )
    # Comparison between calculated and expected position
    diff_x = abs(calculated_position[0] - expected_x)
    diff_y = abs(calculated_position[1] - expected_y)
    diff_z = abs(calculated_position[2] - expected_z)

    diff_a = (abs(calculated_angles[0] - expected_a) + 180) % 360 - 180
    diff_b = (abs(calculated_angles[1] - expected_b) + 180) % 360 - 180
    diff_c = (abs(calculated_angles[2] - expected_c) + 180) % 360 - 180

    # Check if difference is within tolerance
    assert diff_x < tolerance_fk_mm, f"X-Fehler zu groß: {diff_x} mm"
    assert diff_y < tolerance_fk_mm, f"Y-Fehler zu groß: {diff_y} mm"
    assert diff_z < tolerance_fk_mm, f"Z-Fehler zu groß: {diff_z} mm"
    assert diff_a < tolerance_fk_deg, f"A-Fehler zu groß: {diff_a} deg"
    assert diff_b < tolerance_fk_deg, f"B-Fehler zu groß: {diff_b} deg"
    assert diff_c < tolerance_fk_deg, f"C-Fehler zu groß: {diff_c} deg"

    print(
        f"Forward Kinematics Test successfully! | ΔX: {diff_x:.3f} mm, ΔY: {diff_y:.3f} mm, ΔZ: {diff_z:.3f} mm, ΔA: {diff_a:.3f} deg, ΔB: {diff_x:.3f} deg, ΔC: {diff_x:.3f} deg"
    )


def test_inverse_kinematics(robot, test_data: dict) -> None:
    """
    DESCRIPTION:
    Checks if the calculated inverse kinematics solutions match the expected solutions defined in the test case.

    :param robot: instance of the robot class used for inverse kinematic calculations
    :param test_data: dictionary containing the forward kinematic matrix and expected inverse kinematic solutions

    :return: None
    """

    # Load homogeneous transformation matrix from json
    fk_matrix = roset.extract_fk_matrix(test_data)

    # Extracting the expected solutions from .json
    ik_solutions_raw = test_data.get("J", [])
    num_expected_solutions = test_data.get("n")  # number of expected solutions

    # Check if no solutions are expected, no solutions are found
    if num_expected_solutions == 0:
        assert (
            len(ik_solutions_raw) == 0
        ), f"No solution expected, but {len(ik_solutions_raw)} solutions found"
        print(
            f"Test successfully! No solutions expected and {len(ik_solutions_raw)} solutions found"
        )
        return

    # Rearrange expected solutions to match shape of calculated solutions
    ik_solutions_expected = [
        {f"A{i + 1}": ik_solutions_raw[i][j] for i in range(6)}
        for j in range(num_expected_solutions)
    ]

    print(f"solutions expected\n")
    for line in ik_solutions_expected:
        print(line)

    # Calculate solutions for given homogeneous transformation matrix
    ik_solutions_calculated = robot.inverse_kinematics(fk_matrix)
    num_calculated_solutions = len(
        ik_solutions_calculated
    )  # Get number of calculated solutions

    print("solutions calculated\n")
    for line in ik_solutions_calculated:
        print(line)

    # If no solution was calculated, but solutions are expected
    assert (
        num_calculated_solutions > 0
    ), f"Calculation of IK for given point ({fk_matrix[0,3]}, {fk_matrix[1,3]}, {fk_matrix[2,3]}) lead to no solution, but {num_expected_solutions} solutions are expected"

    # Keep track of validated solutions
    validated_solutions = []

    for i, calculated_solution in enumerate(ik_solutions_calculated, start=1):
        for j, expected_solution in enumerate(ik_solutions_expected, start=1):
            if all(
                abs(
                    calculated_solution[f"A{k + 1}.{i}"]
                    - expected_solution[f"A{k + 1}"]
                )
                < tolerance_ik_deg
                for k in range(6)
            ):
                validated_solutions.append(calculated_solution)
                break  # Interrupt if valid solution is found in expected solution

    # Checks if number of validated solutions matches expected
    assert (
        len(validated_solutions) > 0
    ), f"No calculated solution within given tolerance, allthough solutions are expected"
    assert (
        len(validated_solutions) <= num_expected_solutions
    ), f"Number of calculated solutions ({len(validated_solutions)} > {num_expected_solutions})!"

    print(
        f"Test successfully! Number of validated solutions: {len(validated_solutions)}"
    )
