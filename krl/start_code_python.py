def set_start_code_python(layers: int) -> list[str]:
    """
    DESCRIPTION:
    builds the start code from values acquired in the python code (apriori unknown values)

    :param layers: maximum layer count to track print progress

    :return: list of strings to insert into .src file between setup.Robot.start_code.json and krl lines from modify to krl
    """
    start_code = [f"LAYER_MAX = {layers}"]
    return start_code
