from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RobotsFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, config):
        super(RobotsFileSystemEventHandler, self).__init__()
        self._config = config

    def on_any_event(self, event):
        print(event)

class ProjectWatcher:

    def __init__(self, config):
        self._config = config
        self._project_dir = Path(self._config.get('rcc', 'project_dir')).absolute()
        self._wrap_dir = Path(self._config.get('rcc', 'wrap_dir')).absolute()

    def watch(self):
        event_handler = RobotsFileSystemEventHandler(self._config)

        observer = Observer()
        observer.schedule(event_handler, self._project_dir, recursive=True)
        
        observer.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            observer.stop()
            observer.join()