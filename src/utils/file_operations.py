DEFAULT = {
    'title': 'Untitled',
    'font': 'Arial',
    'font_size': 36,
    'primary_color': '&H00FFFFFF',
    'secondary_color': '&H000000FF',
    'outline_color': '&H00000000',
    'back_color': '&H64000000',
    'bold': 0,
    'italic': 0,
    'underline': 0,
    'strikeout': 0,
    'scale_x': 100,
    'scale_y': 100,
    'spacing': 0,
    'angle': 0,
    'border_style': 1,
    'outline': 1,
    'shadow': 0,
    'alignment': 2,
    'margin_l': 10,
    'margin_r': 10,
    'margin_v': 10,
    'encoding': 1,
    'play_res_x': 1920,
    'play_res_y': 1080,
    'wrap_style': 0,
    'scaled_border_and_shadow': 'yes'
}


def generate_ass_header(settings: dict, default: dict = DEFAULT) -> str:
    """
    Generates the ASS file header section using fallback defaults from DEFAULT dict.

    Args:
        settings (dict): User-specified settings.
        default (dict): Default fallback values.

    Returns:
        str: ASS header string.
    """
    get = lambda key: settings.get(key, default.get(key))

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
Style: Default,{get('font')},{get('font_size')},{get('primary_color')},{get('secondary_color')},{get('outline_color')},{get('back_color')},{get('bold')},{get('italic')},{get('underline')},{get('strikeout')},{get('scale_x')},{get('scale_y')},{get('spacing')},{get('angle')},{get('border_style')},{get('outline')},{get('shadow')},{get('alignment')},{get('margin_l')},{get('margin_r')},{get('margin_v')},{get('encoding')}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
