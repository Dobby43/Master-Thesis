"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.0"

# Example usage in main.py
from gcode import get_gcode
from gcode import simplify_gcode as splf

# Directory and file name
DIRECTORY = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\G_Code"
FILE_NAME = r"Cura_25_10_CFFFP_xyzCalibration_cube.gcode"

# Read the G-Code lines
gcode_lines = get_gcode.get_gcode_lines(DIRECTORY, FILE_NAME)

# Simplify_gcode
# Gets necessary G-Code lines
gcode_necessary = splf.necessary_gcode(gcode_lines)
# Deletes feed information from G-Code lines
gcode_no_feed = splf.delete_feed(gcode_necessary)
# Deletes extrusion information from G-Code lines
gcode_no_extrusion = splf.delete_extrusion(gcode_no_feed)
# Cleans G-Code from blank lines
gcode_cleaned = splf.clean_gcode(gcode_no_extrusion)
# Formates G-Code according to KRL
gcode_formatted = splf.format_gcode_lines(gcode_cleaned, 2)
# Appends Z-Value t

for line in gcode_formatted:
    print(line)


# Modifies the G-Code lines

# Append z-height
