import numpy as np
from scipy.interpolate import interp1d


def create_interpolator(characteristic_curve):
    """
    Erstellt eine lineare Interpolationsfunktion basierend auf unsortierten Stützstellen.
    :param characteristic_curve: Dictionary mit "value": Liste der Form [[QM, RPM], ...]
    :return: Funktion, die für einen gegebenen Volumenstrom die interpolierte Drehzahl liefert
    """
    # Extrahiere die Werte aus dem Dictionary
    data = np.array(characteristic_curve["value"])

    # Sortiere die Werte nach dem Volumenstrom (erste Spalte)
    sorted_indices = np.argsort(data[:, 0])  # Sortiere nach QM
    sorted_data = data[sorted_indices]

    # Trenne die Spalten
    qm_values = sorted_data[:, 0]  # Volumenstrom
    rpm_values = sorted_data[:, 1]  # Drehzahl

    # Erstelle die lineare Interpolationsfunktion
    interpolator = interp1d(
        qm_values, rpm_values, kind="linear", fill_value="extrapolate"
    )

    return interpolator


# Beispielhafte Eingabedaten
characteristic_curve = {
    "description": "Gives the function of Flow to RPM of the Pump in [QM, RPM]",
    "value": [[10, 100], [30, 360], [20, 220]],  # Absichtlich unsortiert
    "type": "list[list[float,float]]",
}

# Erstelle die Interpolationsfunktion
interpolator = create_interpolator(characteristic_curve)

# Beispiel: Werte berechnen
test_qms = [15, 25, 35]  # Volumenströme, für die interpoliert wird
interpolated_rpms = [interpolator(qm) for qm in test_qms]

# Ergebnisse ausgeben
for qm, rpm in zip(test_qms, interpolated_rpms):
    print(f"QM: {qm}, Interpolated RPM: {rpm}")
