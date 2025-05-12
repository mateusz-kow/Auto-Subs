def generate_ass_header(settings: dict) -> str:
    """
    Generates the ASS file header section.

    Args:
        settings (dict): A dictionary containing settings like title, font, etc.

    Returns:
        str: The header string for the ASS file format.
    """
    return f"""[Script Info]
Title: {settings['title']}
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, Bold, Italic, Alignment, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow, Encoding
Style: Default,{settings['font']},{settings['font_size']},{settings['primary_color']},{settings['bold']},{settings['italic']},{settings['alignment']},{settings['margin_l']},{settings['margin_r']},{settings['margin_v']},{settings['border_style']},{settings['outline']},{settings['shadow']},{settings['encoding']}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
