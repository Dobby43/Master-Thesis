import numpy as np

from robot.pre_process.mathematical_operators import Rotation


class RobotOPW:
    """RobotOPW class for calculating joint angles or wrist center points of ortho-parallel robots with minimal initialization data."""

    def __init__(
        self,
        robot_id: str,
        robot_geometry: dict,
        robot_rotation_sign: dict,
        robot_rotation_limit: dict,
        robot_rotation_offset: dict,
        robot_tool_offset: dict,
        robot_rotation_root_tool: np.array,
    ):
        # Namen of robot
        self.type = robot_id
        # Number of axis
        self.num_axis = 6

        # Geometry
        self.a1 = robot_geometry["a1"]
        self.a2 = robot_geometry["a2"]
        self.b = robot_geometry["b"]
        self.c1 = robot_geometry["c1"]
        self.c2 = robot_geometry["c2"]
        self.c3 = robot_geometry["c3"]
        self.c4 = robot_geometry["c4"]

        # tool_offset from $NULLFRAME
        self.tool_offset_x = robot_tool_offset["X"]
        self.tool_offset_y = robot_tool_offset["Y"]
        self.tool_offset_z = robot_tool_offset["Z"]

        # Rotation matrix from $NULLFRAME / $TCP to $ROBOTROOT
        self.r0e = robot_rotation_root_tool

        # Rotation properties
        self.offset = [robot_rotation_offset[f"A{i+1}"] for i in range(self.num_axis)]
        self.sign = np.array(
            [robot_rotation_sign[f"A{i+1}"] for i in range(self.num_axis)]
        )
        self.lim = np.array(
            [
                [
                    robot_rotation_limit[f"A{i + 1}"][0],
                    robot_rotation_limit[f"A{i + 1}"][1],
                ]
                for i in range(self.num_axis)
            ],
            dtype=float,
        )  # Direkt als numpy-Array

        self.limits_lower = self.lim[:, 0].reshape(self.num_axis, 1)  # Untere Grenze
        self.limits_upper = self.lim[:, 1].reshape(self.num_axis, 1)  # Obere Grenze

        self.precision = 2

    def __str__(self):
        geometry = f"a1={self.a1}, a2={self.a2}, b={self.b}, c1={self.c1}, c2={self.c2}, c3={self.c3}, c4={self.c4}"
        limits = ", ".join(
            f"A{i + 1}: [{low:.1f}, {high:.1f}]"
            for i, (low, high) in enumerate(np.rad2deg(self.lim))
        )
        return (
            f"Robot ID: {self.type}\n"
            f"Geometry (mm): {geometry}\n"
            f"Rotation Signs: {self.sign.tolist()}\n"
            f"Rotation Limits (deg): {limits}\n"
            f"Rotation Offsets (deg): {(self.offset)}"
        )

    def add_correction(self, A):
        """
        Modifies joint angles in "Brandstötter et al." convention to robot specific convention
        """
        print("Before Correction (deg):")
        print(A)

        corrected_A = A * self.sign + self.offset

        print("After Correction (deg):")
        print(corrected_A)

        return corrected_A

    def sub_correction(self, A):
        """
        Turns angles from specific robot convention to "Brandstötter et al." convention
        """
        return A * self.sign - self.offset

    def validate_joint_limits(self, solutions_deg):
        """
        Prüft, ob die berechneten Gelenkwinkel innerhalb der spezifizierten Grenzwerte liegen.
        :param solutions_deg: 2D-Numpy-Array mit Winkelwerten in Grad (6 x N)
        :return: Gefiltertes 2D-Numpy-Array mit gültigen Lösungen
        """
        valid_solutions = []
        for i in range(
            solutions_deg.shape[1]
        ):  # Durch alle Spalten iterieren (jeweils eine Lösung)
            solution = solutions_deg[:, i]

            # Prüfen, ob alle Gelenkwinkel innerhalb der Grenzwerte liegen
            within_limits = np.all(
                (self.limits_lower.flatten() <= solution)
                & (solution <= self.limits_upper.flatten())
            )

            if within_limits:
                valid_solutions.append(solution)
            else:
                print(f"Solution {i + 1} discarded (out of limits): {solution}")

        # Konvertiere die gültigen Lösungen in ein 2D-Array, falls noch Lösungen übrig sind
        if valid_solutions:
            return np.array(valid_solutions).T
        else:
            print("No valid solutions found!")
            return np.array([]).reshape(
                6, 0
            )  # Leere Lösung mit der richtigen Dimension zurückgeben

    def forward_kinematics(self, joint_angles: dict[str, float]):
        """
        Calculates the forward kinematics of the robot including tool offset.
        :param joint_angles: Joint angles in degrees.
        :return: Transformation matrix including tool offset.
        """
        A = self.add_correction(
            np.deg2rad(
                [
                    joint_angles["A1"],
                    joint_angles["A2"],
                    joint_angles["A3"],
                    joint_angles["A4"],
                    joint_angles["A5"],
                    joint_angles["A6"],
                ]
            )
        )

        # forward kinematics (orientation part)
        s, c = np.sin(A), np.cos(A)

        psi3 = np.arctan2(self.a2, self.c3)
        k = np.sqrt(self.a2**2 + self.c3**2)

        cx1 = self.c2 * s[1] + k * np.sin(A[1] + A[2] + psi3) + self.a1
        cy1 = self.b
        cz1 = self.c2 * c[1] + k * np.cos(A[1] + A[2] + psi3)

        cx0 = cx1 * c[0] - cy1 * s[0]
        cy0 = cx1 * s[0] + cy1 * c[0]
        cz0 = cz1 + self.c1

        r_0c = np.array(
            [
                [
                    c[0] * c[1] * c[2] - c[0] * s[1] * s[2],
                    -s[0],
                    c[0] * c[1] * s[2] + c[0] * s[1] * c[2],
                ],
                [
                    s[0] * c[1] * c[2] - s[0] * s[1] * s[2],
                    c[0],
                    s[0] * c[1] * s[2] + s[0] * s[1] * c[2],
                ],
                [-s[1] * c[2] - c[1] * s[2], 0, -s[1] * s[2] + c[1] * c[2]],
            ]
        )

        r_ce = np.array(
            [
                [
                    c[3] * c[4] * c[5] - s[3] * s[5],
                    -c[3] * c[4] * s[5] - s[3] * c[5],
                    c[3] * s[4],
                ],
                [
                    s[3] * c[4] * c[5] + c[3] * s[5],
                    -s[3] * c[4] * s[5] + c[3] * c[5],
                    s[3] * s[4],
                ],
                [-s[4] * c[5], s[4] * s[5], c[4]],
            ]
        )

        r_0e = r_0c @ r_ce

        u = np.array([cx0, cy0, cz0]) + self.c4 * (r_0e @ np.array([0, 0, 1]))
        u += r_0e @ np.array(
            [self.tool_offset_x, self.tool_offset_y, self.tool_offset_z]
        )

        t = np.eye(4)
        t[:3, :3] = r_0e
        t[:3, 3] = u
        t_round = np.round(t, self.precision)

        return t_round

    def inverse_kinematics(self, point):
        """
        Compute the inverse kinematics for a 3R manipulator based on a given 4x4 transformation matrix.
        :param point: dictionary of coordinates X Y and Z
        :return: Tuple of two matrices: (solutions in rad, solutions in deg), where each column represents [theta1, theta2, theta3, theta4, theta5, theta6].
        """
        # calculate the position of the wrist center based on given point, tool_offset and orientation of tool
        tool_offset_robotroot = self.r0e @ np.array(
            [self.tool_offset_x, self.tool_offset_y, self.tool_offset_z]
        )

        c4_robotroot = self.c4 * self.r0e @ np.array([0, 0, 1])

        # Extract wrist center position from the transformation matrix
        cx0 = point["X"] - tool_offset_robotroot[0] - c4_robotroot[0]
        cy0 = point["Y"] - tool_offset_robotroot[1] - c4_robotroot[1]
        cz0 = point["Z"] - tool_offset_robotroot[2] - c4_robotroot[2]

        print(f"Coordinates Point = {point} ")
        print(f"Coordinates Point cx0, cy0, cz0 = {cx0,cy0,cz0}")
        print(f"c1 = {self.c1}")

        # Extract rotation matrix from the transformation matrix
        e11, e12, e13 = self.r0e[0, 0], self.r0e[0, 1], self.r0e[0, 2]
        e21, e22, e23 = self.r0e[1, 0], self.r0e[1, 1], self.r0e[1, 2]
        e31, e32, e33 = self.r0e[2, 0], self.r0e[2, 1], self.r0e[2, 2]

        # e11, e12, e13 = T[0, 0], T[0, 1], T[0, 2]
        # e21, e22, e23 = T[1, 0], T[1, 1], T[1, 2]
        # e31, e32, e33 = T[2, 0], T[2, 1], T[2, 2]

        # Calculation of positional part
        # Step 1: Compute intermediate values

        n_x1 = np.sqrt(cx0**2 + cy0**2 - self.b**2) - self.a1
        s_12 = n_x1**2 + (cz0 - self.c1) ** 2  # s12 = s1^2
        s_22 = (n_x1 + 2 * self.a1) ** 2 + (cz0 - self.c1) ** 2  # s22 = s2^2
        k = np.sqrt(self.a2**2 + self.c3**2)

        print(f"n_x1 = {n_x1}")

        # Initialize theta matrix with complex values (for unreachable configurations)
        theta = np.ones((3, 4), dtype=complex) * 1j

        # Step 2: Check if solutions are real
        # np.isreal() determines if the Point in the x-y plane is inside the radius described by the offset b around the z axis.
        # If that's the case, the point is not reachable and the solution is marked as complex.
        if cx0**2 + cy0**2 >= self.b**2:
            # Solve for theta1
            theta1_1 = np.atan2(cy0, cx0) - np.atan2(self.b, n_x1 + self.a1)
            # mistake in Brandstötter et al. paper regarding signs
            theta1_2 = np.atan2(cy0, cx0) - np.atan2(self.b, n_x1 + self.a1) + np.pi

            theta[0, 0] = theta1_1
            theta[0, 1] = theta1_1
            theta[0, 2] = theta1_2
            theta[0, 3] = theta1_2

            # Solve for theta2
            print(f"FOR THETA 1,0 and 1,1: s_12 = {s_12}, k = {k}, c2 = {self.c2}")
            value1 = (s_12 + self.c2**2 - k**2) / (2 * np.sqrt(s_12) * self.c2)
            print(f"value1 = {value1}")
            # Checks if value1 is inside the defined domain of acos
            if -1 <= value1 <= 1:
                raw_angle = np.arctan(n_x1 / (cz0 - self.c1))
                if cz0 - self.c1 < 0:  # Korrektur für den Quadranten
                    raw_angle += np.pi
                print(raw_angle)
                print(np.arccos(value1))
                theta2_1 = -np.arccos(value1) + raw_angle
            else:
                theta2_1 = np.nan

            print(f"arccos(value1) = {np.arccos(value1)}")
            print(f"atan2(n_x1, cz0 - c1) = {np.atan2(n_x1, cz0 - self.c1)}")
            print(np.rad2deg(theta1_1))

            if -1 <= value1 <= 1:
                theta2_2 = +np.acos(value1) + np.arctan2(n_x1, (cz0 - self.c1))
            else:
                theta2_2 = np.nan

            theta[1, 0] = theta2_1
            print(f"theta1_1 = {theta[1, 0]}")
            theta[1, 1] = theta2_2

            print(f"FOR THETA 1,2 and 1,3: s_12 = {s_22}, k = {k}, c2 = {self.c2}")
            value2 = (s_22 + self.c2**2 - k**2) / (2 * np.sqrt(s_22) * self.c2)
            print(f"value2 = {value2}")
            if -1 <= value2 <= 1:
                theta2_3 = -np.acos(value2) - np.atan2(
                    n_x1 + 2 * self.a1, cz0 - self.c1
                )
            else:
                theta2_3 = np.nan

            if -1 <= value2 <= 1:
                theta2_4 = +np.arccos(value2) - np.arctan2(
                    n_x1 + 2 * self.a1, cz0 - self.c1
                )
            else:
                theta2_4 = np.nan

            theta[1, 2] = theta2_3
            theta[1, 3] = theta2_4

            # Solve for theta3
            value3_12 = (s_12 - self.c2**2 - k**2) / (2 * self.c2 * k)
            if -1 <= value3_12 <= 1:
                theta3_1 = +np.arccos(value3_12) - np.arctan2(self.a2, self.c3)
            else:
                theta3_1 = np.nan

            if -1 <= value3_12 <= 1:
                theta3_2 = -np.arccos(value3_12) - np.arctan2(self.a2, self.c3)
            else:
                theta3_2 = np.nan

            theta[2, 0] = theta3_1
            theta[2, 1] = theta3_2

            # not duplicated!
            value3_34 = (s_22 - self.c2**2 - k**2) / (2 * self.c2 * k)
            if -1 <= value3_34 <= 1:
                theta3_3 = +np.arccos(value3_34) - np.arctan2(self.a2, self.c3)
            else:
                theta3_3 = np.nan

            if -1 <= value3_34 <= 1:
                theta3_4 = -np.arccos(value3_34) - np.arctan2(self.a2, self.c3)
            else:
                theta3_4 = np.nan

            theta[2, 2] = theta3_3
            theta[2, 3] = theta3_4

        # Step 3: Filter valid solutions (columns with no NaN values)
        valid_columns = ~np.isnan(theta).any(axis=0)
        filtered_pos_solution_rad = np.real(theta[:, valid_columns])

        print(f"filtered_pos_solution = {np.rad2deg(filtered_pos_solution_rad)}\n")

        # Calculation of rotational part for filtered solutions of theta1-3
        # Step 4: Calculate orientation for valid solutions in radians
        final_solutions_rad = []

        for j in range(filtered_pos_solution_rad.shape[1]):
            theta_1, theta_2, theta_3 = filtered_pos_solution_rad[:, j]

            # Precompute sines and cosines
            s_1 = np.sin(theta_1)
            c_1 = np.cos(theta_1)
            s_23 = np.sin(theta_2 + theta_3)
            c_23 = np.cos(theta_2 + theta_3)

            # Calculate m_i
            m = e13 * s_23 * c_1 + e23 * s_23 * s_1 + e33 * c_23

            # Calculate theta_4
            theta_4_i = np.arctan2(
                e23 * c_1 - e13 * s_1, e13 * c_23 * c_1 + e23 * c_23 * s_1 - e33 * s_23
            )
            theta_4_q = theta_4_i + np.pi

            print(f"theta_4,1 = {theta_4_i}\ntheta_4,2 = {theta_4_q}")

            # Calculate theta_5
            theta_5_i = np.arctan2(np.sqrt(1 - m**2), m)
            theta_5_q = -theta_5_i

            # Calculate theta_6
            theta_6_i = np.arctan2(
                e12 * s_23 * c_1 + e22 * s_23 * s_1 + e32 * c_23,
                -e11 * s_23 * c_1 - e21 * s_23 * s_1 - e31 * c_23,
            )
            theta_6_q = theta_6_i - np.pi

            # Combine all solutions into the final matrix in radians
            final_solutions_rad.append(
                [theta_1, theta_2, theta_3, theta_4_i, theta_5_i, theta_6_i]
            )
            final_solutions_rad.append(
                [theta_1, theta_2, theta_3, theta_4_q, theta_5_q, theta_6_q]
            )

        # Zuerst Umwandlung in Grad
        final_solutions_deg = np.rad2deg(final_solutions_rad).T

        # Debugging-Ausgabe: Vor der Korrektur
        print("\n--- Inverse Kinematics (deg) BEFORE Correction ---")
        for i, sol in enumerate(final_solutions_deg.T):
            print(f"Solution {i + 1}: {sol}")

        # Anwendung der Korrektur
        final_solutions_corrected = np.column_stack(
            [
                self.add_correction(final_solutions_deg[:, i])
                for i in range(final_solutions_deg.shape[1])
            ]
        )

        # Debugging-Ausgabe: Nach der Korrektur
        print("\n--- Inverse Kinematics (deg) AFTER Correction ---")
        for i, sol in enumerate(final_solutions_corrected.T):
            print(f"Solution {i + 1}: {sol}")

        # *** NEU: Gelenkwinkel auf Grenzwerte überprüfen ***
        valid_solutions = self.validate_joint_limits(final_solutions_corrected)

        # Debugging-Ausgabe: Nach Validierung
        print("\n--- Inverse Kinematics (deg) AFTER LIMIT CHECK ---")
        if valid_solutions.shape[1] > 0:
            for i, sol in enumerate(valid_solutions.T):
                print(f"Valid Solution {i + 1}: {sol}")
        else:
            print("No valid solutions remain after limit check!")

        return valid_solutions


if __name__ == "__main__":
    # Robot-specific settings
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

    # Tool offset relative to TCP
    tool_offset = {"X": 0, "Y": 0, "Z": 0}

    robot_base_tool_rotation = np.array(
        [
            [1.0000000e00, 0.0000000e00, 0.0000000e00],
            [0.0000000e00, -1.0000000e00, -0],
            [0.0000000e00, 0, -1.0000000e00],
        ]
    )

    # Initialize robot
    robot = RobotOPW(
        robot_id="ExampleRobot",
        robot_geometry=robot_geometry,
        robot_rotation_sign=robot_rotation_sign,
        robot_rotation_limit=robot_rotation_limit,
        robot_rotation_offset=robot_rotation_offset,
        robot_tool_offset=tool_offset,
        robot_rotation_root_tool=robot_base_tool_rotation,
    )

    # # Example 4x4 transformation matrix (input)
    # T = np.array(
    #     [
    #         [-1.0, 0.0, 0.0, 2025],
    #         [0.0, 1.0, 0.0, -1494.637],
    #         [0.0, 0.0, -1.0, 752.17],
    #         [0.0, 0.0, 0.0, 1.0],
    #     ]
    # )
    #
    # solution_inv = robot.inverse_kinematics(T)
    # print(np.rad2deg(solution_inv))

    point1 = {
        "Move": "G0",
        "X": 2025,
        "Y": 0,
        "Z": 2000,
        "E_rel": 0,
        "Layer": 0,
        "Type": "travel",
        "Layer_Height": 15.0,
    }
    point2 = {
        "Move": "G1",
        "X": 900.000,
        "Y": -956.883,
        "Z": 1300.000,
        "E_Rel": 133.69,
        "Layer": 0,
        "Type": "wall_outer",
        "Layer_Height": 15.0,
    }
    point3 = {
        "Move": "G1",
        "X": 512.5,
        "Y": 2162.5,
        "Z": 15.0,
        "E_Rel": 133.69,
        "Layer": 0,
        "Type": "wall_outer",
        "Layer_Height": 15.0,
    }

    # Inverse Kinematics
    solution_inv = robot.inverse_kinematics(point2)

    # Spaltennamen für eine bessere Übersicht
    column_headers = ["θ1", "θ2", "θ3", "θ4", "θ5", "θ6"]

    # Berechnen, wie viele Lösungen es gibt
    num_solutions = solution_inv.shape[1]

    # Tabellenkopf drucken
    header = " | ".join(
        f"{col:^10}" for col in column_headers
    )  # Zentrierte Spaltennamen
    print(f"{'Solution':^10} | {header}")
    print("-" * (12 + 11 * len(column_headers)))  # Trennlinie

    # Zeilenweise Lösungen ausgeben
    for i in range(num_solutions):
        row_values = " | ".join(
            f"{solution_inv[j, i]:>10.3f}" for j in range(6)
        )  # Formatierte Zahlen
        print(f"{i + 1:^10} | {row_values}")

    # Forward Kinematics
    # A = {"A1": 0, "A2": -90.0, "A3": 90.0, "A4": 0.0, "A5": 90.0, "A6": 0.0}
    # # A = {"A1": 0, "A2": -90, "A3": 0, "A4": 0, "A5": 0, "A6": 0}
    # solutions = robot.forward_kinematics(A, tool_offset)
    # print("Forward Kinematics Solutions relative to ROBOTROOT (deg):")
    # print(solutions)

    # [[-1.000e+00  0.000e+00  0.000e+00  2.015e+03]
    #  [0.000e+00   1.000e+00  0.000e+00  1.000e+01]
    #  [-0.000e+00  0.000e+00 -1.000e+00  2.000e+03]
    #  [0.000e+00   0.000e+00  0.000e+00  1.000e+00]]
