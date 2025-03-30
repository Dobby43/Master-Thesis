import pytest
import os
from pathlib import Path
from tests.test_kinematics import setup_kinematics_test as roset


# Directory with all test data
BASE_DIR = str(Path(__file__).parent / "kinematics_test_cases")

tolerance_ik_deg = 0.02  # tolerance for ik
tolerance_fk_mm = 0.00  # tolerance for fk


@pytest.fixture(scope="session")
def robot():
    """
    DESCRIPTION:
    Fixture for initialisation of robot class (done once for all tests in this session)
    """
    return roset.load_robot()


@pytest.fixture(
    params=[
        os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if f.endswith(".json")
    ]
)
def test_data(request):
    """
    DESCRIPTION:
    Loads a single test case
    """
    return roset.load_json_file(request.param)


def test_forward_kinematics(robot, test_data):
    """
    DESCRIPTION:
    tests, if the forward kinematics function is working and calculates the expected position
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

    # Calculating the forward kinematik for robot setup
    fk_matrix, reachable = robot.forward_kinematics(joint_angles)  # unpacks tuple

    if not reachable:
        print(
            "[WARNING] Given position is outside of working radius or leads to self-collision"
        )
        return

    # Extracting calculated position
    calculated_position = fk_matrix[:3, 3]

    # Comparrison between calculated and expected position
    diff_x = abs(calculated_position[0] - expected_x)
    diff_y = abs(calculated_position[1] - expected_y)
    diff_z = abs(calculated_position[2] - expected_z)

    # Check if difference is within tolerance
    assert diff_x < tolerance_fk_mm, f"X-Fehler zu groß: {diff_x} mm"
    assert diff_y < tolerance_fk_mm, f"Y-Fehler zu groß: {diff_y} mm"
    assert diff_z < tolerance_fk_mm, f"Z-Fehler zu groß: {diff_z} mm"

    print(
        f"Forward Kinematics Test successfully! | ΔX: {diff_x:.3f} mm, ΔY: {diff_y:.3f} mm, ΔZ: {diff_z:.3f} mm"
    )


def test_inverse_kinematics(robot, test_data):
    """
    DESCRIPTION:
    Checks if the calculated solution has a line matching with the expected solutions from .json
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
