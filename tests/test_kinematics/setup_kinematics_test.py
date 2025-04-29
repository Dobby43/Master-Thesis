import json
import os
import numpy as np
from robot import kinematics as rokin


def load_robot():
    """
    DESCRIPTION:
    Builds robot matching the robot used for generating teh test cases under tests.test_kinematics.kinematics_test_cases
    See robot.kinematics for necessary input
    """
    robot_geometry = {
        "a1": 500,
        "a2": 55,
        "b": 0,
        "c1": 1045,
        "c2": 1300,
        "c3": 1525,
        "c4": 290,
    }
    robot_rotation_sign = {
        "A1": False,
        "A2": True,
        "A3": True,
        "A4": False,
        "A5": True,
        "A6": False,
    }
    robot_rotation_limit = {
        "A1": [-185, 185],
        "A2": [-130, 20],
        "A3": [-100, 140],
        "A4": [-350, 350],
        "A5": [-120, 120],
        "A6": [-350, 350],
    }
    robot_rotation_offset = {"A1": 0, "A2": -90, "A3": 0, "A4": 0, "A5": 0, "A6": 0}

    tool_offset = {"X": 0, "Y": 0, "Z": 0}

    return rokin.RobotOPW(
        robot_id="ExampleRobot",
        robot_base_radius=0,
        robot_geometry=robot_geometry,
        robot_rotation_sign=robot_rotation_sign,
        robot_rotation_limit=robot_rotation_limit,
        robot_rotation_offset=robot_rotation_offset,
        robot_tool_offset=tool_offset,
    )


def load_json_file(file_path: json) -> dict:
    """
    DESCRIPTION:
    Loads a JSON file from the given file path and returns its content as a dictionary.

    :param file_path: path to the JSON file to be loaded

    :return: dictionary containing the data parsed from the JSON file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"[ERROR] File not found in {file_path}")

    with open(file_path, "r") as f:
        data = json.load(f)
        print(file_path)

    return data


def extract_ik_solutions(data: dict) -> list[dict]:
    """
    DESCRIPTION:
    Extracts inverse kinematic solutions (stored under key "J") from a given dictionary.
    Returns a list of dictionaries, one for each solution.

    :param data: dictionary containing the inverse kinematic data with keys "J" and "n"

    :return: list of dictionaries containing joint angle solutions for each configuration
    """
    if "J" not in data or not isinstance(data["J"], list) or len(data["J"]) == 0:
        print(f"[ERROR] file has no solutions for inverse kinematics")
        return []

    num_solutions = data.get("n", 0)

    if num_solutions == 0 or len(data["J"]) == 0 or len(data["J"][0]) == 0:
        print(f"[WARNING] Inverse kinematic solution for given point has length == 0")
        return []

    ik_solutions = [{} for _ in range(num_solutions)]

    for joint_idx, joint_values in enumerate(data["J"]):
        if len(joint_values) != num_solutions:
            print(
                f"[WARNING] Number of solutions fro inverse kinematic {joint_idx + 1} doesn't match test case"
            )
            return []

        for sol_idx in range(num_solutions):
            ik_solutions[sol_idx][f"A{joint_idx + 1}.{sol_idx + 1}"] = float(
                joint_values[sol_idx]
            )

    return ik_solutions


def extract_fk_matrix(data: dict) -> np.array:
    """
    DESCRIPTION:
    Extracts the forward kinematic transformation matrix (stored under key "F") from a given dictionary.

    :param data: dictionary containing the forward kinematic data under the key "F"

    :return: NumPy array representing the forward kinematic transformation matrix
    """

    return np.array(data["F"])
