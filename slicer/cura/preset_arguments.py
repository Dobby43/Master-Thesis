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
        "machine_name": machine_name,
        "machine_width": bed_size["X"],
        "machine_depth": bed_size["Y"],
        "machine_height": bed_size["Z"],
        "machine_show_variants": False,
        "material_guid": "",
        "material_type": "",
        "material_brand": "",
        "machine_shape": "rectangular",
        "machine_extruder_count": 1,
        "extruders_enabled_count": 0,
        "machine_firmware_retract": False,
        "initial_layer_line_width_factor": 100,
        "ironing_enabled": False,
        "wall_0_material_flow": flow["wall_outer"],
        "wall_x_material_flow": flow["wall_inner"],
        "wall_0_material_flow_roofing": flow["wall_outer"],
        "wall_x_material_flow_roofing": flow["wall_inner"],
        "skin_material_flow": flow["surface"],
        "roofing_material_flow": flow["surface"],
        "infill_material_flow": flow["infill"],
        "skirt_brim_material_flow": flow["curb"],
        "support_material_flow": flow["support"],
        "support_roof_material_flow": flow["support"],
        "support_bottom_material_flow": flow["support"],
        "prime_tower_flow": 100,
        "material_flow_layer_0": 100,
        "retraction_enable": pump_retract,
        "retraction_hop_enabled": False,
        "layer_0_z_overlap": 0,
        "wipe_hop_enable": False,
        "mesh_rotation_matrix": scaling,
        "filament_diameter": filament_dia,
    }

    return preset
