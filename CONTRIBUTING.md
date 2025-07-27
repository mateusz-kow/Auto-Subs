# Contributing to Auto Subs

First off, thank you for considering contributing to Auto Subs! We're excited to see what you can bring to the project. Any contribution, whether it's reporting a bug, suggesting a new feature, or writing code, is greatly appreciated.

This document provides guidelines to help make the contribution process clear and effective for everyone involved.

## How Can I Contribute?

*   [Reporting Bugs](#reporting-bugs)
*   [Suggesting Enhancements](#suggesting-enhancements)
*   [Submitting Pull Requests](#submitting-pull-requests)

## Code of Conduct

We expect all contributors to adhere to a high standard of professional and respectful conduct. Please be kind and considerate in your interactions. Harassment or exclusionary behavior will not be tolerated. This project is released with a Contributor Code of Conduct. By participating, you agree to abide by its terms. Please see our [LICENSE](LICENSE) file for more details.

## Getting Started: Setting Up Your Development Environment

To get your local development environment set up and ready to go, please follow these steps.

### Prerequisites

Ensure you have the following software installed on your system:

1.  **Git:** For version control. ([Download Git](https://git-scm.com/downloads/))
2.  **Python:** Version 3.9 or newer. ([Download Python](https://www.python.org/downloads/))
3.  **Poetry:** For managing dependencies and the project environment. ([Installation Guide](https://python-poetry.org/docs/#installation))
4.  **FFmpeg:** Required for audio/video processing. ([Download FFmpeg](https://ffmpeg.org/download.html))
    *   Make sure `ffmpeg` and `ffprobe` are available in your system's PATH.
5.  **mpv:** Required for the embedded video preview. ([Download mpv](https://mpv.io/installation/))
    *   The `python-mpv` library needs access to the `mpv` executable.

### Installation

1.  **Fork the repository:**
    Start by forking the `ozzy-420/auto-subs` repository on GitHub.

2.  **Clone your fork:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/auto-subs.git
    cd auto-subs
    ```

3.  **Install dependencies with Poetry:**
    This command will create a virtual environment inside the project directory (`.venv`) and install all required packages, including development tools.
    ```bash
    poetry install
    ```

4.  **Run the application:**
    To ensure everything is working, activate the virtual environment and run the app.
    ```bash
    poetry run python main.py
    ```

## Contribution Workflow

### Reporting Bugs

If you find a bug, please create an issue on our GitHub repository. A great bug report includes:
*   A clear and descriptive title.
*   Your operating system and version.
*   The version of Auto Subs you are using.
*   Clear, step-by-step instructions to reproduce the bug.
*   What you expected to happen vs. what actually happened.
*   Relevant logs from the console or the `app.log` file found in the application's data directory.

### Suggesting Enhancements

If you have an idea for a new feature or an improvement, please open an issue first. This allows us to discuss the proposal and ensure it aligns with the project's goals before you invest time in development.

### Submitting Pull Requests

1.  Create a new branch for your feature or bugfix from the `dev` branch. Use a descriptive name.
    ```bash
    git checkout -b my-awesome-branch dev
    ```
2.  Make your changes and commit them with a clear, descriptive message (see [Commit Message Conventions](#commit-message-conventions)).
3.  Push your branch to your forked repository.
    ```bash
    git push origin my-awesome-feature
    ```
4.  Open a pull request from your branch to the `dev` branch of the original `auto-subs` repository.
5.  In your pull request description, explain the changes you've made and link to any relevant issues.

## Code Style and Quality Standards

To maintain code quality and consistency, we use a few automated tools. Your pull request must pass all these checks.

*   **Formatting:** We use `black` for strict code formatting.
*   **Linting:** We use `ruff` to check for a wide range of potential errors and style issues.
*   **Type Checking:** We use `mypy` for static type analysis.

You can run these checks locally before committing your changes:

```bash
# Check formatting with Black
poetry run black . --check

# Lint with Ruff
poetry run ruff check .

# Run static type checking with Mypy
poetry run mypy .
```

To automatically fix formatting and some linting issues, you can run:
```bash
poetry run black .
poetry run ruff check . --fix
```

## Commit Message Conventions

We don't follow any commit message format. However, we encourage you to write clear and descriptive commit messages that explain the "what" and "why" of your changes. This helps maintain a readable project history.

Thank you for contributing