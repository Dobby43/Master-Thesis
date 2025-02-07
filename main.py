"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.6"

from pathlib import Path
import numpy as np

# SETUP
from setup import directory_setup as disu
from setup import slicer_setup as slsu
from setup import robot_setup as rosu
from setup import pump_setup as pusu
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
from gcode import filter_gcode as filtr

# PLOT
from gcode import plot_gcode as plt

# KRL
from krl import modify_to_krl_2 as mdfkr
from krl import export_to_src as expkr

# ROBOT
from robot.pre_process.mathematical_operators import Transformation
from robot.pre_process.mathematical_operators import Rotation
from robot.process import kinematiks_test as rokin

# RHINO
from rhino.process import extend_gcode as prcrh
from rhino.process import draw_gcode_2 as drgrh
from rhino.process import draw_printbed as drprh
from rhino.pre_process import create_rhino as crtrh

# ----------------GET SETUP PATH----------------
setup_path = str(Path(__file__).parent / "setup" / "setup.json")

# ----------------CONFIGURE DIRECTORY & FOLDERS----------------
# evaluate setup.json file for "Directory" information
directory_setup = disu.get_directory_setup(setup_path)

# Directories and Filenames
# STL file
INPUT_DIRECTORY_STL = directory_setup["input_directory"]
INPUT_FILE = directory_setup["input_name"]
INPUT_FILE_STL = f"{INPUT_FILE}.stl"
OUTPUT_DIRECTORY = directory_setup["output_directory"]
OUTPUT_NAME = directory_setup["output_name"]
# G-Code
INPUT_DIRECTORY_GCODE = OUTPUT_DIRECTORY  # for pre-sliced G-Code set from OUTPUT_DIRECTORY to INPUT_DIRECTORY_STL and give Input directory of G-Code
INPUT_FILE_GCODE = f"{OUTPUT_NAME}.gcode"  # for pre-sliced G-Code set from OUTPUT_NAME to INPUT_FILE_STL and give name of G-CODE in setup.json
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
ROBOT_NOZZLE_DIAMETER = robot_settings["nozzle_diameter"]
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
ROBOT_START_CODE_JSON = robot_settings["start_code"]
ROBOT_END_CODE_JSON = robot_settings["end_code"]


# Printbed measurements
BED_SIZE_X = robot_settings["bed_size"]["X"]
BED_SIZE_Y = robot_settings["bed_size"]["Y"]
BED_SIZE_Z = robot_settings["bed_size"]["Z"]

# Print speed
ROBOT_VEL_CP = robot_settings["print_speed"]

# ----------------PUMP CONFIGURATION----------------
pump_settings = pusu.get_pump_settings(setup_path)

PUMP_RETRACT = pump_settings["retract"]


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
TYPE_VALUES = rhino_settings["type_values"]
LINE_WIDTHS = rhino_settings["line_widths"]


# ----------------SLICING OF .STL FILE----------------
if SLICER == "cura":
    CURA_SCALING = smacu.compute_scaling_and_rotation_matrix(SLICER_SCALING)
    # arguments from setup.json that also need to be handled by Cura
    preset_arguments_cura = {
        "machine_name": f"{ROBOT_ID} BEDSIZE: {BED_SIZE_X}x{BED_SIZE_Y}x{BED_SIZE_Z} [mm]",
        "machine_width": BED_SIZE_X,
        "machine_depth": BED_SIZE_Y,
        "machine_height": BED_SIZE_Z,
        "machine_nozzle_size": ROBOT_NOZZLE_DIAMETER,
        "mesh_rotation_matrix": CURA_SCALING,
        "support_enable": "false",
        "prime_blob_enable": "false",
        "adhesion_type": "none",
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

elif SLICER == r"open slicer":  # TODO: typos ausgleichen
    print("Slicer not yet implemented")
elif SLICER == "orca":
    print("Slicer not yet implemented")
else:
    print("Choose valid Slicer")

# ----------------INITIALIZING ROBOT----------------

# initialize robot
robot = rokin.RobotOPW(
    robot_id=ROBOT_ID,
    robot_geometry=ROBOT_GEOMETRY,
    robot_rotation_sign=ROBOT_ROTATION_SIGN,
    robot_rotation_limit=ROBOT_ROTATION_LIMIT,
    robot_rotation_offset=ROBOT_ROTATION_OFFSET,
)

# ----------------G-CODE IMPORT AND EVALUATION----------------
# Read the G-Code lines
gcode_lines = getgc.get_gcode_lines(INPUT_DIRECTORY_GCODE, INPUT_FILE_GCODE)

# Simplify_gcode
# Gets min X, Y and Z values
min_values = mima.get_min_values(gcode_lines)
X_MIN = min_values["x_min"]
Y_MIN = min_values["y_min"]
Z_MIN = min_values["z_min"]
# Gets max X, Y and Z values
max_values = mima.get_max_values(gcode_lines)
X_MAX = max_values["x_max"]
Y_MAX = max_values["y_max"]
Z_MAX = max_values["z_max"]

# Calculation of Start and End coordinates
START_POS_ROBOTROOT = robot.forward_kinematics(ROBOT_START_POSITION, ROBOT_TOOL_OFFSET)
END_POS_ROBOTROOT = robot.forward_kinematics(ROBOT_END_POSITION, ROBOT_TOOL_OFFSET)

T_ROBOTROOT_BASE = Transformation.from_rotation_and_translation(
    Rotation.from_euler_angles(ROBOT_BASE["C"], ROBOT_BASE["B"], ROBOT_BASE["A"]),
    [ROBOT_BASE["X"], ROBOT_BASE["Y"], ROBOT_BASE["Z"]],
)
T_BASE_ROBOTROOT = Transformation.invert(T_ROBOTROOT_BASE)

START_POS_BASE = np.round(T_ROBOTROOT_BASE @ START_POS_ROBOTROOT, 2)
END_POS_BASE = np.round(T_ROBOTROOT_BASE @ END_POS_ROBOTROOT, 2)

ROBOT_START_POSITION = {
    "X": float(START_POS_BASE[0, 3]),
    "Y": float(START_POS_BASE[1, 3]),
    "Z": float(START_POS_BASE[2, 3]),
}
ROBOT_END_POSITION = {
    "X": float(END_POS_BASE[0, 3]),
    "Y": float(END_POS_BASE[1, 3]),
    "Z": float(END_POS_BASE[2, 3]),
}

# print(f"Start Pos Robotroot \n{START_POS_ROBOTROOT}\n")
# print(f"End pos Robotroot \n{END_POS_ROBOTROOT}\n")
# print(f"T_ROBOTROOT_BASE \n{T_ROBOTROOT_BASE}\n")
# print(f"T_BASE_ROBOTROOT \n{Transformation.invert(T_ROBOTROOT_BASE)}\n")
# print(f"START_POS_BASE \n{START_POS_BASE}\n")
# print(f"END_POS_BASE \n{END_POS_BASE}\n")
#
# print(f"ROBOT_START_POSITION \n{ROBOT_START_POSITION}\n")
# print(f"ROBOT_END_POSITION \n{ROBOT_END_POSITION}\n")


# Gets necessary G-Code lines
gcode_necessary = smplf.simplify_gcode(
    gcode_lines, SLICER, TYPE_VALUES, X_MIN, Y_MIN, Z_MIN
)
# Gets maximum layer number
LAYER_MAX = gcode_necessary[-1]["Layer"]

# ----------------PUMP IMPLEMENTATION
if PUMP_RETRACT is False:
    gcode_filtered = filtr.filter_retracts(gcode_necessary)
else:
    gcode_filtered = gcode_necessary

for line in gcode_filtered:
    print(line)

gcode_line_width = 0


# ----------------PYVISTA PLOT----------------
plotter = plt.plot_bed(
    bed_size_x=BED_SIZE_X,
    bed_size_y=BED_SIZE_Y,
    bed_size_z=BED_SIZE_Z,
)

# Füge den G-Code-Pfad dem vorhandenen Plotter hinzu
plt.plot_gcode(
    plotter=plotter,
    processed_gcode=gcode_filtered,
    layers="all",
    type_values=TYPE_VALUES,
)

# ----------------KRL FORMATING OF G-CODE----------------
# Formats G-Code to KRL and appends tool-head orientation
krl_lines = mdfkr.krl_format(
    gcode_necessary,
    type_mapping=TYPE_VALUES,
    a=ROBOT_TOOL_ORIENTATION["A"],
    b=ROBOT_TOOL_ORIENTATION["B"],
    c=ROBOT_TOOL_ORIENTATION["C"],
    vel=ROBOT_VEL_CP,
    x_max=BED_SIZE_X,
    y_max=BED_SIZE_Y,
    z_max=BED_SIZE_Z,
)

for line in krl_lines:
    print(line)

# Export of KRL-File
expkr.export_to_src(
    krl_lines, ROBOT_START_CODE_JSON, ROBOT_END_CODE_JSON, OUTPUT_DIRECTORY, OUTPUT_NAME
)

# ----------------ROBOT SIMULATION----------------

# calculate Transformation matrix for point in $BASE (account for tool_offset) and return T for inverse kinematic
# transf_matrix = []
# joint_angles = []
# for point in gcode_necessary:
#     # calculate T for point in points
#     point_transf_robotroot = trfgc.transform_gcode_point(
#         point=point,
#         tool_orientation=ROBOT_TOOL_ORIENTATION,
#         tool_offset=ROBOT_TOOL_OFFSET,
#         robot_base=ROBOT_BASE,
#     )
#     transf_matrix.append(point_transf_robotroot)
#
#     # calculate all joint angles for point in points
#     robot_angles = robot.inverse_kinematics(point_transf_robotroot)
#     joint_angles.append(robot_angles)
#
# for line in joint_angles:
#     print(line)


# ----------------RHINO FILE----------------
# Process G-Code for Rhino file
extended_gcode = prcrh.add_point_info(gcode_filtered)

print("Extended G-Code:\n")
for line in extended_gcode:
    print(line)


# Get filepath of generated Rhino file
filepath = crtrh.initialize_rhino_file(
    OUTPUT_DIRECTORY_RHINO, OUTPUT_FILE_RHINO, LAYER_MAX
)

# Generate toolpath in Rhino
drgrh.create_geometry(extended_gcode, filepath, TYPE_VALUES, LINE_WIDTHS)
# Generate printbed in Rhino
drprh.add_print_bed(
    filepath, X_MAX=BED_SIZE_X, Y_MAX=BED_SIZE_Y, parent_layer="printbed"
)
