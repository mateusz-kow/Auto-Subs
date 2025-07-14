import uuid
from logging import getLogger
from pathlib import Path
from typing import Any

from src.subtitles.models import Subtitles
from src.utils.constants import TEMP_DIR
from src.utils.file_operations import generate_ass_header

logger = getLogger(__name__)

HIGHLIGHT_END = r"{\\r}"


class SubtitleGenerator:
    """Utility class for generating subtitle files in ASS and SRT formats."""

    @staticmethod
    def to_ass(subtitles: Subtitles, ass_settings: dict[str, Any], output_path: Path | None = None) -> Path:
        """
        Generate an ASS subtitle file from the given subtitles and settings.

        This method creates an ASS (Advanced SubStation Alpha) subtitle file
        using the provided subtitles and styling settings. It supports optional
        highlighting of specific words and offsets the timestamps based on the
        provided `timestamp` parameter.

        Args:
            subtitles (Subtitles): The subtitles to export, containing segments and words.
            ass_settings (Dict[str, Any]): ASS-specific settings, including styles and optional highlight styles.
            output_path (Path, optional): Path to save the generated file. If not provided, a temporary file is created.

        Returns:
            Path: The path to the generated ASS file.
        """

        def format_ass_timestamp(seconds: float) -> str:
            """Format a timestamp in seconds to ASS format (h:mm:ss.cs)."""
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            cs = int((seconds - int(seconds)) * 100)
            return f"{h}:{m:02}:{s:02}.{cs:02}"

        def build_ass_highlight_tag(style_dict: dict[str, Any]) -> str:
            """Build ASS highlight tags based on the provided style dictionary."""
            tag = r"{"
            if "text_color" in style_dict:
                tag += rf"\1c{style_dict['text_color']}"
            if "border_color" in style_dict:
                tag += rf"\3c{style_dict['border_color']}"
            if style_dict.get("fade"):
                tag += r"\fad(50,50)"
            tag += "}"
            return tag

        lines = [generate_ass_header(ass_settings)]
        highlight_style_dict = ass_settings.get("highlight_style")

        if highlight_style_dict:
            highlight_tag = build_ass_highlight_tag(highlight_style_dict)
            for segment in subtitles.segments:
                for h_index, highlighted_word in enumerate(segment.words):
                    text = []
                    start = format_ass_timestamp(highlighted_word.start)
                    if len(segment.words) > h_index + 1:
                        end = format_ass_timestamp(segment.words[h_index + 1].start)
                    else:
                        end = format_ass_timestamp(highlighted_word.end)

                    for o_index, other_word in enumerate(segment.words):
                        if h_index == o_index:
                            text.append(f"{highlight_tag}{highlighted_word.text}{HIGHLIGHT_END}")
                        else:
                            text.append(other_word.text)

                    lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{' '.join(text)}")
        else:
            for segment in subtitles.segments:
                start = format_ass_timestamp(segment.start)
                end = format_ass_timestamp(segment.end)
                text = [str(segment)]
                lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{' '.join(text)}")

        lines.append("")

        if output_path is None:
            output_path = Path(TEMP_DIR) / f"{uuid.uuid4()}_subs.ass"
        elif not isinstance(output_path, Path):
            assert output_path is not None
            output_path = Path(output_path)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        logger.info(f"Generated subtitles in {output_path}")
        return output_path

    @staticmethod
    def to_srt(subtitles: Subtitles, output_path: Path | None = None) -> Path:
        """
        Generate an SRT subtitle file from the given subtitles.

        Args:
            subtitles (Subtitles): The subtitles to export.
            output_path (Path, optional): Path to save the generated file. Defaults to a temporary file.

        Returns:
            Path: The path to the generated SRT file.
        """

        def format_to_srt_time(seconds: float) -> str:
            """Format a timestamp in seconds to SRT format (hh:mm:ss,ms)."""
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

        if output_path is None:
            output_path = Path(TEMP_DIR) / f"{uuid.uuid4()}_subs.srt"
        elif not isinstance(output_path, Path):
            output_path = Path(output_path)

        with open(output_path, "w", encoding="utf-8") as file:
            srt_lines = []
            for index, segment in enumerate(subtitles.segments, start=1):
                start_time = format_to_srt_time(segment.start)
                end_time = format_to_srt_time(segment.end)
                text = str(segment)

                srt_lines.append(f"{index}")
                srt_lines.append(f"{start_time} --> {end_time}")
                srt_lines.append(text)
                srt_lines.append("")

            file.write("\n".join(srt_lines))

        logger.info(f"Generated subtitles in {output_path}")
        return output_path

    @staticmethod
    def to_txt(subtitles: Subtitles, output_path: Path | None = None) -> Path:
        if output_path is None:
            output_path = Path(TEMP_DIR) / f"{uuid.uuid4()}_subs.txt"
        elif not isinstance(output_path, Path):
            output_path = Path(output_path)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(str(subtitles))

        logger.info(f"Generated subtitles in {output_path}")
        return output_path
