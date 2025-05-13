import os
from typing import Dict

from src.subtitles.models import Subtitles
from src.utils.file_operations import generate_ass_header
from src.utils.constants import TEMP_DIR

HIGHLIGHT_END = r"{\\r}"


class SubtitleGenerator:
    @staticmethod
    def to_ass(subtitles: Subtitles, ass_settings: Dict[str, any], output_path: str = None) -> str:
        def format_ass_timestamp(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            cs = int((seconds - int(seconds)) * 100)
            return f"{h}:{m:02}:{s:02}.{cs:02}"

        lines = [generate_ass_header(ass_settings)]
        highlight_style = ass_settings.get("highlight_style")

        if highlight_style:
            for segment in subtitles.segments:
                for h_index, highlighted_word in enumerate(segment.words):
                    text = []
                    start = format_ass_timestamp(highlighted_word.start)
                    end = format_ass_timestamp(highlighted_word.end)

                    for o_index, other_word in enumerate(segment.words):
                        if h_index == o_index:
                            text.append(f"{highlight_style}{highlighted_word.text}{HIGHLIGHT_END}")
                        else:
                            text.append(other_word.text)

                    lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{" ".join(text)}")

        else:
            for segment in subtitles.segments:
                start = format_ass_timestamp(segment.start)
                end = format_ass_timestamp(segment.end)
                text = str(segment)

                lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        lines.append("")
        if not output_path:
            output_path = os.path.join(TEMP_DIR, "temp.ass")

        with open(output_path, "w") as file:
            file.write("\n".join(lines))

        return output_path

    @staticmethod
    def to_srt(subtitles, output_path: str = None) -> str:
        def format_to_srt_time(seconds: float) -> str:
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

        if not output_path:
            output_path = os.path.join(TEMP_DIR, "subtitles.srt")

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

        return output_path
