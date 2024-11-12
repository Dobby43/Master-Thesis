"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.1"

# Example usage in main.py
from gcode import get_gcode
from gcode import min_max_values as mima
from gcode import simplify_gcode as smplf
from gcode import plot_gcode as plt
from krl import modify_to_krl as mdf
from robot import robot_start_code as rsc
from robot import robot_end_code as rec
from export import export as exp

# IMPORT_DIRECTORY and IMPORT_FILE
IMPORT_DIRECTORY = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\G_Code"
IMPORT_FILE = r"Cura_02_11_CFFFP_3DBenchy.gcode"

# Slicer used
SLICER = "CURA"  # Sets dictionary used for essential G-Code lines in simplify_gcode

# EXPORT_DIRECTORY and EXPORT_FILE
EXPORT_DIRECTORY = r"C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\KRL_Files\KRL_EXPORT_PYTHON\V1.0"
EXPORT_FILE = "Cura_02_11_CFFFP_FlowCalibrationCube"

# Print-bed Size
BED_SIZE_X = 1200
BED_SIZE_Y = 4500
BED_SIZE_Z = 2000

# Tool-head orientation
ORIENTATION_A = 0
ORIENTATION_B = 0
ORIENTATION_C = 180

# Coordinate frames
BASE = "{X 1460.9, Y -2237.66, Z 268.5, A 0.0, B 0.0, C 0.0}"
TOOL = "{X -10.99, Y -0.86, Z 917.61, A 0.0, B 0.0, C 0.0}"
# Start configuration
ZERO_POSITION = "{A1 75.0, A2 -90.0, A3 90.0, A4 0.0, A5 90.0, A6 0.0}"

# Jerk mode parameters
T_1 = "{VEL 20,ACC 100,APO_DIST 10}"
T_2 = "{VEL 20,ACC 100,APO_DIST 10}"
AUT = "{VEL 20,ACC 100,APO_DIST 10}"
DEFAULT = "{VEL 20,ACC 100,APO_DIST 10}"

# Motion parameters
VEL_CP = 0.25  # Continues path velocity at start in [m/s]
VEL_PRT = 0.35  # Velocity during print
VEL_ORI1 = 100  # [deg/sec]
VEL_ORI2 = 100  # [deg/sec]
ADVANCE = 3  # Number of code lines calculated in advance

# Read the G-Code lines
gcode_lines = get_gcode.get_gcode_lines(IMPORT_DIRECTORY, IMPORT_FILE)

# Simplify_gcode
# Gets min X, Y and Z values
min_values = mima.get_min_values(gcode_lines)
X_MIN = min_values["x_min"]
Y_MIN = min_values["y_min"]
# Gets max X, Y and Z values
max_values = mima.get_max_values(gcode_lines)
X_MAX = max_values["x_max"]
Y_MAX = max_values["y_max"]
Z_MAX = max_values["z_max"]
# Gets necessary G-Code lines
gcode_necessary = smplf.process_gcode(gcode_lines, SLICER)


for line in gcode_necessary:
    print(line)


# Erstelle das Druckbett und speichere das Plotter-Objekt
plotter = plt.plot_bed(
    bed_size_x=BED_SIZE_X,
    bed_size_y=BED_SIZE_Y,
    bed_size_z=BED_SIZE_Z,
)

# Füge den G-Code-Pfad dem vorhandenen Plotter hinzu
plt.plot_gcode(plotter=plotter, processed_gcode=gcode_necessary, layers="5-6")

# # Modifies the G-Code lines
# # formats G-Code to KRL and appends tool-head orientation
# krl_lines = mdf.krl_format(
#     gcode_formatted,
#     a=ORIENTATION_A,
#     b=ORIENTATION_B,
#     c=ORIENTATION_C,
#     end_pos=ZERO_POSITION,
#     vel=VEL_PRT,
# )
# for line in krl_lines:
#     print(line)
#
#
# # Robot configuration
# # Robot start code
# setup = rsc.project_setup(EXPORT_FILE)
# init = rsc.initialisation()
# sta_conc_print = rsc.start_concrete_printing()
# bco = rsc.block_coordinates(
#     base=BASE,
#     tool=TOOL,
#     t_1=T_1,
#     t_2=T_2,
#     aut=AUT,
#     default=DEFAULT,
#     start_pos=ZERO_POSITION,
# )
# move = rsc.motion(vel_cp=VEL_CP, vel_ori1=VEL_ORI1, vel_ori2=VEL_ORI2, adv=ADVANCE)
#
# # Robot end code
# end_conc_print = rec.end_concrete_printing()
#
# # Export of KRL-File
# exp.export_to_src(
#     setup=setup,
#     init=init,
#     sta_conc_print=sta_conc_print,
#     end_conc_print=end_conc_print,
#     bco=bco,
#     move=move,
#     code=krl_lines,
#     file_directory=EXPORT_DIRECTORY,
#     file_name=EXPORT_FILE,
# )
