def check_fit_and_shift(
    bed_size: dict[str, float],
    min_values: dict[str, float],
    max_values: dict[str, float],
    margin=0,
) -> tuple[bool, bool, dict]:
    """
    DESCRIPTION:
    Determines if the object fits on printbed and if it is located on the printbed

    :param bed_size: Dict {"x": bed_x, "y": bed_y, "z": bed_z} - printbed size
    :param min_values: Dict {"x": obj_min_x, "y": obj_min_y, "z": obj_min_z} - minimum coordinates of object
    :param max_values: Dict {"x": obj_max_x, "y": obj_max_y, "z": obj_max_z} - maximum coordinates of object
    :param margin: safety distance from edge of printbed to the object
    :return: Tuple (fits_printbed, needs_offset, shift_dict)
             - fits_printbed: True/False, if the object fits the printbed
             - needs_offset: True/False, if the object needs to be shifted to locate fully on the printbed
             - shift_dict: {"dx": ..., "dy": ..., "dz": ...} if True, else {}
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
    shift_z = max(-min_values["z"], 0)
    if shift_x or shift_y or shift_z != 0:
        return (
            True,
            False,
            {"dx": shift_x, "dy": shift_y, "dz": shift_z},
        )  # Fits, but needs to be shifted
    else:
        return True, True, {}


if __name__ == "__main__":
    bedsize = {"X": 1200, "Y": 4500, "Z": 2000}
    min_val = {"x": 400, "y": 0, "z": 0}
    max_val = {"x": 500, "y": 4500, "z": 2000}

    fit = check_fit_and_shift(bedsize, min_val, max_val)

    print(fit)
