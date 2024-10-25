"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.0"

# Example usage in main.py
from gcode import get_gcode
from gcode.simplify_gcode import necessary_gcode, delete_feed, delete_extrusion

# Directory and file name
directory = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\G_Code"
file_name = r"Cura_25_10_CFFFP_xyzCalibration_cube.gcode"

# Read the G-code lines
gcode_lines = get_gcode.get_gcode_lines(directory, file_name)
for line in gcode_lines:
    print(line.strip())


# Simplifies G-Code list
simplify_gcode = necessary_gcode(gcode_lines)
for line in simplify_gcode:
    print(line.strip())

# Deletes feed
simplify_gcode = delete_feed(simplify_gcode)
for line in simplify_gcode:
    print(line.strip())

# Deletes extrusion
simplify_gcode = delete_extrusion(simplify_gcode)
for line in simplify_gcode:
    print(line.strip())
# Modifies the G-Code lines

# Append z-height
