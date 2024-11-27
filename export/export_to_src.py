import os


def export_to_src(
    setup: str,
    init: str,
    sta_conc_print: str,
    end_conc_print: str,
    bco: str,
    move: str,
    code: list,
    file_directory: str,
    file_name: str,
):
    """
    Exports a list of KRL code lines with setup and initialization text blocks to a .src file.

    :param setup: Project setup text block.
    :param init: Initialization text block.
    :param con_prin: Concrete printing configuration text block.
    :param bco: Block coordinates (BCO) text block.
    :param move: Motion settings text block.
    :param code: List of KRL code lines to export.
    :param file_directory: Directory where the .src file should be saved.
    :param file_name: Name of the .src file (without extension).
    """
    # collects all given textblocks
    text_blocks_start = [
        block if block is not None else ""
        for block in [setup, init, sta_conc_print, bco, move]
    ]

    text_blocks_end = [block if block is not None else "" for block in [end_conc_print]]

    # Zusammenfügen der Textbausteine und des eigentlichen Codes
    full_krl_code = (
        "".join(text_blocks_start) + "".join(code) + "".join(text_blocks_end)
    )

    full_path = os.path.join(file_directory, f"{file_name}.src")

    # writes complete KRL-Code to give path
    with open(full_path, "w") as file:
        file.write(full_krl_code)

    print(f"Export completed. File saved at: {full_path}")
