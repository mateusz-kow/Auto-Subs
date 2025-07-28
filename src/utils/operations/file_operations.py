from typing import Any


def generate_ass_header(settings: dict[str, Any]) -> str:
    """Generates the ASS file header section using the provided settings.

    Args:
        settings (dict): A dictionary containing ASS header and style settings.

    Returns:
        str: The formatted ASS header string.
    """
    return (
        f"[Script Info]\n"
        f"Title: {settings.get('title', 'Untitled')}\n"
        f"ScriptType: v4.00+\n"
        f"Collisions: Normal\n"
        f"PlayResX: {settings.get('play_res_x', 1920)}\n"
        f"PlayResY: {settings.get('play_res_y', 1080)}\n"
        f"WrapStyle: {settings.get('wrap_style', 0)}\n"
        f"ScaledBorderAndShadow: {settings.get('scaled_border_and_shadow', 1)}\n"
        f"[V4+ Styles]\n"
        f"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        f"OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        f"ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        f"Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{settings.get('font')},{settings.get('font_size')},"
        f"{settings.get('primary_color')},{settings.get('secondary_color')},"
        f"{settings.get('outline_color')},{settings.get('back_color')},"
        f"{settings.get('bold')},{settings.get('italic')},{settings.get('underline')},"
        f"{settings.get('strikeout')},{settings.get('scale_x')},{settings.get('scale_y')},"
        f"{settings.get('spacing_spinbox')},{settings.get('angle')},{settings.get('border_style')},"
        f"{settings.get('outline')},{settings.get('shadow')},{settings.get('alignment')},"
        f"{settings.get('margin_l')},{settings.get('margin_r')},{settings.get('margin_v')},"
        f"{settings.get('encoding')}\n"
        f"[Events]\n"
        f"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
