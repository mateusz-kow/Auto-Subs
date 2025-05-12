import os
from typing import Dict
from src.utils.file_operations import generate_ass_header
from src.utils.constants import TEMP_DIR


class SubtitleGenerator:
    @staticmethod
    def to_ass(subtitles, ass_settings: Dict[str, any], output_path: str = None) -> str:
        def format_ass_timestamp(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            cs = int((seconds - int(seconds)) * 100)
            return f"{h}:{m:02}:{s:02}.{cs:02}"

        lines = [generate_ass_header(ass_settings)]
        highlight_style = ass_settings.get("highlight_style")

        for segment in subtitles.segments:
            start = format_ass_timestamp(segment.start)
            end = format_ass_timestamp(segment.end)
            if highlight_style:
                text = " ".join([f"{highlight_style}{word.text}" for word in segment.words])
            else:
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
