"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.4"

from pathlib import Path

from setup import directory_setup as disu
from setup import slicer_setup as slsu
from setup import robot_setup as rosu
from setup import rhino_setup as rhsu

# gcode
from gcode import get_gcode
from gcode import min_max_values as mima
from gcode import simplify_gcode as smplf

# plot
from gcode import plot_gcode as plt

# krl
from krl import modify_to_krl as mdf
from krl import export_to_src as exp

# rhino
from rhino import create_rhino as crt
from rhino import process_gcode as prc
from rhino import draw_gcode as drg
from rhino import draw_printbed as drp

# ----------------GET SETUP PATH----------------
setup_path = str(Path(__file__).parent / "setup" / "setup.json")

# ----------------CONFIGURE DIRECTORY & FOLDERS----------------
# evaluate setup.json file for "Directory" information
directory_setup = disu.get_directory_setup(setup_path)

# Directories and Filenames
INPUT_DIRECTORY_STL = directory_setup["input_directory"]
INPUT_NAME_STL = directory_setup["input_name"]
OUTPUT_DIRECTORY = directory_setup["output_directory"]
OUTPUT_NAME = directory_setup["output_name"]

# G-Code
INPUT_DIRECTORY_GCODE = INPUT_DIRECTORY_STL
INPUT_FILE_GCODE = f"{OUTPUT_NAME}.gcode"
# KRL Code
OUTPUT_DIRECTORY_KRL = OUTPUT_DIRECTORY
OUTPUT_FILE_KRL = f"{OUTPUT_NAME}.src"
# Rhino file
OUTPUT_DIRECTORY_RHINO = OUTPUT_DIRECTORY
OUTPUT_FILE_RHINO = f"{OUTPUT_NAME}.3dm"

# ----------------ROBOT CONFIGURATION----------------
# evaluate setup.json file for "Robot" information
robot_settings = rosu.get_robot_settings(setup_path)
BED_SIZE_X = robot_settings["bed_size"]["X"]
BED_SIZE_Y = robot_settings["bed_size"]["Y"]
BED_SIZE_Z = robot_settings["bed_size"]["Z"]

# Tool-head orientation
TOOL_ORIENTATION_A = robot_settings["tool_orientation"]["A"]
TOOL_ORIENTATION_B = robot_settings["tool_orientation"]["B"]
TOOL_ORIENTATION_C = robot_settings["tool_orientation"]["C"]

# Coordinate frames
BASE = robot_settings["base_coordinates"]
TOOL = robot_settings["tool_coordinates"]

# Start and End Coordinates
START_POSITION = robot_settings["start_position"]
END_POSITION = robot_settings["end_position"]

# Print speed
VEL_CP = robot_settings["print_speed"]

# Start- and End- Code of Robot
robot_start_code = robot_settings["start_code"]
robot_end_code = robot_settings["end_code"]

# ----------------SLICER CONFIGURATION----------------
# evaluate setup.json file for "Slicer" information
slicer_settings = slsu.get_slicer_settings(setup_path)

SLICER = slicer_settings["slicer_name"]
SLICER_CMD_PATH = slicer_settings["slicer_cmd_path"]
SLICER_CONFIG_FILE_PATH = slicer_settings["slicer_config_file_path"]
SLICER_ARGUMENTS = slicer_settings["slicer_arguments"]


# ----------------RHINO CONFIGURATION----------------
# evaluate setup.json dile for "Rhino" information
rhino_settings = rhsu.get_rhino_settings(setup_path)
TYPE_VALUES = rhino_settings["TYPE_VALUES"]


# ----------------SLICING OF .STL FILE----------------
# print("Starting to slice")
# sucess, message = slicu.slice(
#     stl_file=INPUT_FILE_STL,
#     INPUT_directory_stl=INPUT_DIRECTORY_STL,
#     export_directory_gcode=EXPORT_DIRECTORY_GCODE,
#     export_file_gcode=EXPORT_FILE_GCODE,
# )
# print(message)
# print(f"Finished slicing {INPUT_FILE_GCODE}")

# ----------------G-CODE IMPORT AND EVALUATION----------------
# Read the G-Code lines
gcode_lines = get_gcode.get_gcode_lines(INPUT_DIRECTORY_GCODE, INPUT_FILE_GCODE)

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
gcode_necessary = smplf.process_gcode(gcode_lines, SLICER, TYPE_VALUES)

for line in gcode_necessary:
    print(line)

# Gets maximum layer number
LAYER_MAX = gcode_necessary[-1]["Layer"]


# ----------------PYVISTA PLOT----------------
plotter = plt.plot_bed(
    bed_size_x=BED_SIZE_X,
    bed_size_y=BED_SIZE_Y,
    bed_size_z=BED_SIZE_Z,
)

# Füge den G-Code-Pfad dem vorhandenen Plotter hinzu
plt.plot_gcode(
    plotter=plotter,
    processed_gcode=gcode_necessary,
    layers="all",
    type_values=TYPE_VALUES,
)


# ----------------KRL FORMATING OF G-CODE----------------
# Formats G-Code to KRL and appends tool-head orientation
krl_lines = mdf.krl_format(
    gcode_necessary,
    a=TOOL_ORIENTATION_A,
    b=TOOL_ORIENTATION_B,
    c=TOOL_ORIENTATION_C,
    end_pos=END_POSITION,
    vel=VEL_CP,
)

# for line in krl_lines:
#     print(line)

# Export of KRL-File
exp.export_to_src(
    krl_lines, robot_start_code, robot_end_code, OUTPUT_DIRECTORY, OUTPUT_NAME
)

# ----------------RHINO FILE----------------
# Process G-Code for Rhino file
extended_gcode = prc.process_points(gcode_necessary)

# for line in extended_gcode:
#     print(line)

# Get filepath of generated Rhino file
filepath = crt.initialize_rhino_file(
    OUTPUT_DIRECTORY_RHINO, OUTPUT_FILE_RHINO, LAYER_MAX
)

# Generate toolpath in Rhino
drg.create_geometry(extended_gcode, filepath, line_width=15, type_values=TYPE_VALUES)
# Generate printbed in Rhino
drp.add_print_bed(filepath, X_MAX=BED_SIZE_X, Y_MAX=BED_SIZE_Y, parent_layer="printbed")
