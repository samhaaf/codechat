from datetime import datetime
import time
from pathlib import Path
from kit.utils.file import File
from kit.utils.singleton import NamedSingletonMeta


class FileDb(metaclass=NamedSingletonMeta):

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.files = {}

    def __getitem__(self, file_path):
        path = self.db_path / file_path
        if path not in self.files:
            self.files[path] = File(path)
        return self.files[path]
