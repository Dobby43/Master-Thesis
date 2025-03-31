"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.7"

from pathlib import Path
import numpy as np
from datetime import datetime
import time
import os
import sys


# SETUP
from setup import load_settings as sulod
from setup import validate_value as suval
from setup import replace_strings as surpl


# SLICER
# CURA
from slicer.cura import slicing as cusli
from slicer.cura import extract_settings as cuext
from slicer.cura import preset_arguments as cupre
from slicer.cura import scaling_matrix as cusca

# G-CODE
from gcode import get_gcode as gcget
from gcode import min_max_values as gcmim
from gcode import simplify_gcode as gcspf
from gcode import fits_printbed as gcfit

# KRL
from krl import export_to_src as krexp
from krl import start_code_python as krscp
from krl import modify_to_krl as krmdf

# ROBOT
from robot.mathematical_operators import Transformation
from robot.mathematical_operators import Rotation
from robot import kinematics as rokin

# PUMP
from pump import calculate_linewidth as puliw
from pump import calculate_flow as puflo
from pump import calculate_rpm as purpm

# RHINO
from rhino.pre_process import create_rhino as crtrh
from rhino.pre_process import evaluate_sublayers as rhevl
from rhino.process import extend_gcode as rhext
from rhino.process import draw_printbed as rhdrp
from rhino.process import draw_gcode as rhdrg
from rhino.process import import_robot as rhdrr

# REPORT
from report import plot_gcode as repgc
from report import plot_char_curve as repcc
from report import write_report as rewrt


# All upper case variables are taken from the setup.json file and are upper case to be clearly identified
def main():
    print(f"[INFO] Program initialized")
    start_time = time.time()

    # ----------------GET SETUP PATH----------------
    setup_path = str(Path(__file__).parent / "setup" / "setup.json")

    # ----------------PRECISION----------------
    # Define the Precision of each value that gets displayed in Rhino and .src
    # Calculation is not affected
    precision = 3

    # ----------------LOAD + VALIDATE SETTINGS----------------
    # loads the settings from setup.settings.json and validates them according to each specified type
    # Program gets aborted if any error in the setup.json file occurs
    try:
        settings = sulod.load_settings(json_path=setup_path)
        suval.validate_settings(user_settings=settings)
        print("[INFO] Loaded and validated setup.json successfully.\n")
    except ValueError as e:
        print("\n[ERROR] Invalid input in setup.json:")
        print(e)
        exit(1)

    # ----------------EXTRACT DIRECTORY INFORMATION----------------
    # Access "Directory" section in settings imported from setup.json
    directory_settings = settings["Directory"]

    INPUT_DIRECTORY_STL = directory_settings["input_directory"]["value"]
    INPUT_FILE_STL = f"{directory_settings["input_name"]["value"]}.stl"

    # Program gets aborted if input directory or input file doesn't exist
    if not os.path.isdir(INPUT_DIRECTORY_STL):
        print(f"[ERROR] Input Directory {INPUT_DIRECTORY_STL} does not exist")
        sys.exit(1)

    if not os.path.isfile(os.path.join(INPUT_DIRECTORY_STL, INPUT_FILE_STL)):
        print(
            f"[ERROR] Input .stl file {INPUT_FILE_STL} inside input directory does not exist"
        )
        sys.exit(1)

    OUTPUT_NAME = directory_settings["output_name"]["value"]
    OUTPUT_DIRECTORY = directory_settings["output_directory"]["value"]
    folder_name = f"{OUTPUT_NAME}_{datetime.now().strftime('%H_%M_%S')}"

    # Generate output directory
    output_folder = os.path.join(OUTPUT_DIRECTORY, folder_name)
    os.makedirs(output_folder, exist_ok=True)

    # Specify output file names
    # G-Code
    OUTPUT_DIRECTORY_GCODE = output_folder
    OUTPUT_FILE_GCODE = f"{OUTPUT_NAME}.gcode"

    # Rhino
    OUTPUT_DIRECTORY_RHINO = output_folder
    OUTPUT_FILE_RHINO = f"{OUTPUT_NAME}.3dm"

    # ----------------EXTRACT ROBOT SETTINGS----------------
    # Access "Robot" section in settings imported from setup.json
    robot_settings = settings["Robot"]

    ROBOT_ID = robot_settings["id"]["value"]
    ROBOT_GEOMETRY = robot_settings["geometry"]["value"]
    ROBOT_BASE_RADIUS = robot_settings["base_radius"]["value"]
    ROBOT_SPLIT_SRC = robot_settings["split_src"]["value"]

    ROBOT_BASE = robot_settings["base_coordinates"]["value"]
    ROBOT_TOOL_OFFSET = robot_settings["tool_offset"]["value"]
    ROBOT_TOOL_ORIENTATION = robot_settings["tool_orientation"]["value"]

    ROBOT_START_POSITION = robot_settings["start_position"]["value"]
    ROBOT_END_POSITION = robot_settings["end_position"]["value"]
    ROBOT_ROTATION_LIMIT = robot_settings["rotation_limit"]["value"]
    ROBOT_ROTATION_SIGN = robot_settings["rotation_sign"]["value"]
    ROBOT_ROTATION_OFFSET = robot_settings["rotation_offset"]["value"]

    BED_SIZE = robot_settings["bed_size"]["value"]
    ROBOT_VEL_CP = robot_settings["print_speed"]["value"]
    ROBOT_VEL_TVL = robot_settings["travel_speed"]["value"]
    ROBOT_TYPE_NUMBER = robot_settings["type_number"]["value"]
    ROBOT_3DM_FILE = robot_settings["3dm_file"]["value"]
    ROBOT_MIN_LAYER_TIME = robot_settings["min_layer_time"]["value"]

    # Replacing placeholders in robot.start_code and robot.end_code
    ROBOT_START_CODE_JSON = [
        surpl.replace_placeholders(text=line, settings=settings, precision=precision)
        for line in robot_settings["start_code"]["value"]
    ]
    ROBOT_END_CODE_JSON = [
        surpl.replace_placeholders(text=line, settings=settings, precision=precision)
        for line in robot_settings["end_code"]["value"]
    ]

    # ----------------PUMP CONFIGURATION----------------
    # Access "Pump" section in settings imported from setup.json
    pump_settings = settings["Pump"]

    PUMP_RETRACT = pump_settings["retract"]["value"]
    PUMP_CHARACTERISTIC_CURVE = pump_settings["characteristic_curve"]["value"]
    PUMP_CONTROL = pump_settings["pump_control"]["value"]
    PUMP_FILAMENT_DIAMETER = pump_settings["filament_diameter"]["value"]
    PUMP_LINETYPE_FLOW = pump_settings["linetype_flow"]["value"]

    # Ensure first values are 0
    PUMP_CHARACTERISTIC_CURVE.insert(0, [0, 0, 0])

    print(f"[INFO] Pump Setting Retraction enabled: {PUMP_RETRACT}")

    # ----------------CURA CONFIGURATION----------------
    # Access "Cura" section in settings imported from setup.json
    cura_settings = settings["Cura"]

    CURA_CMD_PATH = cura_settings["cura_cmd_path"]["value"]
    CURA_PRINTER_CONFIG_FILE_PATH = cura_settings["cura_printer_config_file_path"][
        "value"
    ]

    # Program gets aborted if CuraEngine filepath or printer_config input file doesn't exist
    if not os.path.isfile(CURA_CMD_PATH):
        print(f"[ERROR] CuraEngine-Path {CURA_CMD_PATH} not found")
        sys.exit(1)

    if not os.path.isfile(CURA_PRINTER_CONFIG_FILE_PATH):
        print(
            f"[ERROR] Configuration file {CURA_PRINTER_CONFIG_FILE_PATH} for printer not found"
        )
        sys.exit(1)

    CURA_ARGUMENTS = cura_settings["cura_arguments"]["value"]
    CURA_SCALING = cura_settings["cura_scaling"]["value"]
    CURA_LINE_TYPES_DICT = cura_settings["cura_line_types_dict"]["value"]

    # ----------------SLICER CONFIGURATION----------------
    # Access "Slicer" section in settings imported from setup.json
    slicer_settings = settings["Slicer"]
    # Extract the choosen slicer
    SLICER = slicer_settings["slicer_name"]["value"].lower()

    # Slicer linetype_dict; fixed to cura
    slicer_line_type_dict = CURA_LINE_TYPES_DICT

    # ----------------RHINO CONFIGURATION----------------
    # Access "Rhino" section in settings imported from setup.json
    rhino_settings = settings["Rhino"]

    RHINO_POINT_PRINT = rhino_settings["point_print"]["value"]
    RHINO_POINT_COLORS = rhino_settings["point_color"]["value"]
    RHINO_LINE_STYLE_LINE = rhino_settings["line_style_line"]["value"]
    RHINO_LINE_TYPES_COLOR = rhino_settings["line_types_color"]["value"]
    RHINO_LINE_WIDTH = rhino_settings["line_width"]["value"]

    # ----------------SLICING OF .STL FILE----------------
    print(f"[INFO] Trying to slice {INPUT_FILE_STL} with given Slicer {SLICER.upper()}")
    if SLICER == "cura":
        # Calculate scaling Matrix
        scale = cusca.compute_scaling_and_rotation_matrix(scaling_input=CURA_SCALING)
        # Setup fixed arguments
        cura_fixed_arguments = cupre.def_preset_arguments(
            machine_name=ROBOT_ID,
            bed_size=BED_SIZE,
            flow=PUMP_LINETYPE_FLOW,
            pump_retract=PUMP_RETRACT,
            scaling=scale,
            filament_dia=PUMP_FILAMENT_DIAMETER,
        )

        # Load default data set
        default_data_path = Path(__file__).parent / "slicer" / "cura" / "default"
        default_data_printer = cuext.load_json(
            filepath=str(default_data_path / "TUM_C3DP_fdmprinter.def.json")
        )
        default_data_extruder = cuext.load_json(
            filepath=str(default_data_path / "TUM_C3DP_fdmextruder.def.json")
        )
        # Extract all default printer settings for possible type check and possible default value replacement
        printer_default_values = cuext.extract_settings(
            data=default_data_printer.get("settings", {})
        )
        extruder_default_values = cuext.extract_settings(
            data=default_data_extruder.get("settings", {})
        )

        # Validate user arguments from setup_old.json with default values
        print("[INFO] Validating and updating user arguments...")
        validated_user_arguments = cuext.validate_user_arguments(
            user_arguments=CURA_ARGUMENTS,
            printer_default=printer_default_values,
            extruder_default=extruder_default_values,
        )

        # Update and extend user arguments with fixed arguments
        final_slicer_arguments = cuext.final_arguments(
            validated_arguments=validated_user_arguments,
            preset_arguments=cura_fixed_arguments,
        )

        # Slice STL with updated user arguments
        print(f"[INFO] Starting to slice {INPUT_FILE_STL}")
        success, message = cusli.slicer(
            directory_stl=INPUT_DIRECTORY_STL,
            file_name_stl=INPUT_FILE_STL,
            export_directory_gcode=output_folder,
            export_file_gcode=OUTPUT_NAME,
            cura_engine_path=CURA_CMD_PATH,
            cura_def_file=CURA_PRINTER_CONFIG_FILE_PATH,
            additional_args=final_slicer_arguments,
        )
        print(message)
        print(f"[INFO] Finished slicing {INPUT_FILE_STL}")

    elif SLICER == r"open slicer":
        print(f"[ERROR] Slicer {SLICER.upper()} not yet implemented")
        sys.exit(1)
    elif SLICER == "orca":
        print(f"[ERROR] Slicer {SLICER.upper()} not yet implemented")
        sys.exit(1)
    else:
        print(f"[ERROR] {SLICER.upper()} not supported; Choose valid Slicer")
        sys.exit(1)

    # ----------------SAFETY SWITCH----------------
    # Define switch to ensure all points in a .src file are reachable
    # If scr == False no .src file is generated
    src = True

    # ----------------G-CODE IMPORT AND EVALUATION----------------
    # Read the G-Code lines
    gcode_lines = gcget.get_gcode_lines(
        directory=OUTPUT_DIRECTORY_GCODE, file_name=OUTPUT_FILE_GCODE
    )

    # Gets min X, Y and Z values
    min_values = gcmim.get_min_values(gcode=gcode_lines)
    # Gets max X, Y and Z values
    max_values = gcmim.get_max_values(gcode=gcode_lines)

    # Check if object fits on printbed
    location = True
    size_check, needs_offset, offset = gcfit.check_fit_and_shift(
        bed_size=BED_SIZE, min_values=min_values, max_values=max_values
    )
    if not size_check:
        src = False
        location = False
        print(f"[ERROR] Object doesn't fit printbed in given orientation")
    elif not needs_offset:
        src = False
        location = False
        print(
            f"[ERROR] Object not located fully on the printbed; shift at least {offset}"
        )

    # Gets necessary G-Code lines
    gcode_necessary = gcspf.simplify_gcode(
        gcode=gcode_lines,
        slicer=SLICER,
        type_dict=slicer_line_type_dict,
        x_min=min_values["x"],
        y_min=min_values["y"],
        z_min=min_values["z"],
    )

    # Gets maximum layer number
    layer_max = gcode_necessary[-1]["Layer"]

    # ----------------INITIALIZING ROBOT----------------
    # Setting switch to identify invalid locations
    reachable = True

    # Precalculate fixed Rotation and Translation-matrices
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
        ax=ROBOT_TOOL_ORIENTATION["C"],
        ay=ROBOT_TOOL_ORIENTATION["B"],
        az=ROBOT_TOOL_ORIENTATION["A"],
    )
    r_robotroot_tool = r_robotroot_base @ r_base_tool

    # INITIALIZE ROBOT CLASS
    print(f"[INFO] Initialising class for {ROBOT_ID}")
    robot = rokin.RobotOPW(
        robot_id=ROBOT_ID,
        robot_geometry=ROBOT_GEOMETRY,
        robot_base_radius=ROBOT_BASE_RADIUS,
        robot_rotation_sign=ROBOT_ROTATION_SIGN,
        robot_rotation_limit=ROBOT_ROTATION_LIMIT,
        robot_rotation_offset=ROBOT_ROTATION_OFFSET,
        robot_tool_offset=ROBOT_TOOL_OFFSET,
    )

    # Calculation of Start and End coordinates as well as check if within limits

    # Start position
    print(
        f"[INFO] Checking start position {ROBOT_START_POSITION} of robot from setup.json"
    )
    start_pos_robotroot, start_pos_status = robot.forward_kinematics(
        joint_angles=ROBOT_START_POSITION
    )
    if not start_pos_status:
        src = False
        reachable = False
        start_pos_base = np.eye(4)
        start_pos_base[:, 3] = [0, 0, 0, 1]
        print(f"[WARNING] Start position {ROBOT_START_POSITION} is not valid")
        print("[INFO] No .src file will be created")
        print(
            f"[INFO] Rhino file created with alternative end point [{start_pos_base[0,3]}, {start_pos_base[1,3]}, {start_pos_base[2,3]}]"
        )

    else:
        start_pos_base = t_base_robotroot @ start_pos_robotroot

    # End position
    print(f"[INFO] Checking end position of robot from setup.json")
    end_pos_robotroot, end_pos_status = robot.forward_kinematics(
        joint_angles=ROBOT_END_POSITION
    )
    if not end_pos_status:
        src = False
        reachable = False
        end_pos_base = np.eye(4)
        end_pos_base[:, 3] = [0, 0, 0, 1]
        print(f"[WARNING] End position {ROBOT_END_POSITION} is not valid")
        print("[INFO] No .src file will be created")
        print(
            f"[INFO] Rhino file created with alternative end point [{end_pos_base[0,3]}, {end_pos_base[1,3]}, {end_pos_base[2,3]}] "
        )
    else:
        print(f"[INFO] End position {ROBOT_END_POSITION} is valid")
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
    print(f"[INFO] Checking robot kinematics for each Point of given G-Code")
    status = []
    for index, line in enumerate(gcode_necessary):
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

        ik_point = robot.inverse_kinematics(hom_trans=point_hom)

        if not ik_point:
            src = False
            reachable = False
            line.update({"Reachable": False})
            print(
                f"[ERROR] Point ({line["X"]}, {line['Y']}, {line['Z']}) on printbed is not reachable"
            )
        else:
            line.update({"Reachable": True})

    if all(entry.get("Reachable") is True for entry in gcode_necessary):
        print("[INFO] All points from G-Code are reachable")

    # Insert start and end point into the list
    gcode_necessary.insert(0, robot_start_point)
    gcode_necessary.append(robot_end_point)

    # ----------------PUMP IMPLEMENTATION----------------

    # Calculate linewidth of each line
    linewidths, volume = puliw.get_linewidth(
        points=gcode_necessary, flow=PUMP_LINETYPE_FLOW, diam_fil=PUMP_FILAMENT_DIAMETER
    )
    for gcd, lw in zip(gcode_necessary, linewidths):
        gcd["Linewidth"] = lw

    # Calculate the Flow in [mm^3/s]
    pump_flow = puflo.get_flow(points=gcode_necessary, vel_cp=ROBOT_VEL_CP)
    for gcd, flo in zip(gcode_necessary, pump_flow):
        gcd["Flow"] = flo

    # Calculate the value for the external axis (rpm or voltage)
    pump_command = purpm.get_rpm(
        points=gcode_necessary,
        characteristic_curve=PUMP_CHARACTERISTIC_CURVE,
        vel_cp=ROBOT_VEL_CP,
        vel_tvl=ROBOT_VEL_TVL,
        precision=precision,
    )
    for gcd, cmd in zip(gcode_necessary, pump_command):
        gcd.update(cmd)

    # ----------------KRL FORMATING OF G-CODE----------------
    if src is True:
        print("[INFO] compiling .src file")
        # Set Start and End Code parts from Python values
        length_name = 25 if ROBOT_SPLIT_SRC == False else 21
        filename_formatted = OUTPUT_NAME.replace(" ", "_")[:length_name]
        robot_start_code_py = krscp.set_start_code_python(layers=layer_max)
        robot_end_code_py = []

        krl_lines = krmdf.krl_format(
            gcode_necessary[
                1:-1
            ],  # Skip start and end position as they are part of start and end code in setup.json
            type_mapping=ROBOT_TYPE_NUMBER,
            a=ROBOT_TOOL_ORIENTATION["A"],
            b=ROBOT_TOOL_ORIENTATION["B"],
            c=ROBOT_TOOL_ORIENTATION["C"],
            vel_tvl=ROBOT_VEL_TVL,
            pump_control=PUMP_CONTROL,
            precision=precision,
            axis_min=min_values,
            axis_max=max_values,
            timer=4,
            mlt=ROBOT_MIN_LAYER_TIME,
            split_layers=ROBOT_SPLIT_SRC,
            project_name=filename_formatted,
        )
        if not ROBOT_SPLIT_SRC:
            # Export one single src-File
            krexp.export_to_src(
                krl_lines=krl_lines,
                file_name_krl=filename_formatted,
                start_code_json=ROBOT_START_CODE_JSON,
                start_code_python=robot_start_code_py,
                end_code_json=ROBOT_END_CODE_JSON,
                end_code_python=robot_end_code_py,
                output_path=output_folder,
                file_name=OUTPUT_NAME,
            )
        else:
            # Export multiple .src files with one main file and file_name_XXX as the files for each layer
            krexp.split_and_export_to_src(
                krl_lines=krl_lines,
                file_name_krl=filename_formatted,
                start_code_json=ROBOT_START_CODE_JSON,
                start_code_python=robot_start_code_py,
                end_code_json=ROBOT_END_CODE_JSON,
                end_code_python=robot_end_code_py,
                output_path=output_folder,
                file_name=OUTPUT_NAME,
            )
    else:
        if not reachable:
            print("[ERROR] .src file not generated due unreachable point")
        if not location:
            print(
                "[ERROR] .src file not generated due to invalid location or of object or object not fitting on printbed"
            )

    # ---------------- REPORT ----------------
    # Plot of the G-Code and Printbed
    # Plot of Printbed
    plotter = repgc.plot_bed(
        bed_size_x=BED_SIZE["X"],
        bed_size_y=BED_SIZE["Y"],
        bed_size_z=BED_SIZE["Z"],
    )

    # Adds G-Code to the printbed
    repgc.plot_gcode(
        plotter=plotter,
        points=gcode_necessary[1:-1],
        layers="all",
        line_types_color=RHINO_LINE_TYPES_COLOR,
    )

    # Plot of the characteristic curve for the pump
    repcc.plot_pump_curve(characteristic_curve=PUMP_CHARACTERISTIC_CURVE)

    # Build dictionary to replace placeholders in template
    pump_retract = "activated" if PUMP_RETRACT else "deactivated"
    pump_control = "RPM" if PUMP_CONTROL else "Voltage"
    measurement_x = max_values["x"] - min_values["x"]
    measurement_y = max_values["y"] - min_values["y"]
    measurement_z = max_values["z"]

    text_data = {
        "filename": INPUT_FILE_STL,
        "weight": round(volume * 1e-7 * 21, precision),
        "volume": round(volume * 1e-6, precision),
        "measurements": [
            round(measurement_x, precision),
            round(measurement_y, precision),
            round(measurement_z, precision),
        ],
        "x_min": round(min_values["x"], precision),
        "y_min": round(min_values["y"], precision),
        "z_min": round(0, precision),
        "x_max": round(max_values["x"], precision),
        "y_max": round(max_values["y"], precision),
        "z_max": round(max_values["z"], precision),
        "robot_name": ROBOT_ID,
        "robot_geometry": ROBOT_GEOMETRY,
        "tool_offset": ROBOT_TOOL_OFFSET,
        "tool_orientation": ROBOT_TOOL_ORIENTATION,
        "printbed": BED_SIZE,
        "base_coordinates": ROBOT_BASE,
        "print_speed": round(ROBOT_VEL_CP, precision),
        "travel_speed": round(ROBOT_VEL_TVL, precision),
        "protract": ROBOT_TYPE_NUMBER["protract"],
        "retract": ROBOT_TYPE_NUMBER["retract"],
        "travel": ROBOT_TYPE_NUMBER["travel"],
        "outside": ROBOT_TYPE_NUMBER["wall_outer"],
        "inside": ROBOT_TYPE_NUMBER["wall_inner"],
        "surface": ROBOT_TYPE_NUMBER["surface"],
        "infill": ROBOT_TYPE_NUMBER["infill"],
        "bridge": ROBOT_TYPE_NUMBER["bridge"],
        "curb": ROBOT_TYPE_NUMBER["curb"],
        "support": ROBOT_TYPE_NUMBER["support"],
        "unknown": ROBOT_TYPE_NUMBER["unknown"],
        "pump_retract": pump_retract,
        "pump_control": pump_control,
        "flow_outer": round(PUMP_LINETYPE_FLOW["wall_outer"], precision),
        "flow_inner": round(PUMP_LINETYPE_FLOW["wall_inner"], precision),
        "flow_surface": round(PUMP_LINETYPE_FLOW["surface"], precision),
        "flow_unknown": round(PUMP_LINETYPE_FLOW["unknown"], precision),
        "flow_infill": round(PUMP_LINETYPE_FLOW["infill"], precision),
        "flow_bridge": round(PUMP_LINETYPE_FLOW["bridge"], precision),
        "flow_curb": round(PUMP_LINETYPE_FLOW["curb"], precision),
    }

    # Initiate a new .docx file based on the given template
    report_path = os.path.join(OUTPUT_DIRECTORY_RHINO, f"Report_{OUTPUT_NAME}.docx")

    # Write the given values into the .docx file for the keys {key}
    rewrt.build_report(output_path=report_path, text_data=text_data)

    # specify filenames to delete
    files_to_delete = ["gcode_plot.png", "characteristic_curve_plot.png"]

    # Delete plot files in directory
    for filename in files_to_delete:
        file_path = f"{str(Path(__file__).parent)}/{filename}"
        if os.path.exists(file_path):
            os.remove(file_path)

    # ----------------RHINO FILE----------------
    # Process G-Code for Rhino file
    extended_gcode = rhext.add_point_info(points=gcode_necessary)

    # Evaluate sub_sub Layers for the Layer "toolpath" inside the rhino file
    sublayers = rhevl.evaluate_sublayers_printbed(points_list=extended_gcode)

    # Get filepath of generated Rhino file
    filepath = crtrh.initialize_rhino_file(
        directory=OUTPUT_DIRECTORY_RHINO,
        filename=OUTPUT_FILE_RHINO,
        max_layers=layer_max,
        sublayers=sublayers,
    )

    # Import Robot.3dm file into Rhino
    robot_file = Path(ROBOT_3DM_FILE)
    if robot_file.exists() and robot_file.suffix.lower() == ".3dm":
        # Position of Robotroot relative to printbed origin
        robotroot_pos = [ROBOT_BASE["X"], ROBOT_BASE["Y"], ROBOT_BASE["Z"]]

        rhdrr.import_step_file_to_rhino_file(
            file_path=ROBOT_3DM_FILE,
            target_point=robotroot_pos,
            target_3dm_path=filepath,
            target_layer_name="robot",
        )
    else:
        print(
            f"[WARNING] .3dm file for Robot does not exist under given filepath {ROBOT_3DM_FILE} or has the wrong format"
        )
        print("[INFO] Skipping robot.3dm_file import from setup.json to Rhino file")

    # Generate printbed in Rhino
    printbed = rhdrp.add_print_bed(
        file_path=filepath,
        x_max=BED_SIZE["X"],
        y_max=BED_SIZE["Y"],
        parent_layer="printbed",
    )

    if printbed:
        print("[INFO] printbed successfully created in Rhino file")
    else:
        print("[ERROR] printbed creation failed")
        exit(1)

    # Generate toolpath in Rhino
    toolpath = rhdrg.create_geometry(
        points=extended_gcode,
        filepath=filepath,
        linetype_dict=RHINO_LINE_STYLE_LINE,
        line_color_dict=RHINO_LINE_TYPES_COLOR,
        line_widths=RHINO_LINE_WIDTH,
        point_color=RHINO_POINT_COLORS,
        point_print=RHINO_POINT_PRINT,
        precision=precision,
    )
    if toolpath:
        print("[INFO] toolpath successfully created in Rhino file")
    else:
        print("[ERROR] toolpath creation failed")
        exit(1)

    elapsed_seconds = time.time() - start_time
    minutes, seconds = divmod(int(elapsed_seconds), 60)
    print(f"[INFO] Runtime: {minutes:02d} min : {seconds:02d} sec")


if __name__ == "__main__":
    main()
