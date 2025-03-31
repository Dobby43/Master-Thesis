from typing import Any, Dict
from setup.load_settings import load_settings


def validate_value(value: Any, expected_type: str) -> bool:
    """
    DESCRIPTION:
    Validates values for given type in setup.json file '(float', 'list[str]', 'dict[str, int|float]', etc.)

    :param value: value to validate
    :param expected_type: expected type of value (saved under "type" in setup.json)

    :return: returns a bool; if actual type == expected type -> true, else false
    """

    # ---------------------- UNION-TYPE (e.g "int|float") ----------------------
    if "|" in expected_type and not expected_type.startswith("dict["):
        subtypes = [t.strip() for t in expected_type.split("|")]
        return any(validate_value(value, subtype) for subtype in subtypes)

    # ---------------------- STANDARD TYPES ----------------------
    if expected_type == "str":
        return isinstance(value, str)
    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "float":
        return isinstance(value, (float, int)) and not isinstance(value, bool)
    if expected_type == "bool":
        return isinstance(value, bool)

    # ---------------------- SPECIAL list[list[float,float,float]] ----------------------
    if expected_type == "list[list[float,float,float]]":
        if not isinstance(value, list):
            return False
        for inner in value:
            if not (isinstance(inner, list) and len(inner) == 3):
                return False
            for i in inner:
                if isinstance(i, bool) or not isinstance(i, (float, int)):
                    return False
        return True

    # ---------------------- LIST OF SINGLE TYPE ----------------------
    if expected_type.startswith("list[") and expected_type.endswith("]"):
        subtype = expected_type[5:-1]
        return isinstance(value, list) and all(
            validate_value(item, subtype) for item in value
        )

    # ---------------------- LIST OF LIST ----------------------
    if expected_type.startswith("list[list[") and expected_type.endswith("]]"):
        subtype = expected_type[10:-2]
        return isinstance(value, list) and all(
            isinstance(inner, list) and all(validate_value(i, subtype) for i in inner)
            for inner in value
        )

    # ---------------------- DICTIONARY WITH COMMA SEPERATED KEY,VALUE ----------------------
    if expected_type.startswith("dict[") and expected_type.endswith("]"):
        inner = expected_type[5:-1]

        key_type, value_type = map(str.strip, inner.split(",", maxsplit=1))

        return isinstance(value, dict) and all(
            validate_value(k, key_type) and validate_value(v, value_type)
            for k, v in value.items()
        )

    return False


def validate_settings(user_settings: Dict[str, Dict[str, Dict[str, Any]]]) -> None:
    """
    DESCRIPTION:
    Strictly validates all values in the settings dict.
    If an entry is invalid, a ValueError is thrown with a summary of all errors.

    :param user_settings: settings dict (nested dict of settings from setup.json)
    """
    errors = []

    for section, keys in user_settings.items():
        for key, entry in keys.items():
            value = entry.get("value")
            type_str = entry.get("type")

            if not validate_value(value, type_str):
                errors.append(
                    f"[WARNING] settings.{section}.{key}: Invalid value '{value}' for type '{type_str}'\n"
                )

    if errors:
        error_msg = "\n".join(errors)
        raise ValueError(f"[ERROR] Configuration error found\n{error_msg}")


if __name__ == "__main__":
    from pathlib import Path

    setup_path = Path(__file__).parent / "setup.json"
    settings = load_settings(str(setup_path))

    try:
        validate_settings(settings)
        print("[INFO] Alle Eingaben sind gültig.")
    except ValueError as e:
        print(e)
        print("[ERROR] Programm wird beendet.")
        exit(1)
