"""
This file contains the basis for all adjacent functions
"""

__author__ = "<DAVID SCHEIDT>"
__email__ = "<<david.scheidt@tum.de>>"
__version__ = "1.0"

import os
import math
import sys

import numpy as np
import matplotlib.pyplot as plt

# Example usage in main.py

import get_g_code

# Directory and file name
directory = r'C:\Users\daves\OneDrive\Bauingenieurwesen\Masterarbeit\G_Code'
file_name = 'Cura_23_10_CFFFP_FlowCalibrationCube.gcode'

# Read the G-code lines
gcode_lines = get_g_code.get_gcode_lines(directory, file_name)

# Process the lines
for line in gcode_lines:
    print(line.strip())
