from typing import List, Dict, Union


def filter_retracts(
    simplified_gcode: List[Dict[str, Union[str, float, int, None]]]
) -> List[Dict[str, Union[str, float, int, None]]]:
    """
    Filters G-code entries based on retract logic.
    If retract=False, all entries between retract and protract are excluded,
    and the protract entry is replaced with a travel entry.

    Parameters:
        simplified_gcode: List of G-code entries processed by simplify_gcode.

    Returns:
        List of G-code entries with retract and protract logic applied.
    """

    filtered_gcode = []
    skip_block = False

    for entry in simplified_gcode:
        # Start of retract block
        if entry["Type"] == "retract":
            skip_block = True
            continue

        # End of retract block (protract)
        if entry["Type"] == "protract":
            # Add a travel entry instead of the protract entry
            travel_entry = {
                "Move": "G0",
                "X": entry["X"],
                "Y": entry["Y"],
                "Z": entry["Z"],
                "E_rel": 0,
                "Layer": entry["Layer"],
                "Type": "travel",
                "Layer_Height": entry["Layer_Height"],
            }
            filtered_gcode.append(travel_entry)
            skip_block = False  # Stop skipping lines
            continue
        # TODO: Filter dublicats
        # Skip entries between retract and protract
        if skip_block:
            continue

        # Add all other entries
        filtered_gcode.append(entry)

    return filtered_gcode
