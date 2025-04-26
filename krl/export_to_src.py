import os


def export_to_src(
    krl_lines: list[str],
    file_name_krl: str,
    start_code_json: list[str],
    start_code_python: list[str],
    end_code_json: list[str],
    end_code_python: list[str],
    output_path: str,
    file_name: str,
) -> None:
    """
    DESCRIPTION:
    Combines robot start/end code and KRL lines into a single .src file.

    :param krl_lines: list of str formatted in KRL
    :param file_name_krl: str formatted in KRL (used inside file)
    :param start_code_json: list of str from setup.Robot.start_code.json formatted in KRL
    :param start_code_python: list of str from krl.start_code_python.py formatted in KRL
    :param end_code_json: list of str from setup.Robot.end_code.json formatted in KRL
    :param end_code_python: list of str from krl.start_code_python.py formatted in KRL (currently not used)
    :param output_path: path to the output file
    :param file_name: name of the output file
    """
    if not output_path.endswith(("/", "\\")):
        output_path += "/"

    combined_lines = (
        [f"DEF {file_name_krl} ()"]
        + [""]
        + start_code_json
        + [""]
        + start_code_python
        + [""]
        + krl_lines
        + [""]
        + end_code_python
        + [""]
        + end_code_json
    )

    full_file_path = f"{output_path}{file_name}.src"

    try:
        with open(full_file_path, "w") as file:
            file.write("\n".join(combined_lines))
        print(f"[INFO] .src file exported to {full_file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to export .src file: {e}")


def split_and_export_to_src(
    krl_lines: list[list[str]],
    file_name_krl: str,  # used as base name for subprograms
    start_code_json: list[str],
    start_code_python: list[str],
    end_code_json: list[str],
    end_code_python: list[str],
    output_path: str,
    file_name: str,  # used for the folder and the main file name
) -> None:
    """
    Exports KRL code split by LAYER = lines into subfiles and a master .src file.

    :param krl_lines: list of str formatted in KRL
    :param file_name_krl: str formatted in KRL (used as base name for subprograms)
    :param start_code_json: list of str from setup.Robot.start_code.json formatted in KRL
    :param start_code_python: list of str from krl.start_code_python.py formatted in KRL
    :param end_code_json: list of str from setup.Robot.end_code.json formatted in KRL
    :param end_code_python: list of str from krl.start_code_python.py formatted in KRL (currently not used)
    :param output_path: path to the output file
    :param file_name: name of the output file (used for the folder and the main file name)
    """

    # Create subdirectory
    folder_name = f"{file_name}_SRC"
    folder_path = os.path.join(output_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    blocks = krl_lines

    # Create list of subprogram call names
    sub_names = [f"{file_name_krl.upper()}_{i:03d} ()" for i in range(len(blocks))]

    # Combine main file with program calls only
    combined_main = (
        [f"DEF {file_name[:25]} ()"]
        + [""]
        + start_code_json
        + [""]
        + start_code_python
        + [""]
        + sub_names
        + [""]
        + end_code_python
        + [""]
        + end_code_json
    )

    # Write main file
    main_file_path = os.path.join(folder_path, f"{file_name}.src")
    try:
        with open(main_file_path, "w") as file:
            file.write("\n".join(combined_main))
        print(f"[INFO] Main .src file written to {main_file_path}")
    except Exception as e:
        print(f"[ERROR] Could not write main .src file: {e}")

    # Write subfiles
    for i, block in enumerate(blocks):
        sub_name = f"{file_name_krl}_{i:03d}.src"
        sub_path = os.path.join(folder_path, sub_name)
        sub_content = block
        try:
            with open(sub_path, "w") as subfile:
                subfile.write("\n".join(sub_content))
            print(f"[INFO] Subfile written: {sub_path}")
        except Exception as e:
            print(f"[ERROR] Could not write subfile {sub_name}: {e}")
