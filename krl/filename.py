def set_filename_krl(filename: str) -> list[str]:
    """
    Formats a given filename to be used in a KRL DEF statement.
    """
    # Remove spaces and limit to 25 characters
    filename_formatted = filename.replace(" ", "_")[:25]

    # Return formatted string
    return [f"DEF {filename_formatted} ()"]
