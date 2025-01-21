"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.6"

from pathlib import Path
import typing

# SETUP
from setup import directory_setup as disu
from setup import slicer_setup as slsu
from setup import robot_setup as rosu
from setup import rhino_setup as rhsu

# SLICER
# CURA
from slicer.cura import slice as slicu
from slicer.cura import get_default_arguments as defcu
from slicer.cura import get_user_arguments as usrcu
from slicer.cura import set_user_arguments as stacu
from slicer.cura import set_scaling_matrix as smacu

# ORCA

# G-CODE
from gcode import get_gcode as getgc
from gcode import min_max_values as mima
from gcode import simplify_gcode as smplf

# PLOT
from gcode import plot_gcode as plt

# KRL

# ROBOT

from robot.pre_processing import transf_gcode_to_robotroot as trfgc
from robot.processing import kinematiks_test as rokin

# RHINO

# ----------------GET SETUP PATH----------------
setup_path = str(Path(__file__).parent / "setup" / "setup.json")

# ----------------CONFIGURE DIRECTORY & FOLDERS----------------
# evaluate setup.json file for "Directory" information
directory_setup = disu.get_directory_setup(setup_path)

# Directories and Filenames
# STL file
INPUT_DIRECTORY_STL = directory_setup["input_directory"]
INPUT_FILE_STL = f"{directory_setup["input_name"]}.stl"
OUTPUT_DIRECTORY = directory_setup["output_directory"]
OUTPUT_NAME = directory_setup["output_name"]
# G-Code
INPUT_DIRECTORY_GCODE = OUTPUT_DIRECTORY
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

# Robot
ROBOT_ID = robot_settings["id"]
ROBOT_GEOMETRY = robot_settings["geometry"]

# Coordinate frames
ROBOT_BASE = robot_settings["base_coordinates"]
ROBOT_TOOL_OFFSET = robot_settings["tool_offset"]
ROBOT_TOOL_ORIENTATION = robot_settings["tool_orientation"]

# Start and End Coordinates
ROBOT_START_POSITION = robot_settings["start_position"]
ROBOT_END_POSITION = robot_settings["end_position"]
ROBOT_ROTATION_LIMIT = robot_settings["rotation_limit"]
ROBOT_ROTATION_SIGN = robot_settings["rotation_sign"]
ROBOT_ROTATION_OFFSET = robot_settings["rotation_offset"]

# Start- and End- Code of Robot
ROBOT_START_CODE = robot_settings["start_code"]
ROBOT_END_CODE = robot_settings["end_code"]


# Printbed measurements
BED_SIZE_X = robot_settings["bed_size"]["X"]
BED_SIZE_Y = robot_settings["bed_size"]["Y"]
BED_SIZE_Z = robot_settings["bed_size"]["Z"]

# Print speed
ROBOT_VEL_CP = robot_settings["print_speed"]


# ----------------SLICER CONFIGURATION----------------
# evaluate setup.json file for "Slicer" information
slicer_settings = slsu.get_slicer_settings(setup_path)

SLICER = slicer_settings["slicer_name"]
SLICER_CMD_PATH = slicer_settings["slicer_cmd_path"]
SLICER_CONFIG_FILE_PATH = slicer_settings["slicer_config_file_path"]
SLICER_ARGUMENTS = slicer_settings["slicer_arguments"]
SLICER_SCALING = slicer_settings["slicer_scaling"]

# ----------------RHINO CONFIGURATION----------------
# evaluate setup.json dile for "Rhino" information
rhino_settings = rhsu.get_rhino_settings(setup_path)
TYPE_VALUES = rhino_settings["TYPE_VALUES"]

# ----------------SLICING OF .STL FILE----------------
if SLICER == "CURA":
    CURA_SCALING = smacu.compute_scaling_and_rotation_matrix(SLICER_SCALING)
    # arguments from setup.json that also need to be handled by Cura
    preset_arguments_cura = {
        "machine_name": f"{ROBOT_ID} BEDSIZE: {BED_SIZE_X}x{BED_SIZE_Y}x{BED_SIZE_Z} [mm]",
        "machine_width": BED_SIZE_X,
        "machine_depth": BED_SIZE_Y,
        "machine_height": BED_SIZE_Z,
        "mesh_rotation_matrix": CURA_SCALING,
    }

    # collect all default slicing parameters
    default_arguments_cura = defcu.extract_slicer_arguments(SLICER_CONFIG_FILE_PATH)
    # validate user input with default slicing parameters
    user_arguments_cura = usrcu.validate_user_arguments(
        SLICER_ARGUMENTS, default_arguments_cura
    )
    # summarize all necessary user arguments for slicing process
    selected_arguments_cura = stacu.set_user_arguments(
        user_arguments=user_arguments_cura, additional_args=preset_arguments_cura
    )
    # slice STL with user arguments
    print("Starting to slice")
    sucess, message = slicu.slice(
        import_directory_stl=INPUT_DIRECTORY_STL,
        stl_file=INPUT_FILE_STL,
        export_directory_gcode=OUTPUT_DIRECTORY,
        export_file_gcode=OUTPUT_NAME,
        cura_engine_path=SLICER_CMD_PATH,
        cura_def_file=SLICER_CONFIG_FILE_PATH,
        additional_args=selected_arguments_cura,
    )
    print(message)
    print(f"Finished slicing {INPUT_FILE_STL}")

elif SLICER == "OPEN SLICER":
    print("Slicer not yet implemented")
elif SLICER == "ORCA":
    print("Slicer not yet implemented")
else:
    print("Choose valid Slicer")

# ----------------G-CODE IMPORT AND EVALUATION----------------
# Read the G-Code lines
gcode_lines = getgc.get_gcode_lines(INPUT_DIRECTORY_GCODE, INPUT_FILE_GCODE)

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

# # ----------------KRL FORMATING OF G-CODE----------------
# # Formats G-Code to KRL and appends tool-head orientation
# krl_lines = mdfkr.krl_format(
#     gcode_necessary,
#     a=TOOL_ORIENTATION_A,
#     b=TOOL_ORIENTATION_B,
#     c=TOOL_ORIENTATION_C,
#     vel=VEL_CP,
# )
#
# # for line in krl_lines:
# #     print(line)
#
# # Export of KRL-File
# expkr.export_to_src(
#     krl_lines, ROBOT_START_CODE, ROBOT_END_CODE, OUTPUT_DIRECTORY, OUTPUT_NAME
# )

# ----------------ROBOT SIMULATION----------------

# initialize robot
robot = rokin.RobotOPW(
    robot_id=ROBOT_ID,
    robot_geometry=ROBOT_GEOMETRY,
    robot_rotation_sign=ROBOT_ROTATION_SIGN,
    robot_rotation_limit=ROBOT_ROTATION_LIMIT,
    robot_rotation_offset=ROBOT_ROTATION_OFFSET,
)

# calculate Transformation matrix for point in $BASE (account for tool_offset) and return T for inverse kinematic
transf_matrix = []
joint_angles = []
for point in gcode_necessary:
    # calculate T for point in points
    point_transf_robotroot = trfgc.transform_gcode_point(
        point=point,
        tool_orientation=ROBOT_TOOL_ORIENTATION,
        tool_offset=ROBOT_TOOL_OFFSET,
        robot_base=ROBOT_BASE,
    )
    transf_matrix.append(point_transf_robotroot)

    # calculate all joint angles for point in points
    robot_angles = robot.inverse_kinematics(point_transf_robotroot)
    joint_angles.append(robot_angles)

for line in joint_angles:
    print(line)


# ----------------RHINO FILE----------------
# # Process G-Code for Rhino file
# extended_gcode = prcrh.process_points(gcode_necessary)
#
# # for line in extended_gcode:
# #     print(line)
#
# # Get filepath of generated Rhino file
# filepath = crtrh.initialize_rhino_file(
#     OUTPUT_DIRECTORY_RHINO, OUTPUT_FILE_RHINO, LAYER_MAX
# )
#
# # Generate toolpath in Rhino
# drgrh.create_geometry(extended_gcode, filepath, line_width=15, type_values=TYPE_VALUES)
# # Generate printbed in Rhino
# drprh.add_print_bed(
#     filepath, X_MAX=BED_SIZE_X, Y_MAX=BED_SIZE_Y, parent_layer="printbed"
# )
