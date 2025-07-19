from PySide6.QtGui import QColor


def ass_to_qcolor(ass_color: str) -> QColor:
    """
    Converts an ASS subtitle color string to a QColor object.

    Args:
        ass_color (str): The ASS color string in the format "&HAABBGGRR" or "AABBGGRR".

    Returns:
        QColor: A QColor object representing the color with the appropriate alpha value.
    """
    # Remove the "&H" prefix if present and ensure the string is 8 characters long
    hex_str = ass_color[2:] if ass_color.startswith("&H") else ass_color
    hex_str = hex_str.zfill(8)  # Ensure it's always 8 digits (AABBGGRR)

    # Extract color components
    rr = int(hex_str[6:8], 16)
    gg = int(hex_str[4:6], 16)
    bb = int(hex_str[2:4], 16)
    aa = int(hex_str[0:2], 16)

    # Convert ASS alpha (00 = opaque, FF = transparent) to QColor alpha
    alpha = 255 - aa

    # Create and return the QColor object
    color = QColor(rr, gg, bb)
    color.setAlpha(alpha)
    return color


def qcolor_to_ass(qcolor: QColor) -> str:
    """
    Converts a QColor object to an ASS subtitle color string.

    Args:
        qcolor (QColor): The QColor object to convert.

    Returns:
        str: The ASS color string in the format "&HAABBGGRR".
    """
    # Convert QColor alpha (0 = transparent, 255 = opaque) to ASS alpha
    alpha = 255 - qcolor.alpha()

    # Extract RGB components
    r = qcolor.red()
    g = qcolor.green()
    b = qcolor.blue()

    # Format and return the ASS color string
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"
