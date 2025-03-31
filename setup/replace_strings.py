import re
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


def replace_placeholders(text: str, settings: dict, precision: int = 2) -> str:
    """
    DESCRIPTION:
    Replaces all ?key? placeholders in the given text with values ?key? from settings ["settings"]["Robot"][key]["value"].
    Returns the replaced text as a string.

    :param text: The text with the placeholders (Robot.start_code, Robot.end_code)
    :param settings: The settings dictionary (with all available placeholders)
    :param precision: The number of decimal places to show for the replaced key

    :return: The replaced text as a string
    """
    robot_values = settings.get("Robot", {})
    pattern = re.compile(r"\?([a-z0-9_]+)\?")

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        entry = robot_values.get(key)
        if entry is not None:
            return format_value(entry["value"], precision)
        else:
            print(f"[ERROR] Key {key} inside robot start or end code not found")
            print(f"[WARNING] Key {key} not replaced; Check start code")
            return f"?{key}?"  # Unknown key stays visible

    return pattern.sub(replacer, text)
