# Auto Subs: Automatic Subtitle Generator & Editor

[![Continuous Integration](https://github.com/ozzy-420/auto-subs/actions/workflows/ci.yml/badge.svg)](https://github.com/ozzy-420/auto-subs/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-PySide6-cyan.svg)](https://www.qt.io/qt-for-python)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Auto Subs is a free and open-source desktop application engineered to streamline the creation of video subtitles. It combines the state-of-the-art accuracy of OpenAI's Whisper for transcription with a powerful, intuitive editor for refining every detail.

Designed for content creators, translators, and professionals, Auto Subs provides a seamless workflow from automatic transcription to advanced styling and final export, all within a clean, offline-first desktop environment.

## ✨ Key Features

*   **🎙️ Automatic Transcription:** High-accuracy, word-level speech recognition powered by local OpenAI Whisper models.
*   **🎞️ Universal Format Support:** Natively handles MP4, MKV, AVI, and other popular video formats through its integrated FFmpeg engine.
*   **🎬 High-Fidelity Video Preview:** Edit subtitles with a real-time preview rendered by `mpv`, ensuring perfect playback and accurate display of complex `.ass` styles.
*   **✍️ Intuitive Subtitle Editor:**
    *   Effortlessly edit text at the segment or individual word level.
    *   Adjust word and segment timestamps with precision.
    *   Merge multiple segments or split them for better pacing.
*   **🎨 Advanced Styling Suite:**
    *   Full control over font, size, and colors (primary, secondary, outline, background).
    *   Fine-tune alignment, margins, border style, shadow, and rotation.
    *   Apply dynamic highlight styles to emphasize specific words.
    *   Save and load custom style presets to maintain a consistent brand.
*   **🗂️ Project Management:** Save your entire session (video, subtitles, and style settings) into a single `.asproj` file. Load projects to seamlessly resume your work.
*   **💾 Multiple Export Options:**
    *   Export subtitle files in **SRT**, **ASS**, or plain **TXT** formats.
    *   Burn subtitles directly into the video to create a permanent **hardsub** MP4 file.
*   **🖥️ Modern Desktop UI:** A clean and responsive interface built with PySide6 (Qt for Python) for a native look and feel.
*   **🔌 Works Offline:** After an initial model download, all transcription and editing are performed locally on your machine. No internet connection is required.
*   **💰 Free & Open Source:** Licensed under the MIT license. Your tool, no strings attached.

## 📸 Screenshots

*(Screenshots of the application, showcasing the main editor, styling panel, and timeline.)*

*   `[Image of main application window with video, timeline, and editor panel]`
*   `[Image focused on the advanced style customization panel]`
*   `[Image showing the word-level editor for a selected segment]`

## 🛠️ Technology Stack

*   **Core:** Python
*   **GUI:** PySide6 (Qt for Python)
*   **Transcription:** OpenAI Whisper
*   **Video Playback:** `python-mpv` & `libmpv` (for high-quality, embeddable video and `.ass` subtitle rendering)
*   **Media Processing:** FFmpeg (for audio extraction and hardsub rendering)
*   **Concurrency:** `asyncio` & `qasync` (for a non-blocking, responsive UI)
*   **Dependency Management:** Poetry

## 🚀 Getting Started

### Prerequisites

Ensure you have the following software installed and available in your system's PATH:

1.  **Python:** Version 3.9 or newer. ([Download Python](https://www.python.org/downloads/))
2.  **Poetry:** For dependency management. ([Installation Guide](https://python-poetry.org/docs/#installation))
3.  **FFmpeg:** For audio extraction and burning subtitles. ([Download FFmpeg](https://ffmpeg.org/download.html))
4.  **mpv:** For the embedded video player. ([Download mpv](https://mpv.io/installation/))
5.  **Git:** For cloning the repository. ([Download Git](https://git-scm.com/downloads/))

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ozzy-420/auto-subs.git
    cd auto-subs
    ```

2.  **Install dependencies using Poetry:**
    This command will create a virtual environment and install all necessary packages.
    ```bash
    poetry install
    ```
    *Note: If you have an NVIDIA GPU, you may benefit from installing a CUDA-enabled version of PyTorch manually before running `poetry install`. Follow the instructions on the [PyTorch website](https://pytorch.org/get-started/locally/).*

3.  **Run the application:**
    ```bash
    poetry run python main.py
    ```

4.  **Whisper Model Download:**
    The first time you run a transcription, the application will download the specified Whisper model (default: `tiny`). This requires a one-time internet connection. Subsequent uses will be fully offline.

## 📖 How to Use

1.  **Load Video:** Launch the application and go to `File > Import Video...` to load your video file. Alternatively, open a project with `File > Open Project...`.
2.  **Automatic Transcription:** If you loaded a new video, the transcription process can be started from the toolbar.
3.  **Edit & Refine:**
    *   The transcribed segments appear on the timeline at the bottom.
    *   Click a segment on the timeline to select it. This will open the **Word Editor** in the left panel.
    *   In the Word Editor, you can modify text, adjust timestamps, or add/delete words.
4.  **Style Your Subtitles:**
    *   Switch to the **Style Editor** in the left panel.
    *   Customize fonts, colors, alignment, and more. Your changes will be reflected in the video preview in real-time.
    *   Save your configuration via `Style > Save Style As...` for future use.
5.  **Export Your Work:**
    *   **Subtitle File:** Go to `File > Export as...` to save your work as an `.srt`, `.ass`, or `.txt` file.
    *   **Burned-in Video:** Choose `File > Export as MP4...` to create a new video file with the subtitles permanently rendered on the frames.
6.  **Save Your Project:**
    *   Use `File > Save Project` or `File > Save Project As...` to save all your progress into a single `.asproj` file.

## 🤝 Contributing

We welcome contributions of all kinds! Whether you're fixing a bug, proposing a new feature, or improving documentation, your help is appreciated.

Please read our **[CONTRIBUTING.md](CONTRIBUTING.md)** file for detailed instructions on how to set up your development environment, our code style, and the pull request process.

## 🗺️ Roadmap

We have an exciting future planned for Auto Subs! Here are some of the features we're looking to add:

*   [ ] Real-time transcription feedback.
*   [ ] Support for translating subtitles.
*   [ ] More sophisticated timeline editing features (e.g., drag-and-drop, resizing).
*   [ ] Integration with cloud-based transcription services as an option.
*   [ ] Customizable keyboard shortcuts.
*   [ ] Packaging the application as a standalone executable (e.g., using PyInstaller or Nuitka).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

This project stands on the shoulders of giants. Our sincere thanks to the teams behind these incredible open-source tools:

*   [OpenAI Whisper](https://github.com/openai/whisper) for their groundbreaking speech recognition model.
*   [PySide6 (Qt for Python)](https://www.qt.io/qt-for-python) for the robust GUI framework.
*   [mpv](https://mpv.io/) for the powerful and versatile media player.
*   [FFmpeg](https://ffmpeg.org/) for being the swiss-army knife of multimedia processing.
*   [Poetry](https://python-poetry.org/) for modernizing Python dependency management.