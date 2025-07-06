import os

# Add the directory containing libmpv-2.dll to the PATH
dll_directory = (
    r"C:\Users\mw-ko\PycharmProjects\Auto-Subs\mpv-dev-x86_64-20250527-git-1d1535f"  # Replace with the actual directory
)
os.environ["PATH"] = dll_directory + os.pathsep + os.environ["PATH"]

from mpv import MPV


def test_mpv():
    """Test the MPV library by initializing an instance and playing a sample video."""
    try:
        # Initialize MPV instance
        player = MPV(loglevel="debug")
        print("MPV instance initialized successfully.")

        # Load a sample video file (update the path to a valid video file)
        video_path = r"C:\path\to\sample_video.mp4"  # Replace with the actual path to a video file
        player.loadfile(video_path)
        print(f"Loaded video: {video_path}")

        # Start playback
        player.play(r"input\video1.mp4")
        print("Playback started. Press Ctrl+C to stop.")

        # Keep the player running
        while True:
            pass

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    test_mpv()
