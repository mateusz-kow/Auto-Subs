def generate_ass_header(settings: dict) -> str:
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
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
