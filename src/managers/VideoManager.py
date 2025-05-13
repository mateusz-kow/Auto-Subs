class VideoManager:
    def __init__(self, video_path: str = None):
        self.video_path: str = video_path
        self.video_changed_listeners: list = []

    def set_video_path(self, path: str):
        self.video_path = path

        for listener in self.video_changed_listeners:
            listener(path)

    def add_video_listener(self, listener):
        self.video_changed_listeners.append(listener)