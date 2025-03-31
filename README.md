[comment]:<> (Header)
# Development of software solution for the use of slicers for polymer materials for additive manufacturing with concretes
**Institute:**  
[Chair of concrete structures](https://www.cee.ed.tum.de/mb/startseite/)  
TUM School of Engineering and Design  
Technical University Munich

**Author:** David Scheidt  
**Year:** 2025

[comment]:<> (Description)
# Description
This code is designed to connect Polymer Slicer such as [Cura](https://ultimaker.com/de/), [Orca](https://orca-slicer.com/) or [Simplify3D](https://www.simplify3d.com/) with state of the art 6 DOF [KUKA](https://www.kuka.com/de-de) robotics and visualisation using [Rhino](https://www.rhino3d.com/de/).
Therefor the Program automatically generates G-Code, evaluates the given code filtering for attributes (which get visualized in dedicated Rhino file), performes safety checks regarding Robot reachability and pump capability and finally outputs .src files, that can be interpreted by KUKA robots using KRL.  
In its current state it is limited to using [Cura](https://ultimaker.com/de/), but could be easily adapted for other Slicers as mentioned above.

[comment]:<> (Overview)
# Overview
```text
main.py
│   # Entry point for the full code workflow.
│   # Executes slicing, kinematics, pump control, Rhino export, and report generation.
│
├── setup/                  # Centralized configuration handling
│   ├── setup.json             # All user inputs and parameters in one JSON file
│   ├── load_settings.py       # Loads the JSON config file
│   ├── replace_strings.py     # Replaces placeholders in robot start/end code
│   ├── validate_value.py      # Validates config values based on expected types from slicer.cura.default
│   └── __init__.py
│
├── slicer/                    # Handles slicing logic (currently only using Cura); Can be extended for using other slicers
│   ├── __init__.py
│   └── cura/                  # CuraEngine-specific implementation
│       ├── slicing.py                          # Runs the actual slicing process (Command for Cura.exe)
│       ├── extract_settings.py                 # Validates and completes slicer arguments given in the specified .def file (using slicer.cura.default) 
│       ├── preset_arguments.py                 # Defines fixed slicing parameters 
│       ├── scaling_matrix.py                   # Computes scaling/rotation matrix for STL
│       ├── default/                            # Default Cura config files (checks of input type in .def are performed with these files)
│       │   ├── TUM_C3DP_fdmextruder.def.json
│       │   └── TUM_C3DP_fdmprinter.def.json
│       └── __init__.py
│
├── gcode/                 # G-code post-processing
│   ├── get_gcode.py          # Loads raw G-code lines from file
│   ├── simplify_gcode.py     # Reduces G-code to essential extrusion paths (Coordinates & Extrusion/Extrusion Mode)
│   ├── fits_printbed.py      # Checks whether the part fits the print bed
│   ├── min_max_values.py     # Extracts min/max coordinates of G-code
│   └── __init__.py
│
├── krl/                   # KUKA Robot Language (.src) file generation
│   ├── modify_to_krl.py      # Converts G-Code-like data into KRL syntax
│   ├── export_to_src.py      # Exports KRL to .src files (single or split)
│   ├── start_code_python.py  # Builds dynamic KRL header/footer (With input from python)
│   └── __init__.py
│
├── robot/                     # Robot kinematics and transformation logic
│   ├── kinematics.py             # OPW-based forward/inverse kinematics model
│   ├── mathematical_operators.py # Rotation and transformation matrix tools
│   └── __init__.py
│
├── pump/                   # Controls flow and extrusion speed
│   ├── calculate_flow.py      # Calculates volumetric flow [mm³/s]
│   ├── calculate_rpm.py       # Maps flow to RPM or voltage using pump curve (also limits Printspeed if necessary)
│   ├── calculate_linewidth.py # Calculates width of deposited lines 
│   └── __init__.py
│
├── rhino/                 # Rhino 3D model generation (.3dm)
│   ├── __init__.py
│   ├── pre_process/          # Prepares and manages Rhino file and layers
│   │   ├── create_rhino.py           # Initializes empty Rhino file
│   │   ├── evaluate_sublayers.py     # Organizes G-Code toolpath into layer hierarchy
│   │   ├── rhino_layermanager.py     # Manages layer structure (parent layers)
│   │   ├── rhino_linemanager.py      # Handles line styling and types (dashed, solid etc.)
│   │   └── __init__.py
│   └── process/              # Draws printbed, toolpath, and robot into Rhino
│       ├── draw_gcode.py             # Draws machine path and adds User strings to Rhino objects
│       ├── draw_printbed.py          # Draws 3D object of printbed into the file
│       ├── extend_gcode.py           # Adds additional metadata to points
│       ├── import_robot.py           # Imports robot geometry from .3dm file
│       └── __init__.py
│
├── report/                # Automated report generation (.docx)
│   ├── plot_gcode.py         # 3D visualization of sliced G-code
│   ├── plot_char_curve.py    # 2D Plot of pump characteristic curve
│   ├── write_report.py       # Inserts metadata into Word report template
│   ├── report_template.docx  # Report template with placeholders
│   └── __init__.py
│
├── tests/                         # Unit tests for robot and kinematic logic
│   ├── test_kinematics/
│   │   ├── kinematics_test_cases/    # Custom test cases generated using RoboDk for KUKA KR340 R3300 
│   │   │   └── __init__.py
│   │   ├── test_kinematics.py        # Tests forward/inverse kinematics
│   │   ├── setup_kinematics_test.py  # Loads test-specific config
│   │   └── __init__.py
│   ├── test_robot_math_operator.py   # Tests transformation logic from robot.mathmatical_operators
│   └── __init__.py
│
├── requirements.txt         # Project dependencies
└── README.md                # Project description (this file)
```
## External Tools and Software Requirements

This project depends on the following third-party tools:

| Tool             | Purpose                                | Required Version / Notes                   |
|------------------|----------------------------------------|--------------------------------------------|
| **CuraEngine**   | Slicing STL files into G-Code          | Recommended: ≥ 5.8                         |
| **Rhino 3D**     | Visualization and .3dm file generation | Version 8 or later                         |
| **Microsoft Word** | For reading `.docx` reports            | Optional, for viewing of print report only |

> ⚠️ Make sure that CuraEngine.exe is properly installed and the paths is configured correctly in `setup.json`.
### CuraEngine.exe
To install the CuraEngine.exe download [Cura 5.8](https://ultimaker.com/de/software/ultimaker-cura/) or higher.
Within the installed folder you will find a _.exe_ file named _CuraEngine.exe_  
Copy the link to this file (e.g.: _C:\Program Files\UltiMaker Cura 5.8.1\CuraEngine.exe_) into the _setup.json_ file under Cura.cura_cmd_path as a value. 
You find the setup.json file under _\setup\setup.json_ in my repository.
Your slicing engine is now set up for remote slicing.

### Rhinoceros 3D
To execute the code and visualize the sliced G-Code as well as the printbed and Robot [Rhinoceros 8](https://www.rhino3d.com/download/) or higher is required.  
It might be possible to open the generated _.3dm_ files with an older version, although this has not been tested.

### Word
From the program a report in .docx format is written to the Output folder. To view this file I used [Microsoft Word](https://www.microsoft.com/de-de/microsoft-365/word).
It should be possible to access the _.docx_ file using [Google Docs](https://workspace.google.com/intl/de/products/docs/) or [LibreOffice](https://de.libreoffice.org/). 
This was not tested so formatting issues might occur.


# Installation
To run this project locally, follow these steps:
1. Clone the repository
    ```bash
   git clone https://github.com/Dobby43/Master-Thesis
   cd repository
    ```
2. Create a virtual environment
    ```bash
    python -m venv .venv
    source .venv/bin/activate      # On Linux/macOS
    .venv\Scripts\activate         # On Windows
    ```
3. Install python dependencies
    ```bash
    pip install -r requirements.txt
    ```
> ⚠️ Make sure that Rhino 8 is installed to use the dependency _rhinoinside_

# Usage

5. Usage (Description)
6. Configuration
7. Example usage
8. Trouble shooting

