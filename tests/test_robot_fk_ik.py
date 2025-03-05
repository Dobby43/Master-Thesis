import numpy as np

import os
import json

from robot.process import kinematics as robki


def load_test_data(test_case_path):
    """Lädt die FK- und IK-Testdaten aus einer JSON-Datei."""
    test_file = os.path.join(test_case_path, "ik_data.json")  # Datei mit FK & IK-Daten

    if not os.path.exists(test_file):
        print(f"❌ Datei nicht gefunden: {test_file}")
        return None, None

    with open(test_file, "r") as f:
        test_data = json.load(f)

    # FK-Matrix aus der Datei extrahieren
    fk_matrix_expected = np.array(test_data["F"])

    # IK-Lösungen extrahieren (Liste von Listen), transponieren für richtige Form
    ik_solutions_expected = np.array(test_data["J"]).T if "J" in test_data else None

    return fk_matrix_expected, ik_solutions_expected


def compare_solutions(ik_computed, ik_expected, atol=0.01):
    """Vergleicht die berechneten IK-Winkel mit den gespeicherten Lösungen."""
    for computed_solution in ik_computed:
        computed_values = np.array(
            [computed_solution[f"A{i+1}.{j+1}"] for i in range(6)]
            for j in range(len(computed_solution))
        )

        for expected_solution in ik_expected:
            if np.allclose(
                computed_values, expected_solution, atol=atol
            ):  # Toleranz in Grad
                return True  # IK erfolgreich
    return False  # Keine Übereinstimmung gefunden


def test_inverse_kinematics(robot, fk_matrix_expected, ik_solutions_expected):
    """Testet die Inverse Kinematik für eine FK-Matrix."""
    ik_solutions_computed = robot.inverse_kinematics(fk_matrix_expected)

    if not ik_solutions_computed:
        return False  # IK hat keine Lösungen gefunden

    return compare_solutions(ik_solutions_computed, ik_solutions_expected)


def test_forward_kinematics(robot, ik_solutions_computed, fk_matrix_expected):
    """Testet die Forward Kinematik für eine der IK-Lösungen."""
    for ik_solution in ik_solutions_computed:
        joint_angles = {
            "A1": ik_solution["A1.1"],
            "A2": ik_solution["A2.1"],
            "A3": ik_solution["A3.1"],
            "A4": ik_solution["A4.1"],
            "A5": ik_solution["A5.1"],
            "A6": ik_solution["A6.1"],
        }
        fk_matrix_computed, reachable = robot.forward_kinematics(joint_angles)

        if not reachable:
            continue  # Falls Lösung nicht erreichbar ist, nächste testen

        if np.allclose(
            fk_matrix_computed, fk_matrix_expected, atol=0.1
        ):  # Toleranz in mm
            return True  # FK erfolgreich

    return False  # Keine Übereinstimmung gefunden


def run_kinematics_tests(robot, base_path):
    """Führt die Tests für alle Testfälle durch und speichert die Fehler."""
    test_cases = [
        os.path.join(base_path, folder)
        for folder in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, folder))
    ]

    ik_success = 0
    fk_success = 0
    failed_cases = []

    for test_case in test_cases:
        fk_matrix_expected, ik_solutions_expected = load_test_data(test_case)

        if fk_matrix_expected is None or ik_solutions_expected is None:
            print(f"⚠️  Testfall übersprungen (fehlende Daten): {test_case}")
            continue

        # Inverse Kinematik testen
        ik_passed = test_inverse_kinematics(
            robot, fk_matrix_expected, ik_solutions_expected
        )

        if ik_passed:
            ik_success += 1

            # Forward Kinematik testen
            fk_passed = test_forward_kinematics(
                robot, robot.inverse_kinematics(fk_matrix_expected), fk_matrix_expected
            )
            if fk_passed:
                fk_success += 1
            else:
                failed_cases.append({"test_case": test_case, "error": "FK failed"})
        else:
            failed_cases.append({"test_case": test_case, "error": "IK failed"})

    # Testergebnisse ausgeben
    print(
        f"✅ Inverse Kinematik erfolgreich: {ik_success}/{len(test_cases)} ({(ik_success / len(test_cases)) * 100:.2f}%)"
    )
    print(
        f"✅ Forward Kinematik erfolgreich: {fk_success}/{ik_success} ({(fk_success / ik_success) * 100:.2f}%)"
    )

    # Fehlerfälle speichern
    with open("failed_cases.json", "w") as f:
        json.dump(failed_cases, f, indent=4)

    print("❗ Fehlerfälle wurden in 'failed_cases.json' gespeichert.")


# 🚀 Testpipeline starten
base_path = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\Daniel\inversekinematic_testcases\Desktop\ik_solutions"

# Robot initialisieren
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
    "A3": [-100, 144],
    "A4": [-350, 350],
    "A5": [-120, 120],
    "A6": [-350, 350],
}
robot_rotation_offset = {"A1": 0, "A2": -90, "A3": 0, "A4": 0, "A5": 0, "A6": 0}
tool_offset = {"X": 0, "Y": 0, "Z": 0}

robot = robki.RobotOPW(
    robot_id="ExampleRobot",
    robot_geometry=robot_geometry,
    robot_rotation_sign=robot_rotation_sign,
    robot_rotation_limit=robot_rotation_limit,
    robot_rotation_offset=robot_rotation_offset,
    robot_tool_offset=tool_offset,
)

run_kinematics_tests(robot, base_path)


# if __name__ == '__main__':
#
# point_1 = {"ROBOT": "KUKA KR 340 R3300", "TOOL": "$NULLFRAME", "BASE": "$ROBROOT",
#         "X": 0.6088391929241084,"Y": 2.6846348824018946, "Z": 31.290347683766527,
#         "A": 30.441401115936216, "B": -62.00910928221709,"C": -136.7808211062857,
#         "F": [[0.40463283994240906, 0.8905493225446717, 0.20783206912160435, 0.6088391929241084],
#               [0.23778986747186387, -0.32191291729843946, 0.9164213291953225, 2.6846348824018946],
#               [0.8830222215594884, -0.32139380484327107, -0.342020143325669, 31.290347683766527],
#               [0.0, 0.0, 0.0, 1.0]],
#         "n": 0, "J": [], "FR": [], "UD": [], "FN": []}
#
# point_2 = {"ROBOT": "KUKA KR 340 R3300", "TOOL": "$NULLFRAME", "BASE": "$ROBROOT",
#            "X": 10.644879149104707, "Y": 150.246332513739, "Z": 3612.7201611815035, "A": 163.38154143409318, "B": 72.87704301322559, "C": 68.43102711976228,
#            "F": [[-0.282125347515918, -0.9567703274361139, -0.07068117731627033, 10.644879149104707],
#                  [0.08420419626163103, -0.09808441136443852, 0.9916093492798586, 150.246332513739],
#                  [-0.9556751234708138, 0.273806480538871, 0.108236175070822, 3612.7201611815035],
#                  [0.0, 0.0, 0.0, 1.0]],
#            "n": 20,
#            "J": [[77.22222222222226, 77.22222222222226, 77.22222222222226, 77.22222222222226, -102.77777777777776, -102.77777777777776, 77.22222222222226, 77.22222222222226, 77.22222222222226, -102.77777777777776, 77.22222222222226, 77.22222222222226, 77.22222222222226, 77.22222222222226, -102.77777777777776, -102.77777777777776, 77.22222222222226, 77.22222222222226, 77.22222222222226, -102.77777777777776],
#                  [-125.26807976938912, -70.85304891002477, -125.26807976938912, -125.26807976938912, -128.35825107001943, -128.35825107001943, -70.85304891002477, -70.85304891002477, -125.26807976938912, -128.35825107001943, -70.85304891002477, -70.85304891002477, -125.26807976938912, -70.85304891002477, -128.35825107001943, -128.35825107001943, -70.85304891002477, -70.85304891002477, -125.26807976938912, -128.35825107001943],
#                  [48.06561232710494, -52.19663216571105, 48.06561232710494, 48.06561232710494, 42.535646828061466, 42.535646828061466, -52.19663216571105, -52.19663216571105, 48.06561232710494, 42.535646828061466, -52.19663216571105, -52.19663216571105, 48.06561232710494, -52.19663216571105, 42.535646828061466, 42.535646828061466, -52.19663216571105, -52.19663216571105, 48.06561232710494, 42.535646828061466],
#                  [8.70447535863854, 11.126272143809656, -171.29552464136145, 8.70447535863854, 8.793139428595119, -171.20686057140486, 191.12627214380964, -348.8737278561903, 188.70447535863855, 188.79313942859514, -168.87372785619036, 11.126272143809656, -171.29552464136145, -168.87372785619036, 8.793139428595119, -171.20686057140486, 191.12627214380964, -348.8737278561903, 188.70447535863855, 188.79313942859514],
#                  [-96.43774818791523, -51.1968738991188, 96.43774818791523, -96.43774818791523, 79.65749612341864, -79.65749612341864, 51.1968738991188, -51.1968738991188, 96.43774818791523, -79.65749612341864, 51.1968738991188, -51.1968738991188, 96.43774818791523, 51.1968738991188, 79.65749612341864, -79.65749612341864, 51.1968738991188, -51.1968738991188, 96.43774818791523, -79.65749612341864],
#                  [-194.05490940958492, 157.9358380518892, -14.054909409584923, 165.94509059041508, -16.62912197503028, 163.37087802496973, -22.064161948110836, 157.9358380518892, -14.054909409584923, 163.37087802496973, 337.93583805188916, -202.0641619481108, 345.9450905904151, -22.064161948110836, 343.3708780249697, -196.62912197503027, 337.93583805188916, -202.0641619481108, 345.9450905904151, -196.62912197503027]],
#            "FR": [0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1], "UD": [0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0], "FN": [1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1]}
