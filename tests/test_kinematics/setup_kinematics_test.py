import json
import os
import numpy as np
from robot.process import kinematics_2 as rokin  # Importiere die Roboterklasse


def load_robot():
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

    return rokin.RobotOPW(
        robot_id="ExampleRobot",
        robot_base_radius=0,
        robot_geometry=robot_geometry,
        robot_rotation_sign=robot_rotation_sign,
        robot_rotation_limit=robot_rotation_limit,
        robot_rotation_offset=robot_rotation_offset,
        robot_tool_offset=tool_offset,
    )


def load_json_file(file_path):
    """Liest die JSON-Datei und gibt die enthaltenen Daten zurück."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Datei {file_path} nicht gefunden!")

    with open(file_path, "r") as f:
        data = json.load(f)
        print(file_path)

    return data


def extract_ik_solutions(data):
    """Extrahiert die IK-Lösungen aus der JSON-Datei."""
    if "J" not in data or not isinstance(data["J"], list) or len(data["J"]) == 0:
        print(f"⚠ Warnung: Datei enthält keine gültigen IK-Lösungen!")
        return []

    # Stelle sicher, dass mindestens eine Lösung existiert
    num_solutions = data.get("n", 0)

    if num_solutions == 0 or len(data["J"]) == 0 or len(data["J"][0]) == 0:
        print(f"⚠ Warnung: Keine gültigen IK-Lösungen (`n=0`).")
        return []

    ik_solutions = [{} for _ in range(num_solutions)]

    for joint_idx, joint_values in enumerate(data["J"]):
        if len(joint_values) != num_solutions:
            print(
                f"⚠ Warnung: Gelenkwinkelanzahl für A{joint_idx + 1} stimmt nicht überein!"
            )
            return []

        for sol_idx in range(num_solutions):
            ik_solutions[sol_idx][f"A{joint_idx + 1}.{sol_idx + 1}"] = float(
                joint_values[sol_idx]
            )

    return ik_solutions


def extract_fk_matrix(data):
    """Lädt die homogene Transformationsmatrix aus der JSON-Datei."""
    return np.array(data["F"])
