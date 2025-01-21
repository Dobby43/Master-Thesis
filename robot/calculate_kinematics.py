def calculate_inverse_kinematics(matrices_points, robot):
    """
    Berechnet die Gelenkwinkel für eine Liste von Transformationsmatrizen.

    :param matrices_points: Liste von 4x4 Transformationsmatrizen.
    :param robot: Instanz des Roboterobjekts (pyKA).
    :return: Liste der Gelenkwinkel für jede Transformationsmatrix.
    """
    joint_solutions = []

    for i, T in enumerate(matrices_points):
        try:
            # Berechnung der Gelenkwinkel für die Transformationsmatrix
            joints = robot.inverse_kinematics(T)
            joint_solutions.append({"matrix_index": i, "joints": joints})
        except ValueError as e:
            # Fehlerbehandlung für unlösbare Kinematik
            joint_solutions.append({"matrix_index": i, "error": str(e)})

    return joint_solutions
