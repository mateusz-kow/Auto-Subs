# Auto Subs: Automatic Subtitle Generator & Editor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-PySide6-cyan.svg)](https://www.qt.io/qt-for-python)

Auto Subs is a free and open-source desktop application designed to simplify and accelerate the process of generating and editing subtitles for video files. Leveraging the power of OpenAI's Whisper for accurate speech recognition, it provides a user-friendly interface for transcribing audio, refining segments, styling captions, and exporting them in various formats. It's an ideal tool for content creators, educators, translators, and anyone needing quick and precise video transcriptions.

## ✨ Key Features

*   **🎤 Automatic Speech Recognition:** High-accuracy transcription using local Whisper models.
*   **🎞️ Wide Video Format Support:** Works with popular video formats (MP4, MKV, AVI, etc.) via FFmpeg.
*   **🎬 Integrated Video Preview:** See your subtitles on the video as you edit (powered by VLC).
*   **✍️ Intuitive Subtitle Editor:**
    *   Segment and word-level editing.
    *   Adjust timestamps with ease.
    *   Merge or split subtitle segments.
*   **🎨 Advanced Styling Options:**
    *   Customize font, size, colors (primary, secondary, outline, background).
    *   Control alignment, margins, border styles, shadow.
    *   Apply highlight styles for specific words or phrases.
    *   Save and load custom style presets.
*   **📤 Multiple Export Formats:** Export subtitles as `.srt`, `.ass`, or plain `.txt`.
*   **🔥 Burn-in Subtitles:** Option to export the video with subtitles embedded directly (hardsubs).
*   **🖥️ Clean Desktop Interface:** Built with PySide6 (Qt for Python) for a native look and feel.
*   **🔒 Works Offline:** Transcription and editing are performed locally after initial model download. No internet connection required for core functionality.
*   **💸 Free & Open Source:** Licensed under MIT.

## 📸 Screenshots

*(Placeholder for screenshots of the application in action. e.g., main interface, style editor, subtitle editor view)*
*   `[Image of main application window]`
*   `[Image of style customization panel]`
*   `[Image of subtitle timeline editor]`

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Python:** Version 3.9 or newer. ([Download Python](https://www.python.org/downloads/))
2.  **FFmpeg:** Required for audio extraction from videos and burning subtitles.
    *   Download from [ffmpeg.org](https://ffmpeg.org/download.html).
    *   Ensure `ffmpeg` (and `ffprobe`) are added to your system's PATH.
3.  **VLC Media Player:** Required for the embedded video preview functionality.
    *   Download from [videolan.org](https://www.videolan.org/vlc/).
    *   The `python-vlc` library will also need access to the VLC installation (usually handled automatically if VLC is installed in a standard location).
4.  **Git:** For cloning the repository. ([Download Git](https://git-scm.com/downloads))

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ozzy-420/auto-subs.git
    cd auto-subs
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    The project uses PyTorch for Whisper. If you have a dedicated NVIDIA GPU, you might want to install a CUDA-enabled version of PyTorch first by following instructions on the [PyTorch website](https://pytorch.org/get-started/locally/). Otherwise, the CPU version will be installed.

    ```bash
    pip install -r requirements.txt
    ```
    *(Note: The `requirements.txt` should include `python-vlc` if it's not already there. If `torch` installation is problematic, refer to PyTorch's official installation guide for your specific OS and hardware.)*

4.  **Whisper Model Download:**
    The first time you run the application or try to transcribe, the specified Whisper model (e.g., "base", "small", "medium") will be downloaded. This requires an internet connection for the initial download. Subsequent uses will be offline. The default model is `WHISPER_MODEL` in `src/utils/constants.py`.

### Running the Application

Once the setup is complete, you can run the application using:

```bash
python main.py
```

## 🛠️ How to Use

1.  **Import Video:** Click "File" > "Import MP4" to load your video.

2.  **Automatic Transcription:** Transcription will start automatically once a video is loaded. The progress might be indicated in the console or a status bar (if implemented).

3.  **Edit Subtitles:**
    *   The transcribed segments will appear in the subtitles panel.
    *   Select a segment to view and edit its words in the word editor.
    *   Modify text, start/end times for words or segments.
    *   Use context menus (right-click) to delete or merge items.

4.  **Style Subtitles:**
    *   Use the "Style" panel to adjust font, colors, alignment, and other visual properties.
    *   Configure highlight styles for dynamic emphasis.
    *   Save your favorite styles or load existing ones via "Style" > "Save Style" / "Load Style".

5.  **Preview:** The video preview will update to reflect your edits and style changes. Use the slider to navigate through the video.

6.  **Export:**
    *   **Subtitle Files:** Go to "File" > "Export as..." to save subtitles in `.srt`, `.ass`, or `.txt` format.
    *   **Video with Burned-in Subtitles:** Choose "File" > "Export as MP4" to create a new video file with the subtitles rendered directly onto the video.

## 💻 Core Technologies

*   **Python:** The core programming language.
*   **PySide6 (Qt for Python):** For the graphical user interface.
*   **OpenAI Whisper:** For state-of-the-art speech-to-text transcription.
*   **python-vlc & libVLC:** For embedded video playback and preview.
*   **FFmpeg:** For audio extraction and video processing (e.g., burning subtitles).
*   **QAsync:** To integrate asyncio with PySide6's event loop.


## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

When contributing, please try to:

1.  Follow the existing code style.
2.  Write clear and concise commit messages.
3.  Ensure your changes do not break existing functionality.
4.  Update or add tests as appropriate.

## 🗺️ Roadmap (Potential Future Enhancements)

*   [ ] Real-time transcription feedback.
*   [ ] Support for translating subtitles.
*   [ ] More sophisticated timeline editing features.
*   [ ] Integration with cloud-based transcription services as an option.
*   [ ] Customizable keyboard shortcuts.
*   [ ] Project saving/loading to resume work.
*   [ ] Packaging the application as a standalone executable (e.g., using PyInstaller or Nuitka).

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

*   The [OpenAI Whisper](https://github.com/openai/whisper) team for their incredible speech recognition model.
*   The [Qt for Python (PySide6)](https://www.qt.io/qt-for-python) team for the GUI framework.
*   The [VideoLAN (VLC)](https://www.videolan.org/) team for the versatile media player.
*   The [FFmpeg](https://ffmpeg.org/) team for the powerful multimedia toolkit.