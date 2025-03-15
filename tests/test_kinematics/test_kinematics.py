import pytest
import os
import numpy as np
from tests.test_kinematics import setup_kinematics_test as roset
from robot.pre_process import mathematical_operators as math

# Verzeichnis mit allen JSON-Dateien
BASE_DIR = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\Daniel\inversekinematic_testcases_2"

TOLERANCE = 0.02  # Toleranz für den Vergleich ganzer Zeilen


@pytest.fixture(scope="session")
def robot():
    """Fixture zur Initialisierung der Roboterklasse (einmalig für alle Tests)."""
    return roset.load_robot()


@pytest.fixture(
    params=[
        os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if f.endswith(".json")
    ]
)
def test_data(request):
    """Fixture zum Laden einer einzelnen JSON-Datei als Testfall."""
    return roset.load_json_file(request.param)


def test_inverse_kinematics(robot, test_data):
    """Testet, ob eine berechnete Lösungsmenge eine Zeile enthält, die mit einer Zeile der erwarteten Lösungen übereinstimmt."""

    # Homogene Transformationsmatrix aus JSON laden
    fk_matrix = roset.extract_fk_matrix(test_data)
    angles = math.Rotation.to_euler_angles(fk_matrix[:3, :3], "ZYX")

    # Erwartete IK-Lösungen aus JSON extrahieren
    ik_solutions_raw = test_data.get("J", [])  # Liste von Listen
    num_expected_solutions = test_data.get("n")  # Anzahl der erwarteten Lösungen

    # Falls keine erwarteten Lösungen vorhanden sind
    if num_expected_solutions == 0:
        assert (
            len(ik_solutions_raw) == 0
        ), "Erwartet KEINE IK-Lösungen, aber Daten gefunden!"
        print("Test bestanden: Keine erwarteten Lösungen – keine berechneten Lösungen.")
        return

    # Erwartete Lösungen umwandeln: [{ "A1": val, "A2": val, ..., "A6": val }, ...]
    ik_solutions_expected = [
        {f"A{i + 1}": ik_solutions_raw[i][j] for i in range(6)}
        for j in range(num_expected_solutions)
    ]

    print(f"solutions expected\n")
    for line in ik_solutions_expected:
        print(line)

    # Berechnete IK-Lösungen
    ik_solutions_calculated = robot.inverse_kinematics(fk_matrix)
    num_calculated_solutions = len(
        ik_solutions_calculated
    )  # Anzahl der berechneten Lösungen

    print("solutions calculated\n")
    for line in ik_solutions_calculated:
        print(line)

    # Falls keine Lösungen berechnet wurden, obwohl welche erwartet wurden
    assert (
        num_calculated_solutions > 0
    ), f"Berechnete IK hat keine Lösungen gefunden, obwohl {num_expected_solutions} erwartet wurden!"

    # Validierte Lösungsmenge bestimmen
    validated_solutions = []

    for i, calculated_solution in enumerate(ik_solutions_calculated, start=1):
        for j, expected_solution in enumerate(ik_solutions_expected, start=1):
            if all(
                abs(
                    calculated_solution[f"A{k + 1}.{i}"]
                    - expected_solution[f"A{k + 1}"]
                )
                < TOLERANCE
                for k in range(6)
            ):
                validated_solutions.append(calculated_solution)
                break  # Sobald eine Übereinstimmung gefunden wurde, zur nächsten berechneten Lösung übergehen

    # Prüfen, ob die validierte Lösungsmenge gültig ist
    assert (
        len(validated_solutions) > 0
    ), f"Keine Lösung hat die Toleranzanforderung erfüllt, obwohl Lösungen erwartet wurden!"
    assert (
        len(validated_solutions) <= num_expected_solutions
    ), f"Zu viele Lösungen gefunden ({len(validated_solutions)} > {num_expected_solutions})!"

    print(f"Test erfolgreich: {len(validated_solutions)} passende Lösungen gefunden.")
