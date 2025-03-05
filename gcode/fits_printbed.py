def check_fit_and_shift(bed_size, min_values, max_values, margin=0):
    """
    Überprüft, ob das Objekt auf das Druckbett passt und berechnet ggf. die minimale Verschiebung.

    :param bed_size: Dict {"X": bed_x, "Y": bed_y, "Z": bed_z} - Druckbettgröße
    :param min_values: Dict {"X": obj_min_x, "Y": obj_min_y, "Z": obj_min_z} - Minimale Koordinaten des Objekts
    :param max_values: Dict {"X": obj_max_x, "Y": obj_max_y, "Z": obj_max_z} - Maximale Koordinaten des Objekts
    :param margin: Abstand zum Rand des Druckbetts in mm (default: 50mm)
    :return: Tuple (fits_printbed, shift_dict)
             - fits_printbed: True/False, ob das Objekt passt
             - needs_offset: True/False, ob das Object verschoben werden muss um auf dem Druckbett zu liegen
             - shift_dict: {"dx": ..., "dy": ..., "dz": ...} falls True, sonst {}
    """

    # determine size printbed
    bed_x, bed_y, bed_z = bed_size["X"], bed_size["Y"], bed_size["Z"]

    # determine size object
    obj_size_x = max_values["x"] - min_values["x"]
    obj_size_y = max_values["y"] - min_values["y"]
    obj_size_z = max_values["z"] - min_values["z"]

    # Checks if object fits printbed
    if (
        obj_size_x > (bed_x - 2 * margin)
        or obj_size_y > (bed_y - 2 * margin)
        or obj_size_z > bed_z
    ):
        return False, False, {}  # doesn't fit

    # Shift in x-direction
    shift_x = max(margin - min_values["x"], 0)
    shift_x = min(shift_x, bed_x - margin - max_values["x"])

    # Shift in y-direction
    shift_y = max(margin - min_values["y"], 0)
    shift_y = min(shift_y, bed_y - margin - max_values["y"])

    # Shift in z-direction
    shift_z = max(0, -min_values["z"])

    return True, True, {"dx": shift_x, "dy": shift_y, "dz": shift_z}
