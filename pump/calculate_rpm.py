import numpy as np
from scipy.interpolate import interp1d


def get_rpm(
    points: list[dict],
    characteristic_curve: list[list[float]],
    vel_cp: float,
):
    """
    DESCRIPTION:
    Computes the required RPM and Voltage for a given pump characteristic curve based on input data.
    Also checks if the maximum flow rate of the pump is sufficient.

    :param points: List of points with flow information, where flow is given in mm^3/s
    :param characteristic_curve: Pump characteristic curve [[QM (l/min), RPM, Voltage, ...], ...] with arbitrary additional parameters
    :param vel_cp: print velocity that should be reached in m/s

    :return: List with [{RPM, Voltage, Vel_CP_Max}] where Vel_CP_Max is in m/s
    """
    # Extracting and sorting values from the characteristic curve
    data = np.array(characteristic_curve)
    sorted_data = data[np.argsort(data[:, 0])]
    qm_values = sorted_data[:, 0]  # Flow values in l/min
    parameter_values = sorted_data[:, 1:].T  # Extract remaining parameters dynamically

    # Define fill_value limits (low = 0, high = max(QM values))
    fill_value_limits = (0, max(qm_values))

    # Create interpolation functions for each parameter
    interpolator = [
        interp1d(
            qm_values,
            param,
            kind="linear",
            fill_value=fill_value_limits,
            bounds_error=False,
        )
        for param in parameter_values
    ]

    max_possible_flow = max(qm_values)  # Maximum flow given for pump in l/min
    print(f"[INFO] Maximum possible flow for Pump in l/min = {max_possible_flow}")
    results = []

    for point in points:
        flow_lpm = point["Flow"] * 6e-5  # Convert flow from mm^3/s to l/min
        interpolated_values = [
            interpolator(flow_lpm) for interpolator in interpolator
        ]  # Compute interpolated values

        # Calculate maximum possible velocity dependent on pump
        final_vel = (
            min(vel_cp, vel_cp * (max_possible_flow / flow_lpm))
            if flow_lpm > max_possible_flow
            else vel_cp
        )

        results.append(
            {
                "RPM": float(interpolated_values[0]),
                "Voltage": float(interpolated_values[1]),
                "Vel_CP_Max": final_vel,
            }
        )

    return results


if __name__ == "__main__":
    # Example input data
    char_curve = [
        [7, 100, 1],
        [40, 360, 10],
        [20, 220, 7],  # Arbitrary number of characteristic points
    ]

    char_curve.insert(0, [0, 0, 0])

    p = [
        {
            "Move": "G1",
            "X": 667.5,
            "Y": 2230.0,
            "Z": 30.0,
            "E_Rel": 10287.023,
            "Layer": 1,
            "Type": "wall_inner",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 25,
            "Flow": 120000,
            "Line": 2,
            "Point": 2,
            "Point_Info": "1",
        },
    ]

    veloci_p = 100.0  # Velocity in m/s
    pump_control = True

    # Compute RPM and Voltage
    result = get_rpm(p, char_curve, veloci_p)

    # Print results
    print("Interpolated values:", result)
