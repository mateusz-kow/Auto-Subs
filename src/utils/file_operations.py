def generate_ass_header(settings: dict) -> str:
    """
    Generates the ASS file header section using fallback defaults from DEFAULT dict.

    Args:
        settings (dict): User-specified settings.
        default (dict): Default fallback values.

    Returns:
        str: ASS header string.
    """
    get = lambda key: settings.get(key)

    return f"""[Script Info]
Title: {get('title')}
ScriptType: v4.00+
Collisions: Normal
PlayResX: {get('play_res_x')}
PlayResY: {get('play_res_y')}
WrapStyle: {get('wrap_style')}
ScaledBorderAndShadow: {get('scaled_border_and_shadow')}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{get('font')},{get('font_size')},{get('primary_color')},{get('secondary_color')},{get('outline_color')},{get('back_color')},{get('bold')},{get('italic')},{get('underline')},{get('strikeout')},{get('scale_x')},{get('scale_y')},{get('spacing_spinbox')},{get('angle')},{get('border_style')},{get('outline')},{get('shadow')},{get('alignment')},{get('margin_l')},{get('margin_r')},{get('margin_v')},{get('encoding')}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
