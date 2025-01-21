import numpy as np


class RobotOPW:
    """RobotOPW class for calculating joint angles or wrist center points of ortho-parallel robots with minimal initialization data."""

    def __init__(
        self,
        robot_id: str,
        robot_geometry: dict,
        robot_rotation_sign: dict,
        robot_rotation_limit: dict,
        robot_rotation_offset: dict,
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

        # Rotation properties
        self.offset = np.deg2rad(
            [robot_rotation_offset[f"A{i+1}"] for i in range(self.num_axis)]
        )
        self.sign = np.array(
            [robot_rotation_sign[f"A{i+1}"] for i in range(self.num_axis)]
        )
        self.lim = np.deg2rad(
            [
                [robot_rotation_limit[f"A{i+1}"][0], robot_rotation_limit[f"A{i+1}"][1]]
                for i in range(self.num_axis)
            ]
        )
        self.limits_lower = self.lim[:, 0].reshape(self.num_axis, 1)
        self.limits_upper = self.lim[:, 1].reshape(self.num_axis, 1)

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
            f"Rotation Offsets (deg): {np.rad2deg(self.offset).tolist()}"
        )

    def add_correction(self, A):
        """
        Modifies joint angels in "Brandstötter et al." convention to robot specific convention
        """
        return A * self.sign - self.offset

    def sub_correction(self, A):
        """
        Turns angles from specific robot convention to "Brandstötter et al." convention
        """
        return A * self.sign[:, np.newaxis] + self.offset[:, np.newaxis]

    def validate_joint_limits(self, solutions_rad) -> np.ndarray:
        """
        Validate if joint angles are within the specified limits.
        :param solutions_rad: Solutions in radians, shape (6, N).
        :return: Solutions with an additional row indicating validity (True/False).
        """
        # Check joint limits
        within_lower_limits = robot.sub_correction(solutions_rad) >= np.deg2rad(
            self.limits_lower
        )
        within_upper_limits = robot.add_correction(solutions_rad) <= np.deg2rad(
            self.limits_upper
        )
        is_valid = np.all(within_lower_limits & within_upper_limits, axis=0)

        # Append validity row to the solutions
        validated_solutions = np.vstack((solutions_rad, is_valid))
        return validated_solutions

    def forward_kinematics(self, A: np.array):
        """
        Calculates the forward kinematics of the robot using RobotOPW.
        :param A:
        :return:
        """
        A = self.add_correction(np.deg2rad(A))

        # forward kinematics (orientation part)
        s, c = np.sin(A), np.cos(A)

        psi3 = np.arctan2(self.a2, self.c3)
        k = np.sqrt(self.a2**2 + self.c3**2)

        d = A[1] + A[2] + psi3

        cx1 = self.c2 * s[1] + k * np.sin(d) + self.a1
        cy1 = self.b
        cz1 = self.c2 * c[1] + k * np.cos(d)

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

        T = np.eye(4)
        T[:3, :3] = r_0e
        T[:3, 3] = u
        return T

    def inverse_kinematics(self, T: np.ndarray):
        """
        Compute the inverse kinematics for a 3R manipulator based on a given 4x4 transformation matrix.
        :param T: 4x4 transformation matrix. Wrist center is in column 4, rows 1-3.
        :return: Tuple of two matrices: (solutions in rad, solutions in deg), where each column represents [theta1, theta2, theta3, theta4, theta5, theta6].
        """

        # Extract wrist center position from the transformation matrix
        cx0, cy0, cz0 = T[0, 3], T[1, 3], T[2, 3]
        # Extract rotation matrix from the transformation matrix
        e11, e12, e13 = T[0, 0], T[0, 1], T[0, 2]
        e21, e22, e23 = T[1, 0], T[1, 1], T[1, 2]
        e31, e32, e33 = T[2, 0], T[2, 1], T[2, 2]

        # Calculation of positional part
        # Step 1: Compute intermediate values
        n_x1 = np.sqrt(cx0**2 + cy0**2 - self.b**2) - self.a1
        s_12 = n_x1**2 + (cz0 - self.c1) ** 2  # s12 = s1^2
        s_22 = (n_x1 + 2 * self.a1) ** 2 + (cz0 - self.c1) ** 2  # s22 = s2^2
        k = np.sqrt(self.a2**2 + self.c3**2)

        # Initialize theta matrix with complex values (for unreachable configurations)
        theta = np.ones((3, 4), dtype=complex) * 1j

        # Step 2: Check if solutions are real
        if np.isreal(n_x1):
            # Solve for theta1
            if np.isreal(n_x1 + self.a1):
                theta1_1 = np.arctan2(cy0, cx0) - np.arctan2(self.b, n_x1 + self.a1)
                theta1_3 = (
                    np.arctan2(cy0, cx0) - np.arctan2(self.b, n_x1 + self.a1) + np.pi
                )

                theta[0, 0] = theta1_1
                theta[0, 1] = theta1_1
                theta[0, 2] = theta1_3
                theta[0, 3] = theta1_3

            # Solve for theta2
            value1 = (s_12 + self.c2**2 - k**2) / (2 * np.sqrt(s_12) * self.c2)
            if -1 <= value1 <= 1:
                theta2_1 = -np.arccos(value1) + np.arctan2(n_x1, cz0 - self.c1)
            else:
                theta2_1 = np.nan

            if -1 <= value1 <= 1:
                theta2_2 = +np.arccos(value1) + np.arctan2(n_x1, cz0 - self.c1)
            else:
                theta2_2 = np.nan

            theta[1, 0] = theta2_1
            theta[1, 1] = theta2_2

            value2 = (s_22 + self.c2**2 - k**2) / (2 * np.sqrt(s_22) * self.c2)
            if np.isreal(n_x1 + 2 * self.a1):
                if -1 <= value2 <= 1:
                    theta2_3 = -np.arccos(value2) - np.arctan2(
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

            # Calculate theta_5
            print(m)
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
                [theta_1, theta_2, theta_3, theta_4_i, theta_5_i, theta_6_q]
            )
            final_solutions_rad.append(
                [theta_1, theta_2, theta_3, theta_4_q, theta_5_q, theta_6_i]
            )
            final_solutions_rad.append(
                [theta_1, theta_2, theta_3, theta_4_q, theta_5_q, theta_6_q]
            )

        final_solutions_rad = np.array(final_solutions_rad).T

        return final_solutions_rad


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
        "A2": [-130, 180],
        "A3": [-100, 144],
        "A4": [-350, 350],
        "A5": [-120, 120],
        "A6": [-350, 350],
    }
    robot_rotation_offset = {"A1": 0, "A2": 0, "A3": 0, "A4": 0, "A5": 0, "A6": 0}

    # Initialize robot
    robot = RobotOPW(
        robot_id="ExampleRobot",
        robot_geometry=robot_geometry,
        robot_rotation_sign=robot_rotation_sign,
        robot_rotation_limit=robot_rotation_limit,
        robot_rotation_offset=robot_rotation_offset,
    )

    # Example 4x4 transformation matrix (input)
    T = np.array(
        [
            [-1.0, 0.0, 0.0, 2025],
            [0.0, 1.0, 0.0, -1494.637],
            [0.0, 0.0, -1.0, 1042.17],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )

    A = [0, 100, 10, 0, 100, 0]

    # Step 1: Calculate inverse kinematics
    # solutions_rad = robot.inverse_kinematics(T)
    fwkin = robot.forward_kinematics(A)

    print(fwkin)

    # print("Inverse Kinematics Solutions (Radians):")
    # print(solutions_rad)
