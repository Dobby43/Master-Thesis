import numpy as np
from scipy.constants import precision
import math

from robot.pre_process.mathematical_operators import Rotation


class RobotOPW:
    """RobotOPW class for calculating joint angles or wrist center points of ortho-parallel robots with minimal initialization data."""

    def __init__(
        self,
        robot_id: str,
        robot_geometry: dict,
        robot_base_radius: float,
        robot_rotation_sign: dict,
        robot_rotation_limit: dict,
        robot_rotation_offset: dict,
        robot_tool_offset: dict,
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

        # Base dimensions
        self.base_r = robot_base_radius

        # tool_offset from $NULLFRAME
        self.tool_offset_x = robot_tool_offset["X"]
        self.tool_offset_y = robot_tool_offset["Y"]
        self.tool_offset_z = robot_tool_offset["Z"]

        # Rotation properties
        self.offset = [robot_rotation_offset[f"A{i+1}"] for i in range(self.num_axis)]
        self.sign = np.array(
            [robot_rotation_sign[f"A{i+1}"] for i in range(self.num_axis)]
        )
        self.lim = robot_rotation_limit

        self.precision = 5

    def __str__(self):
        geometry = f"a1={self.a1}, a2={self.a2}, b={self.b}, c1={self.c1}, c2={self.c2}, c3={self.c3}, c4={self.c4}"
        limits = ", ".join(
            f"A{i + 1}: [{low:.1f}, {high:.1f}]"
            for i, (low, high) in enumerate(np.rad2deg(self.lim))
        )
        return (
            f"Robot ID: {self.type}\n"
            f"Geometry [mm]: {geometry}\n"
            f"Base Radius [mm] r: {self.base_r}"
            f"Rotation Signs: {self.sign.tolist()}\n"
            f"Rotation Limits [deg]: {limits}\n"
            f"Rotation Offsets [deg]: {(self.offset)}"
        )

    def add_correction(self, A):
        """
        Modifies joint angles in "Brandstötter et al." convention to robot specific convention
        needs angles in [deg]
        """
        corrected_A = A * self.sign + self.offset
        return corrected_A

    def sub_correction(self, A):
        """
        Turns angles from specific robot convention to "Brandstötter et al." convention
        needs angles in [deg]
        """
        return A * self.sign - self.offset

    def validate_joint_limits_fk(self, joint_angles):
        """
        Prüft, ob die Gelenkwinkel innerhalb der spezifizierten Grenzwerte liegen.
        """
        for joint, value in joint_angles.items():
            lower, upper = self.lim[joint]
            if not (lower <= value <= upper):
                return False

        return True

    def validate_joint_limits_ik(self, solutions_deg):
        """
        Prüft, ob die berechneten Gelenkwinkel innerhalb der spezifizierten Grenzwerte liegen.
        """
        valid_solutions = []

        joint_names = ["A1", "A2", "A3", "A4", "A5", "A6"]

        for i in range(solutions_deg.shape[1]):  # Jede Lösung durchgehen
            solution = solutions_deg[:, i]
            within_limits = True

            for j, joint in enumerate(joint_names):
                lower, upper = self.lim[joint]
                if not (lower <= np.round(solution[j], self.precision) <= upper):
                    within_limits = False
                    break

            if within_limits:
                valid_solutions.append(solution)

        return (
            np.array(valid_solutions).T
            if valid_solutions
            else np.array([]).reshape(6, 0)
        )

    def validate_self_intersecting(self, x: float, y: float, z: float) -> bool:
        """
        Prüft, ob die berechneten Koordinaten innerhalb eines verbotenen Zylinders (Radius `r`, Höhe `c1`) liegen.
        """

        # calculate radius from robotroot of given point
        r_squared = x**2 + y**2

        # self collision if point is inside given radius and in between z=0 and self.c1
        if r_squared <= self.base_r**2 and (0 <= z <= self.c1):
            return False

        return True  # no self collision

    def forward_kinematics(self, joint_angles: dict[str, float]):
        """
        Calculates the forward kinematics of the robot including tool offset.
        :param joint_angles: Joint angles according to robot convention in degrees.
        :return: Transformation matrix including tool offset.
        """
        if not self.validate_joint_limits_fk(joint_angles):
            reachable = False
            print(f"[ERROR] Given joint angles {joint_angles} are out of joint limits")
            return [], reachable
        else:
            reachable = True
            A = np.deg2rad(
                self.sub_correction(
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

            psi3 = np.arctan(self.a2 / self.c3)
            k = np.sqrt(self.a2**2 + self.c3**2)

            cx1 = self.c2 * s[1] + k * np.sin(A[1] + A[2] + psi3) + self.a1
            cy1 = self.b
            cz1 = self.c2 * c[1] + k * np.cos(A[1] + A[2] + psi3)

            cx0 = cx1 * c[0] - cy1 * s[0]
            cy0 = cx1 * s[0] + cy1 * c[0]
            cz0 = cz1 + self.c1

            # Check for self collision
            if not self.validate_self_intersecting(cx0, cy0, cz0):
                reachable = False
                print(
                    f"[ERROR] Self-collision: coordinates ({cx0:.2f}, {cy0:.2f}, {cz0:.2f}) are inside given base of robot"
                )
                return [], reachable

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

            # Check for self collision of
            if not self.validate_self_intersecting(
                float(u[0]), float(u[1]), float(u[2])
            ):
                reachable = False
                print(
                    f"[ERROR] Self-collision: coordinates ({float(u[0]):.2f}, {float(u[1]):.2f}, {float(u[2]):.2f}) are inside given base of robot"
                )
                return [], reachable

            t = np.eye(4)
            t[:3, :3] = r_0e
            t[:3, 3] = u

            # Check for self collision

            return t, reachable

    def inverse_kinematics(self, hom_trans):
        """
        Compute the inverse kinematics for a 3R manipulator based on a given 4x4 transformation matrix.
        :param hom_trans: np.array of the homogenous transformation matrix for any given point in "Brandstötter et al." convention
        :return: Tuple of two matrices: (solutions in rad, solutions in deg), where each column represents [theta1, theta2, theta3, theta4, theta5, theta6].
        """
        # extract coordinates from homogenious transformation matrix
        x, y, z = hom_trans[0, 3], hom_trans[1, 3], hom_trans[2, 3]

        print(f"x: {x}, y: {y}, z: {z}")

        # Check for self-collision
        if not self.validate_self_intersecting(x, y, z):
            print(
                f"[ERROR] Self-collision detected: Target Position ({x:.2f}, {y:.2f}, {z:.2f}) is inside robot base"
            )
            return []

        r0e = hom_trans[:3, :3]

        # calculate the position of the wrist center based on given point, tool_offset and orientation of tool

        tool_offset_robotroot = r0e @ np.array(
            [self.tool_offset_x, self.tool_offset_y, self.tool_offset_z]
        )
        c4_robotroot = self.c4 * r0e @ np.array([0, 0, 1])

        # Extract wrist center position from the transformation matrix
        cx0 = x - tool_offset_robotroot[0] - c4_robotroot[0]
        cy0 = y - tool_offset_robotroot[1] - c4_robotroot[1]
        cz0 = z - tool_offset_robotroot[2] - c4_robotroot[2]

        # Extract rotation matrix from the transformation matrix
        e11, e12, e13 = r0e[0, 0], r0e[0, 1], r0e[0, 2]
        e21, e22, e23 = r0e[1, 0], r0e[1, 1], r0e[1, 2]
        e31, e32, e33 = r0e[2, 0], r0e[2, 1], r0e[2, 2]

        # A) Calculation of positional part
        # Step 1: Compute intermediate values
        n_x1 = np.sqrt(cx0**2 + cy0**2 - self.b**2) - self.a1
        s_12 = n_x1**2 + (cz0 - self.c1) ** 2  # s12 = s1^2
        s_22 = (n_x1 + 2 * self.a1) ** 2 + (cz0 - self.c1) ** 2  # s22 = s2^2
        k = np.sqrt(self.a2**2 + self.c3**2)

        # Initialize theta matrix with complex values (for unreachable configurations)
        theta = np.ones((3, 4), dtype=complex) * 1j

        # Step 2: Check if solutions are real
        # np.isreal() determines if the Point in the x-y plane is inside the radius described by the offset b around the z axis.
        # If that's the case, the point is not reachable and the solution is marked as complex.
        # Changed to: cx0**2 + cy0**2 >= self.b**2 -> before np.isreal(np.sqrt(self.b**2 - (cx0**2 + cy0**2)))
        if cx0**2 + cy0**2 >= self.b**2:
            # Solve for theta1

            # Brandstötter version
            # theta1_1 = np.atan2(cy0, cx0) - np.atan2(self.b, n_x1 + self.a1)
            # theta1_2 = np.atan2(cy0, cx0) + np.atan2(self.b, n_x1 + self.a1) - np.pi

            # adjusted version to work within (+-180°)
            # theta1_1 = (np.atan2(cy0, cx0) - np.atan2(self.b, n_x1 + self.a1) + np.pi) % (2 * np.pi) - np.pi
            # theta1_2 = (np.atan2(cy0, cx0) + np.atan2(self.b, n_x1 + self.a1) - np.pi + np.pi) % (2 * np.pi) - np.pi

            # final version (to work within +-180°)
            theta1_1 = (
                np.atan2(cy0, cx0) - np.atan2(self.b, n_x1 + self.a1) + np.pi
            ) % (2 * np.pi) - np.pi
            theta1_2 = (
                np.atan2(cy0, cx0) + np.atan2(self.b, n_x1 + self.a1) - np.pi + np.pi
            ) % (2 * np.pi) - np.pi

            theta[0, 0] = theta1_1
            theta[0, 1] = theta1_1
            theta[0, 2] = theta1_2
            theta[0, 3] = theta1_2

            # Solve for theta2
            value1 = (s_12 + self.c2**2 - k**2) / (2 * np.sqrt(s_12) * self.c2)
            # Checks if value1 is inside the defined domain of acos
            if -1 <= value1 <= 1:
                raw_angle = np.arctan(n_x1 / (cz0 - self.c1))
                if cz0 - self.c1 < 0:  # atan2 via if clause
                    raw_angle += np.pi
                theta2_1 = -np.arccos(value1) + raw_angle
            else:
                theta2_1 = np.nan
            if -1 <= value1 <= 1:
                theta2_2 = +np.acos(value1) + np.atan2(n_x1, (cz0 - self.c1))
            else:
                theta2_2 = np.nan

            theta[1, 0] = theta2_1
            theta[1, 1] = theta2_2

            value2 = (s_22 + self.c2**2 - k**2) / (2 * np.sqrt(s_22) * self.c2)
            if -1 <= value2 <= 1:
                theta2_3 = -np.acos(value2) - np.atan2(
                    n_x1 + 2 * self.a1, cz0 - self.c1
                )
            else:
                theta2_3 = np.nan

            if -1 <= value2 <= 1:
                theta2_4 = +np.arccos(value2) - np.atan2(
                    n_x1 + 2 * self.a1, cz0 - self.c1
                )
            else:
                theta2_4 = np.nan

            theta[1, 2] = theta2_3
            theta[1, 3] = theta2_4

            # Solve for theta3
            value3_12 = (s_12 - self.c2**2 - k**2) / (2 * self.c2 * k)
            if -1 <= value3_12 <= 1:
                theta3_1 = +np.arccos(value3_12) - np.atan2(self.a2, self.c3)
            else:
                theta3_1 = np.nan

            if -1 <= value3_12 <= 1:
                theta3_2 = -np.arccos(value3_12) - np.atan2(self.a2, self.c3)
            else:
                theta3_2 = np.nan

            theta[2, 0] = theta3_1
            theta[2, 1] = theta3_2

            # not duplicated!
            value3_34 = (s_22 - self.c2**2 - k**2) / (2 * self.c2 * k)
            if -1 <= value3_34 <= 1:
                theta3_3 = +np.arccos(value3_34) - np.atan2(self.a2, self.c3)
            else:
                theta3_3 = np.nan

            if -1 <= value3_34 <= 1:
                theta3_4 = -np.arccos(value3_34) - np.atan2(self.a2, self.c3)
            else:
                theta3_4 = np.nan

            theta[2, 2] = theta3_3
            theta[2, 3] = theta3_4

        # Step 3: Filter valid solutions (columns with no NaN values)
        valid_columns = ~np.isnan(theta).any(axis=0)
        filtered_pos_solution_rad = np.real(theta[:, valid_columns])

        # B) Calculation of rotational part for filtered solutions of theta1-3
        # Step 1: Calculate orientation for valid solutions in radians
        final_solutions_rad = []

        for j in range(filtered_pos_solution_rad.shape[1]):
            theta_1, theta_2, theta_3 = filtered_pos_solution_rad[:, j]

            # Calculate the rotational matrix from base to wrist center
            s1, c1 = np.sin(theta_1), np.cos(theta_1)
            s23, c23 = np.sin(theta_2 + theta_3), np.cos(theta_2 + theta_3)

            r0c = np.array(
                [[c1 * c23, -c1 * s23, s1], [s1 * c23, -s1 * s23, -c1], [s23, c23, 0]]
            )

            # Calculate the rotational matrix from wrist center to nullframe / endefector
            rce = r0c.T @ r0e

            # Calculate the angels from this rotation matrix
            angles = Rotation.to_euler_angles(rce)

            # Precompute sinus and cosinus
            s_1 = np.sin(theta_1)
            c_1 = np.cos(theta_1)
            s_23 = np.sin(theta_2 + theta_3)
            c_23 = np.cos(theta_2 + theta_3)

            # Calculate m_i
            m = e13 * s_23 * c_1 + e23 * s_23 * s_1 + e33 * c_23
            # Calculate theta_5
            # max() to filter for numerical inaccuracies that would yield to a negativ value inside sqrt
            theta_5_i = np.atan2(math.sqrt(max(1 - m**2, 0)), m)
            theta_5_q = -theta_5_i

            # Check if one of the values of Theta 5 is a singularity (theta_5 = 0)
            # 3. Mistake (no valid solution for singularity)
            if np.isclose(theta_5_i, 0, atol=1e-6) or np.isclose(
                theta_5_q, 0, atol=1e-6
            ):

                # If Theta 5 = 0 choose alternative way of calculating Theta 4 and 6
                # Fix Theta 4 = 0 as Axis 4 and 6 are co-linear (gimbal-lock)
                theta_4_i = 0
                theta_4_q = 0
                # Calculate Theta 6 from the rotational matrix rce
                theta_6_i = np.deg2rad(angles[1])

                theta_6_q = theta_6_i - 2 * np.pi

            else:
                # Following Brandstötter convention
                # Calculate theta_4
                theta_4_i = np.atan2(
                    e23 * c_1 - e13 * s_1,
                    e13 * c_23 * c_1 + e23 * c_23 * s_1 - e33 * s_23,
                )
                theta_4_q = theta_4_i + np.pi

                # Calculate theta_6
                theta_6_i = np.atan2(
                    e12 * s_23 * c_1 + e22 * s_23 * s_1 + e32 * c_23,
                    -e11 * s_23 * c_1 - e21 * s_23 * s_1 - e31 * c_23,
                )

                theta_6_q = theta_6_i - np.pi

            # C) Combine all solutions into the final matrix in radians
            final_solutions_rad.append(
                [theta_1, theta_2, theta_3, theta_4_i, theta_5_i, theta_6_i]
            )
            final_solutions_rad.append(
                [theta_1, theta_2, theta_3, theta_4_q, theta_5_q, theta_6_q]
            )

        # D) Convert to degrees
        final_solutions_deg = np.rad2deg(final_solutions_rad).T

        # Abort if no solutions for given point exist
        if final_solutions_deg.size == 0:
            print(f"[ERROR] Point out of reachable domain of robot")
            return []

        # E) Adjust with offset for robot convention
        final_solutions_corrected = np.column_stack(
            [
                self.add_correction(final_solutions_deg[:, i])
                for i in range(final_solutions_deg.shape[1])
            ]
        )

        # print("final solution corrected")
        # for line in final_solutions_corrected:
        #     print(line)

        # F) Check if angles are within limits
        valid_solutions = self.validate_joint_limits_ik(final_solutions_corrected)

        # Abort for no valid solutions within joint angle limits
        if valid_solutions.size == 0:
            print(
                f"[ERROR] All possible joint angles for point exceed min/max joint angles"
            )
            return []

        # G) Convert solutions into dictionary format with rounding
        num_solutions = valid_solutions.shape[1]

        solutions_list = [
            {
                f"A{i + 1}.{j + 1}": round(float(valid_solutions[i, j]), self.precision)
                for i in range(6)
            }
            for j in range(num_solutions)
        ]

        return solutions_list


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

    # Initialize robot
    robot = RobotOPW(
        robot_id="ExampleRobot",
        robot_geometry=robot_geometry,
        robot_base_radius=0,  # 1. Mistake for testcases (RoboDk can intersect its own base)
        robot_rotation_sign=robot_rotation_sign,
        robot_rotation_limit=robot_rotation_limit,
        robot_rotation_offset=robot_rotation_offset,
        robot_tool_offset=tool_offset,
    )

    hom_trans_0 = np.array(
        [
            [-1.0000000e00, 0.0000000e00, 0.0000000e00, 2025],
            [0.0000000e00, 1.0000000e00, -0, 0],
            [0.0000000e00, 0, -1.0000000e00, 2000],
            [0, 0, 0, 1],
        ]
    )

    # rotation matrix for: [A: 6.518,  B: -50.267, C: 135.7]
    hom_trans_2 = np.array(
        [
            [0.635077, -0.451356, 0.626861, 1312.347],
            [0.072556, -0.773080, -0.630145, 705.641],
            [0.769034, 0.445673, -0.458217, 1711.979],
            [0, 0, 0, 1],
        ]
    )

    # rotation matrix for: [ A: 43.495,  B: 25.624, C: -8.803]
    hom_trans_3 = np.array(
        [
            [0.654, -0.728, 0.205, -422.667],
            [0.621, 0.671, 0.405, 117.502],
            [-0.432, -0.138, 0.891, 3872.297],
            [0, 0, 0, 1],
        ]
    )

    # INVERSE KINEMATICS

    solution_inv = robot.inverse_kinematics(hom_trans_0)
    for entry in solution_inv:
        print(entry)

    # # FORWARD KINEMATICS
    # A = {"A1": 0, "A2": -90.0, "A3": 90.0, "A4": 0.0, "A5": 0, "A6": 0.0}
    # A = {"A1": 0, "A2": -90, "A3": 90, "A4": 0, "A5": 90, "A6": 0}
    # solutions = robot.forward_kinematics(A)
    # print("Forward Kinematics Solutions relative to ROBOTROOT (deg):")
    # print(solutions)

    # [[-1.000e+00  0.000e+00  0.000e+00  2.025e+03]
    #  [0.000e+00   1.000e+00  0.000e+00  0.000e+00]
    #  [-0.000e+00  0.000e+00 -1.000e+00  2.000e+03]
    #  [0.000e+00   0.000e+00  0.000e+00  1.000e+00]]
