import numpy as np
from robot.process import kinematics as rokin


if __name__ == "__main__":
    matrix = np.array(
        [
            [-0.384305, 0.890495, 0.243575, -100.972036],
            [0.895798, 0.423493, -0.134903, 279.190877],
            [-0.223282, 0.166350, -0.960454, 2418.305151],
            [0.000000, 0.000000, 0.000000, 1.000000],
        ]
    )

    KL_1 = np.array(
        [
            [6.55695185e-01, -1.66233737e-01, 7.36498587e-01, -1.14083006e02],
            [1.41446329e-01, 9.85236373e-01, 9.64480428e-02, -9.41779640e01],
            [-7.41658116e-01, 4.09345045e-02, 6.69527898e-01, 2.91774768e03],
            [0.00000000e00, 0.00000000e00, 0.00000000e00, 1.00000000e00],
        ]
    )

    """Erstellt eine Roboterinstanz mit festen Parametern."""
    robot_geometry = {
        "a1": 500,
        "a2": 55,
        "b": 0,
        "c1": 1045,
        "c2": 1300,
        "c3": 1525,
        "c4": 290,
    }
    robot_rotation_sign = {"A1": -1, "A2": 1, "A3": 1, "A4": -1, "A5": 1, "A6": -1}
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

    robot = rokin.RobotOPW(
        robot_id="ExampleRobot",
        robot_base_radius=0,
        robot_geometry=robot_geometry,
        robot_rotation_sign=robot_rotation_sign,
        robot_rotation_limit=robot_rotation_limit,
        robot_rotation_offset=robot_rotation_offset,
        robot_tool_offset=tool_offset,
    )

    sol = robot.inverse_kinematics(KL_1)
    for line in sol:
        print(line)
