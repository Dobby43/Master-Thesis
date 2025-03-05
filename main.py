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
from setup.check import check_input as chksu
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


# PLOT
from gcode import plot_gcode as plt

# KRL


# ROBOT
from robot.pre_process.mathematical_operators import Transformation
from robot.pre_process.mathematical_operators import Rotation
from robot.process import kinematics as rokin

# PUMP
from pump import filter_gcode as filtr

# RHINO

# ----------------GET SETUP PATH----------------
setup_path = str(Path(__file__).parent / "setup" / "setup.json")

# ----------------CONFIGURE DIRECTORY & FOLDERS----------------
# evaluate setup.json file for "Directory" information
directory_setup = disu.get_directory_setup(setup_path)

# Check input for valid type
input_check = chksu.validate_json_types(setup_path)


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

# Line_type translation to int value
ROBOT_TYPE_NUMBER = robot_settings["type_number"]


# ----------------PUMP CONFIGURATION----------------
pump_settings = pusu.get_pump_settings(setup_path)

PUMP_RETRACT = pump_settings["retract"]
PUMP_CHARACTERISTIC_CURVE = pump_settings["characteristic_curve"]
PUMP_FILAMENT_DIAMETER = pump_settings["filament_diameter"]
PUMP_LINETYPE_FLOW = pump_settings["linetype_flow"]


# ----------------SLICER CONFIGURATION----------------
# evaluate setup.json file for "Slicer" information
slicer_settings = slsu.get_slicer_settings(setup_path)

SLICER = slicer_settings["slicer_name"]
SLICER_CMD_PATH = slicer_settings["slicer_cmd_path"]
SLICER_CONFIG_FILE_PATH = slicer_settings["slicer_config_file_path"]
SLICER_ARGUMENTS = slicer_settings["slicer_arguments"]
SLICER_SCALING = slicer_settings["slicer_scaling"]


# ----------------RHINO CONFIGURATION----------------
# evaluate setup.json file for "Rhino" information
rhino_settings = rhsu.get_rhino_settings(setup_path)

RHINO_POINT_PRINT = rhino_settings["point_print"]
RHINO_POINT_TYPES = rhino_settings["point_types"]
RHINO_LINE_TYPES = rhino_settings["line_types"]
RHINO_LINE_WIDTHS = rhino_settings["line_widths"]


# ----------------SLICING OF .STL FILE----------------
if SLICER == "cura":
    CURA_SCALING = smacu.compute_scaling_and_rotation_matrix(SLICER_SCALING)
    # arguments from setup.json that also need to be handled by Cura
    preset_arguments_cura = {
        "machine_name": f"{ROBOT_ID} BEDSIZE: {BED_SIZE_X}x{BED_SIZE_Y}x{BED_SIZE_Z} [mm]",
        "machine_width": BED_SIZE_X,
        "machine_depth": BED_SIZE_Y,
        "machine_height": BED_SIZE_Z,
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
    print("[INFO] Starting to slice")
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
    print(f"[INFO] Finished slicing {INPUT_FILE_STL}")

elif SLICER == r"open slicer":
    print("[WARNING] Slicer not yet implemented")
elif SLICER == "orca":
    print("[WARNING] Slicer not yet implemented")
else:
    print("[WARNING] Choose valid Slicer")


# ----------------G-CODE IMPORT AND EVALUATION----------------
# Read the G-Code lines
gcode_lines = getgc.get_gcode_lines(INPUT_DIRECTORY_GCODE, INPUT_FILE_GCODE)

# Simplify_gcode
# Gets min X, Y and Z values
min_values = mima.get_min_values(gcode_lines)
x_min = min_values["x_min"]
y_min = min_values["y_min"]
z_min = min_values["z_min"]
# Gets max X, Y and Z values
max_values = mima.get_max_values(gcode_lines)
x_max = max_values["x_max"]
y_max = max_values["y_max"]
z_max = max_values["z_max"]

# Gets necessary G-Code lines
gcode_necessary = smplf.simplify_gcode(
    gcode_lines, SLICER, RHINO_LINE_TYPES, x_min, y_min, z_min
)
# Gets maximum layer number
layer_max = gcode_necessary[-1]["Layer"]

# for line in gcode_necessary:
#     print(line)


# ----------------PUMP IMPLEMENTATION
if PUMP_RETRACT is False:
    gcode_filtered = filtr.filter_retracts(gcode_necessary)
else:
    gcode_filtered = gcode_necessary

# ----------------PYVISTA PLOT----------------
plotter = plt.plot_bed(
    bed_size_x=BED_SIZE_X,
    bed_size_y=BED_SIZE_Y,
    bed_size_z=BED_SIZE_Z,
)

# Füge den G-Code-Pfad dem vorhandenen Plotter hinzu
plt.plot_gcode(plotter, gcode_filtered, "all", RHINO_LINE_TYPES)


# ----------------INITIALIZING ROBOT----------------
# Pre calculate fixed Rotation and Translation-matrices
# ORIENTATION BASE TO ROBOTROOT
# Due to the order of rotation ZYX the offset from $BASE to $ROBOTROOT given
# relative to $BASE yields the Transformation Matrix T(BASE,ROBOTROOT)
r_base_robotroot = Rotation.from_euler_angles(
    ROBOT_BASE["C"], ROBOT_BASE["B"], ROBOT_BASE["A"]
)
t_base_robotroot = Transformation.from_rotation_and_translation(
    r_base_robotroot,
    [ROBOT_BASE["X"], ROBOT_BASE["Y"], ROBOT_BASE["Z"]],
)


# ORIENTATION TOOL TO ROBOTROOT
# Due to orthogonal matrix M^-1 = M.T
r_robotroot_base = r_base_robotroot.T
r_base_tool = Rotation.from_euler_angles(
    aX=ROBOT_TOOL_ORIENTATION["C"],
    aY=ROBOT_TOOL_ORIENTATION["B"],
    aZ=ROBOT_TOOL_ORIENTATION["A"],
)
r_robotroot_tool = r_robotroot_base @ r_base_tool

# INITIALIZE ROBOT CLASS
robot = rokin.RobotOPW(
    robot_id=ROBOT_ID,
    robot_geometry=ROBOT_GEOMETRY,
    robot_rotation_sign=ROBOT_ROTATION_SIGN,
    robot_rotation_limit=ROBOT_ROTATION_LIMIT,
    robot_rotation_offset=ROBOT_ROTATION_OFFSET,
    robot_tool_offset=ROBOT_TOOL_OFFSET,
)

# Calculation of Start and End coordinates as well as check if within limits
start_pos_robotroot, start_pos_status = robot.forward_kinematics(ROBOT_START_POSITION)
end_pos_robotroot, end_pos_status = robot.forward_kinematics(ROBOT_END_POSITION)

if not start_pos_status:
    print(f"[ERROR] Start position of robot {ROBOT_START_POSITION} is not reachable")
elif not end_pos_status:
    print(f"[ERROR] End position of robot {ROBOT_END_POSITION} is not reachable")

start_pos_base = t_base_robotroot @ start_pos_robotroot
end_pos_base = t_base_robotroot @ end_pos_robotroot

robot_start_point = {
    "Move": "G0",
    "X": round(float(start_pos_base[0, 3]), 2),
    "Y": round(float(start_pos_base[1, 3]), 2),
    "Z": round(float(start_pos_base[2, 3]), 2),
    "E_Rel": 0,
    "Layer": 0,
    "Type": "travel",
    "Layer_Height": 0,
    "Reachable": start_pos_status,
}
robot_end_point = {
    "Move": "G0",
    "X": round(float(end_pos_base[0, 3]), 2),
    "Y": round(float(end_pos_base[1, 3]), 2),
    "Z": round(float(end_pos_base[2, 3]), 2),
    "E_Rel": 0,
    "Layer": layer_max,
    "Type": "travel",
    "Layer_Height": 0,
    "Reachable": end_pos_status,
}

# ----------------ROBOT SIMULATION----------------
status = []
for index, line in enumerate(gcode_filtered):
    # Transform point in BASE to point in ROBOTROOT
    point_base = [
        line["X"],
        line["Y"],
        line["Z"],
        1,
    ]
    point_robotroot = Transformation.invert(t_base_robotroot) @ point_base
    # Set up homogeneous transformation Matrix
    point_hom = np.eye(4)
    point_hom[:3, :3] = r_robotroot_tool
    point_hom[:3, 3] = point_robotroot[:3]

    ik_point = robot.inverse_kinematics(point_hom)

    if not ik_point:
        print(
            f"[ERROR] Point {line['X']}, {line['Y']}, {line['Z']} on printbed is not reachable"
        )
        line.update({"Reachable": False})
    else:
        line.update({"Reachable": True})

# insert start and end point into the list
gcode_filtered.insert(0, robot_start_point)
gcode_filtered.append(robot_end_point)

for line in gcode_filtered:
    print(line)

# ----------------KRL FORMATING OF G-CODE----------------
# # Set Start and End Code parts from Python values
# KRL_NAME = flnkr.set_filename_krl(OUTPUT_NAME)
# ROBOT_START_CODE_PY = scpkr.set_start_code_python(layer_max)
# ROBOT_END_CODE_PY = []
#
# # Formats G-Code to KRL and appends tool-head orientation
# krl_lines = mdfkr.krl_format(
#     gcode_filtered[1:-1],
#     type_mapping=ROBOT_TYPE_NUMBER,
#     a=ROBOT_TOOL_ORIENTATION["A"],
#     b=ROBOT_TOOL_ORIENTATION["B"],
#     c=ROBOT_TOOL_ORIENTATION["C"],
#     vel=ROBOT_VEL_CP,
#     x_max=BED_SIZE_X,
#     y_max=BED_SIZE_Y,
#     z_max=BED_SIZE_Z,
# )
#
# for line in krl_lines:
#     print(line)
#
# # Export of KRL-File
# expkr.export_to_src(
#     krl_lines,
#     KRL_NAME,
#     ROBOT_START_CODE_JSON,
#     ROBOT_START_CODE_PY,
#     ROBOT_END_CODE_JSON,
#     ROBOT_END_CODE_PY,
#     OUTPUT_DIRECTORY,
#     OUTPUT_NAME,
# )


# ----------------RHINO FILE----------------
# # Process G-Code for Rhino file
# extended_gcode = prcrh.add_point_info(gcode_filtered)
#
# print("Extended G-Code:\n")
# for line in extended_gcode:
#     print(line)
#
# # Get filepath of generated Rhino file
# filepath = crtrh.initialize_rhino_file(
#     OUTPUT_DIRECTORY_RHINO, OUTPUT_FILE_RHINO, layer_max
# )
#
# # Generate toolpath in Rhino
# drgrh.create_geometry(
#     extended_gcode,
#     filepath,
#     RHINO_LINE_TYPES,
#     RHINO_LINE_WIDTHS,
#     RHINO_POINT_TYPES,
#     RHINO_POINT_PRINT,
# )
# # Generate printbed in Rhino
# drprh.add_print_bed(
#     filepath, x_max=BED_SIZE_X, y_max=BED_SIZE_Y, parent_layer="printbed"
# )


# if input_check:
#     print("\n[INFO] Input as expected. \n[INFO] Ready to slice")
# else:
#     print(
#         "\n[ERROR] Invalid input in setup.json. \n[INFO] Programm stopped; Please adjust input and retry"
#     )
