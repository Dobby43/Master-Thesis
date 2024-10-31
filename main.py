"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.0"

# Example usage in main.py
from gcode import get_gcode
from gcode import simplify_gcode as smplf
from gcode import modify_gcode as mdf

# Directory and file name
DIRECTORY = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\G_Code"
FILE_NAME = r"Cura_23_10_CFFFP_FlowCalibrationCube.gcode"

# Toolhead orientation
ORIENTATION_A = -180
ORIENTATION_B = 0
ORIENTATION_C = 180

# Read the G-Code lines
gcode_lines = get_gcode.get_gcode_lines(DIRECTORY, FILE_NAME)

# Simplify_gcode
# Gets necessary G-Code lines
gcode_necessary = smplf.necessary_gcode(gcode_lines)
# Deletes feed information from G-Code lines
gcode_no_feed = smplf.delete_feed(gcode_necessary)
# Deletes extrusion information from G-Code lines
gcode_no_extrusion = smplf.delete_extrusion(gcode_no_feed)
# Cleans G-Code from blank lines
gcode_cleaned = smplf.clean_gcode(gcode_no_extrusion)
# Append and update Z-Value for every line
gcode_updated = smplf.append_z_height(gcode_cleaned)
# Formates G-Code according to KRL
gcode_formatted = smplf.format_gcode(gcode_updated, 1)

# for line in gcode_formatted:
#     print(line)


# Modifies the G-Code lines
# appends toolhead orientation
krl_toolhead = mdf.toolhead_orientation(
    gcode_formatted, a=ORIENTATION_A, b=ORIENTATION_B, c=ORIENTATION_C
)

for line in krl_toolhead:
    print(line)
