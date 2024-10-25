import re

from fontTools.varLib.models import nonNone

dictionary_necessary = {"G0", "G1", ";Layer", ";Type"}


def necessary_gcode(gcode: list) -> list:
    simplified_gcode = []
    for line in gcode:
        # Prüfe, ob die Zeile mit "G1", "G0" oder ";" beginnt
        for item in dictionary_necessary:
            if line.startswith(item):
                simplified_gcode.append(line)  # Zeile hinzufügen
    return simplified_gcode


def delete_feed(gcode: list) -> list:
    modified_lines = []
    for line in gcode:
        # Remove any existing F values (e.g., F1234.56)
        line = re.sub(r" ?F[\d\.]+\b", "", line).strip()

        # Add the modified line to the result list
        modified_lines.append(line)

    return modified_lines


def delete_extrusion(gcode: list) -> list:
    modified_lines = []
    for line in gcode:
        # Remove any existing F values (e.g., F1234.56)
        line = re.sub(r" ?E[\d\.]+\b", "", line).strip()

        # Add the modified line to the result list
        modified_lines.append(line)

    return modified_lines
