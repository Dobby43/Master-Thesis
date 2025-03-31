import matplotlib.pyplot as plt
from typing import List
import numpy as np


def plot_pump_curve(characteristic_curve: List[List[float]]):
    """
    Plot of the characteristic pump curve with two y-axis (flow in [l/min] and voltage [V])
    Saves the picture in the current working directory as characteristic_curve_plot.png

    :param characteristic_curve: nested list of flow,rpm,voltage for specific points along a given characteristic curve from the maufacturer
    """

    # Set fontsize for the plot
    fontsize = 4
    # Sort list of lists by the first value in the nested list
    curve_np = np.array(characteristic_curve)
    curve_sorted = curve_np[np.argsort(curve_np[:, 0])]
    curve = np.array(curve_sorted)

    # Assign values from input data to type
    flow_l_min = curve[:, 0]
    rpm = curve[:, 1]
    voltage = curve[:, 2]

    # Plot the sorted list
    fig, ax1 = plt.subplots(
        figsize=(6.5 / 2.54, 3.5 / 2.54), dpi=300, constrained_layout=True
    )

    color_flow = "#0065bd"
    ax1.set_xlabel("RPM [1/min]", fontsize=fontsize)
    ax1.tick_params(axis="x", labelsize=fontsize)
    ax1.set_ylabel("Flow [l/min]", color=color_flow, fontsize=fontsize)
    ax1.plot(rpm, flow_l_min, "o-", color=color_flow, markersize=3)
    ax1.tick_params(axis="y", labelcolor=color_flow, labelsize=fontsize)
    ax1.grid(visible=True, which="both", linestyle="--", linewidth=0.5, alpha=0.8)

    max_rpm = int(np.ceil(curve[-1, 1]))
    max_flow = int(np.ceil(curve[-1, 0]))
    max_voltage = int(np.ceil(curve[-1, 2]))

    xtick_step = max(1, round(max_rpm / 5)) if max_rpm > 0 else 1
    ytick_step = max(1, round(max_flow / 5)) if max_flow > 0 else 1

    ax1.set_xticks(np.arange(0, max_rpm + xtick_step, xtick_step))
    ax1.set_yticks(np.arange(0, max_flow + ytick_step, ytick_step))

    ax2 = ax1.twinx()
    color_voltage = "#e37222"
    ax2.set_ylabel("Voltage [V]", color=color_voltage, fontsize=fontsize)
    ax2.plot(rpm, voltage, "s--", color=color_voltage, markersize=3)
    ax2.tick_params(axis="y", labelcolor=color_voltage, labelsize=fontsize)

    voltage_step = max(1, round(max_voltage / 5)) if max_voltage > 0 else 1
    ax2.set_yticks(np.arange(0, max_voltage + voltage_step, voltage_step))

    fig.suptitle("Characteristic Curve", fontsize=fontsize + 1)

    fig.savefig("characteristic_curve_plot.png", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    example_curve = [
        [0, 0, 0],
        [1, 100, 2],
        [3, 300, 10],
        [2, 200, 3],
    ]
    plot_pump_curve(example_curve)
    print("Plot saved under 'characteristic_curve.png'")
