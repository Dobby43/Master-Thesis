import numpy as np
from scipy.interpolate import interp1d


def get_rpm(
    points: list[dict],
    characteristic_curve: list[list[float]],
    vel_cp: float,
    vel_tvl: float,
    precision: int,
):
    """
    DESCRIPTION:
    Computes the required RPM and Voltage for a given pump characteristic curve based on input data.
    Also checks if the maximum flow rate of the pump is sufficient.

    :param points: List of points with flow information, where flow is given in mm^3/s (ideell berechnet)
    :param characteristic_curve: Pump characteristic curve [[QM (l/min), RPM, Voltage, ...], ...] with arbitrary additional parameters
    :param vel_cp: print velocity that should be reached in m/s
    :param vel_tvl: travel velocity in m/s
    :param precision: number of decimal places saved

    :return: List with [{RPM, Voltage, Vel_CP_Max}] where Vel_CP_Max is in m/s
    """
    # Extracting and sorting values from the characteristic curve by flow
    data = np.array(characteristic_curve)
    sorted_data = data[np.argsort(data[:, 1])]  # sort for RPM
    qm_values = sorted_data[:, 0]  # Flow values in l/min
    parameter_values = sorted_data[
        :, 1:
    ].T  # List of RPM and Voltage values [[RPM.sorted],[Voltage.sorted]]

    # Create interpolation functions with clamping at boundary values
    def clamped_interp(qm_vals, param_vals):
        f = interp1d(
            qm_vals,
            param_vals,
            kind="linear",
            bounds_error=False,
            fill_value=(param_vals[0], param_vals[-1]),
        )
        return lambda x: f(
            min(x, qm_vals[-1])
        )  # Fixing so maximum flow is pump dependent

    interpolators = [clamped_interp(qm_values, param) for param in parameter_values]

    max_possible_flow = max(qm_values)  # Maximum flow given for pump in l/min
    results = []

    for point in points:
        move = point["Move"]
        flow_lpm = point["Flow"] * 6e-5  # Calculated flow in l/min
        coordinates = round(point["X"], 2), round(point["Y"], 2), round(point["Z"], 2)

        interpolated_values = [
            f(flow_lpm) for f in interpolators
        ]  # Compute clamped interpolated values

        # Calculate maximum possible velocity dependent on pump (linearly)
        final_vel = (
            min(vel_cp, vel_cp * (max_possible_flow / flow_lpm))
            if flow_lpm > max_possible_flow and flow_lpm > 0
            else vel_cp
        )
        if final_vel < vel_cp:
            print(f"[ERROR] Pump capacity limited to {max_possible_flow} l/min")
            print(
                f"[WARNING] Printing velocity reduced to {round(final_vel,2)} m/s for movement to point {coordinates}"
            )

        results.append(
            {
                "RPM": round(float(interpolated_values[0]), precision),
                "Voltage": round(float(interpolated_values[1]), precision),
                "Vel_CP_Max": (
                    round(float(final_vel), precision) if move == "G1" else vel_tvl
                ),
            }
        )

    return results


if __name__ == "__main__":
    # Example input data
    char_curve = [
        [0, 0, 0],
        [2, 100, 1],
        [3, 220, 7],
        [3.3, 360, 10],  # Sorted by flow ascending
    ]

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
            "Linewidth": 20,
            "Flow": 1200000,
            "Line": 2,
            "Point": 2,
            "Point_Info": "1",
        },
        {
            "Move": "G0",
            "X": 667.5,
            "Y": 2230.0,
            "Z": 30.0,
            "E_Rel": 10287.023,
            "Layer": 1,
            "Type": "wall_inner",
            "Layer_Height": 15.0,
            "Reachable": True,
            "Linewidth": 0,
            "Flow": 0,
            "Line": 2,
            "Point": 2,
            "Point_Info": "0",
        },
    ]

    veloci_p = 10.0  # Velocity in m/s
    veloci_t = 10.0
    pump_control = True

    # Compute RPM and Voltage
    result = get_rpm(p, char_curve, veloci_p, veloci_t, 2)

    # Print results
    print("Interpolated values:", result)
