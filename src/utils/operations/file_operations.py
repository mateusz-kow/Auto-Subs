from typing import Any


def generate_ass_header(settings: dict[str, Any]) -> str:
    """
    Generates the ASS file header section using the provided settings.

    Args:
        settings (dict): A dictionary containing ASS header and style settings.

    Returns:
        str: The formatted ASS header string.
    """
    return f"""[Script Info]
Title: {settings.get('title', 'Untitled')}
ScriptType: v4.00+
Collisions: Normal
PlayResX: {settings.get('play_res_x', 1920)}
PlayResY: {settings.get('play_res_y', 1080)}
WrapStyle: {settings.get('wrap_style', 0)}
ScaledBorderAndShadow: {settings.get('scaled_border_and_shadow', 1)}
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{settings.get('font')},{settings.get('font_size')},{settings.get('primary_color')},{settings.get('secondary_color')},{settings.get('outline_color')},{settings.get('back_color')},{settings.get('bold')},{settings.get('italic')},{settings.get('underline')},{settings.get('strikeout')},{settings.get('scale_x')},{settings.get('scale_y')},{settings.get('spacing_spinbox')},{settings.get('angle')},{settings.get('border_style')},{settings.get('outline')},{settings.get('shadow')},{settings.get('alignment')},{settings.get('margin_l')},{settings.get('margin_r')},{settings.get('margin_v')},{settings.get('encoding')}
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
