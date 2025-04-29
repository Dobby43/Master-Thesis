from typing import Any


def format_value(value: Any, precision: int = 2) -> str:
    """
    DESCRIPTION:
    Formating of values depending on their type for placeholders in Robot.start_code and Robot.end_code

    :param value: The value to be formatted
    :param precision: The number of decimal places to show

    :return: The formatted value
    """

    if isinstance(value, dict):
        return ", ".join(f"{k} {format_value(v, precision)}" for k, v in value.items())
    elif isinstance(value, list):
        return "[" + ", ".join(format_value(v, precision) for v in value) + "]"
    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    elif isinstance(value, float):
        return f"{value:.{precision}f}"
    return str(value)


import re


def replace_placeholders(
    text: str, settings: dict, precision: int = 2
) -> tuple[str, bool]:
    """
    DESCRIPTION:
    Replaces all ?key? placeholders in the given text with values from settings["Robot"][key]["value"].
    Returns the replaced text and a success flag.

    :param text: The text with the placeholders (e.g. Robot.start_code, Robot.end_code)
    :param settings: The settings dictionary (with all available placeholders)
    :param precision: Number of decimal places to use when formatting values

    :return: A tuple of (replaced text, success flag)
    """
    robot_values = settings.get("Robot", {})
    pattern = re.compile(r"\?([a-z0-9_]+)\?")
    all_keys_found = True

    def replacer(match: re.Match) -> str:
        nonlocal all_keys_found
        key = match.group(1)
        entry = robot_values.get(key)
        if entry is not None:
            return format_value(entry["value"], precision)
        else:
            print(f"[ERROR] Key ?{key}? inside robot start or end code not found")
            print(f"[WARNING] Key ?{key}? not replaced")
            all_keys_found = False
            return f"?{key}?"

    replaced_text = pattern.sub(replacer, text)
    return replaced_text, all_keys_found
