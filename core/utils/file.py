from datetime import datetime
import time
from pathlib import Path
from .cache import Cache


# def interaction(func):
#     def wrapper(self, *args, **kwargs):
#         result = func(self, *args, **kwargs)
#         self._last_interaction = datetime.now()
#         return result
#     return wrapper




class File(metaclass=NamedSingletonMeta):
    def __init__(self, path: Path):
        self.path = path
        # self._last_interaction = datetime.now()
        self._cache = Cache['files'].setdefault(path, {})

    # @interaction
    def __str__(self):
        return self.path.read_text()

    # @interaction
    def __getitem__(self, rows):
        lines = self.path.read_text().split('\n')
        return '\n'.join(lines[rows])

    # @interaction
    def write(self, content, lines=None):
        if lines is None:
            self.path.write_text(content)
        else:
            file_lines = self.path.read_text().split('\n')
            if isinstance(lines, tuple) and len(lines) == 1:
                lines = slice(lines[0], None, None)
            file_lines[lines] = content.split('\n')
            self.path.write_text('\n'.join(file_lines))

    # @interaction
    def insert(self, content, line):
        file_lines = self.path.read_text().split('\n')
        insert_lines = content.split('\n')
        file_lines = file_lines[:line] + insert_lines + file_lines[line:]
        self.path.write_text('\n'.join(file_lines))

    # @interaction
    def append(self, content):
        with self.path.open('a') as f:
            f.write(content)

    # @interaction
    def prepend(self, content):
        self.insert(content, 0)

    # @interaction
    def __setitem__(self, key, value):
        self.write(value, lines=key)

    @property
    def last_modified(self):
        last_modification_time = datetime.fromtimestamp(self.path.stat().st_mtime)
