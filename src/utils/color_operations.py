from PySide6.QtGui import QColor


def ass_to_qcolor(ass_color: str):
    hex_str = ass_color[2:] if ass_color.startswith("&H") else ass_color
    hex_str = hex_str.zfill(8)  # Ensure it's always 8 digits (AABBGGRR)

    rr = int(hex_str[6:8], 16)
    gg = int(hex_str[4:6], 16)
    bb = int(hex_str[2:4], 16)

    aa = int(hex_str[0:2], 16)
    alpha = 255 - aa  # ASS alpha: 00 = opaque, FF = transparent
    color = QColor(rr, gg, bb)
    color.setAlpha(alpha)
    return color


def qcolor_to_ass(qcolor: QColor):
    alpha = 255 - qcolor.alpha()  # ASS: 0 = opaque, 255 = transparent
    r = qcolor.red()
    g = qcolor.green()
    b = qcolor.blue()
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"
