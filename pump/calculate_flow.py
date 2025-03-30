def get_flow(points: list[dict], vel_cp: float) -> list[float]:
    """
    DESCRIPTION:
    Calculates the flow for a given line in mm^3/s assuming a rectangular crosssection

    :param points: list of dicts of positional data and extrusion values
    :param vel_cp: velocity for printing / extrusion moves (G1)

    :return: List of flow values in mm^3/s ready to convert to RPM or voltage of given pump
    """

    flow = []
    # Flow = mm^3/s, therefor (assuming rectangular cross-section) w*h of line * velocity gives flow
    for point in points:
        flow_value = point["Linewidth"] * point["Layer_Height"] * vel_cp * 1000
        flow.append(flow_value)
    return flow
