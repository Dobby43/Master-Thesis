import re
from get_g_code import get_gcode_lines

def modify_gcode_line(gcode_lines):
    """
    Modifies a G-code line by replacing G1 with LIN and extracting the X and Y values.
    The output is formatted as: LIN {X <X-value>, Y <Y-value>, Z 10}

    Args:
        line (str): The original G-code line.

    Returns:
        str: The modified G-code line in the desired format.
    """
    # Step 1: Replace G1 with LIN
    modified_line = gcode_lines.replace('G1', 'LIN')

    # Step 2: Extract X and Y values using regex
    x_value = None
    y_value = None

    # Find the values after 'X' and 'Y'
    x_match = re.search(r'X([\d\.-]+)', line)
    y_match = re.search(r'Y([\d\.-]+)', line)

    if x_match:
        x_value = x_match.group(1)
    if y_match:
        y_value = y_match.group(1)

    # Step 3: Format the new line in the desired format
    # Assuming Z is always 10
    if x_value and y_value:
        return f'LIN {{X {x_value}, Y {y_value}, Z 10}}'
    else:
        return 'Invalid G-code format - missing X or Y values'