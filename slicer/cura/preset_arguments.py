from typing import Union


def def_preset_arguments(
    machine_name: str,
    bed_size: dict,
    flow: dict,
    pump_retract: bool,
    scaling: str,
    filament_dia: float,
) -> dict[str, Union[int, float, bool, str]]:
    """
    DESCRIPTION:
    Returns a dictionary of input parameters from setup.json and by default fixed values for the slicer

    :param machine_name: name of the 3D printer
    :param bed_size: dictionary with bed sizes (x,y,z)
    :param flow: dictionary with flow parameters
    :param pump_retract: determines if the pump is capable of retraction
    :param scaling: dictionary with scaling parameters (calculated in scaling_matrix)
    :param filament_dia: diameter of the filament used

    :return: dictionary of fixed values for the slicer
    """
    preset = {
        "machine_name": machine_name,  # match "id" from Robot.setup.json
        "machine_width": bed_size["X"],  # match "bed_size" from Robot.setup.json
        "machine_depth": bed_size["Y"],  # match "bed_size" from Robot.setup.json
        "machine_height": bed_size["Z"],  # match "bed_size" from Robot.setup.json
        "machine_show_variants": False,  # allows only one variant of machine
        "material_guid": "",  #
        "material_type": "",  # no material specified
        "material_brand": "",  #
        "machine_shape": "rectangular",  # circular shape not compatible with Rhino implementation and Report
        "machine_extruder_count": 1,  # no dual extruder possible
        "extruders_enabled_count": 0,
        "machine_firmware_retract": False,  # No G10 or G11 commands to specify retractions
        "initial_layer_line_width_factor": 100,  # line width for layer 0 fixed to 100 %
        "ironing_enabled": False,  # not possible to differentiate between surface and ironing; therefor disabled
        "wall_0_material_flow": flow[
            "wall_outer"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "wall_x_material_flow": flow[
            "wall_inner"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "wall_0_material_flow_roofing": flow[
            "wall_outer"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "wall_x_material_flow_roofing": flow[
            "wall_inner"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "skin_material_flow": flow[
            "surface"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "roofing_material_flow": flow[
            "surface"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "infill_material_flow": flow[
            "infill"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "skirt_brim_material_flow": flow[
            "curb"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "support_material_flow": flow[
            "support"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "support_roof_material_flow": flow[
            "support"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "support_bottom_material_flow": flow[
            "support"
        ],  # to match "linetype_flow" input from Pump.setup.json
        "prime_tower_flow": 100,  # as default flow for not specified line types is 100% and prime tower has not been tested
        "material_flow_layer_0": 100,  # flow for layer 0 fixed to 100%; no bed adhesion problems for concrete 3D-printing
        "retraction_enable": pump_retract,  # to match "retract" input from Pump.setup.json
        "retraction_hop_enabled": False,  # could disturb layer_height calculation; therefor deactivated
        "layer_0_z_overlap": 0,  # could disturb layer_height calculation; therefor deactivated
        "wipe_hop_enable": False,  # could disturb layer_height calculation; therefor deactivated
        "mesh_rotation_matrix": scaling,  # calculated for "cura_scaling" from Cura.setup.json via module scaling_matrix.py
        "filament_diameter": filament_dia,  # to match "filament_diameter" input from Pump.setup.json and recalculate E-value correctly
    }

    return preset
