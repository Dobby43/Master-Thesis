"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.0"

# Example usage in main.py
from gcode import get_gcode
from gcode import simplify_gcode as smplf
from gcode import plot_gcode as plt
from krl import modify_gcode as mdf


# Directory and file name
DIRECTORY = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\G_Code"
FILE_NAME = r"Cura_02_11_CFFFP_3DBenchy.gcode"

# Print-bed Size
BED_SIZE_X = 1200
BED_SIZE_Y = 4500
BED_SIZE_Z = 2000

# Tool-head orientation
ORIENTATION_A = 0
ORIENTATION_B = 0
ORIENTATION_C = 180

# Read the G-Code lines
gcode_lines = get_gcode.get_gcode_lines(DIRECTORY, FILE_NAME)

# Simplify_gcode
# Gets min X, Y and Z values
min_values = smplf.get_min_values(gcode_lines)
X_MIN = min_values["x_min"]
Y_MIN = min_values["y_min"]
# Gets max X, Y and Z values
max_values = smplf.get_max_values(gcode_lines)
X_MAX = max_values["x_max"]
Y_MAX = max_values["y_max"]
Z_MAX = max_values["z_max"]
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
gcode_formatted = smplf.format_gcode(gcode_updated, 2)

for line in gcode_formatted:
    print(line)


# Erstelle das Druckbett und speichere das Plotter-Objekt
plotter = plt.plot_bed(
    bed_size_x=BED_SIZE_X,
    bed_size_y=BED_SIZE_Y,
    bed_size_z=BED_SIZE_Z,
)

# Füge den G-Code-Pfad dem vorhandenen Plotter hinzu
plt.plot_gcode_path(plotter=plotter, gcode_lines=gcode_formatted, layers="2")

# Modifies the G-Code lines
# appends toolhead orientation
# krl_toolhead = mdf.toolhead_orientation(
#     gcode_formatted, a=ORIENTATION_A, b=ORIENTATION_B, c=ORIENTATION_C
# )
#
# for line in krl_toolhead:
#     print(line)
