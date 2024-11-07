import os
import json
import pathlib
import platform

from .singleton import NamedSingletonMeta

def get_cache_dir(name):
    if platform.system() == 'Windows':
        cache_dir = os.path.join(os.getenv('LOCALAPPDATA'), name, 'Cache')
    elif platform.system() == 'Darwin':  # macOS
        cache_dir = os.path.join(os.getenv('HOME'), 'Library', 'Caches', name)
    else:  # Assuming Linux or other Unix-like systems
        cache_dir = os.path.join(os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache')), name)

    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


class Cache(metaclass=NamedSingletonMeta):

    def __init__(self, name, _parent=None, auto_save=True, save_path=None):
        self.name = name
        self._parent = _parent
        self.save_path = save_path or os.path.join(get_cache_dir(name), f'{name}.cache')
        self._touched = False
        self.auto_save = auto_save
        self._props = {}
        if _parent is None:
            self.load()

    def __setitem__(self, k, v, _supress_save=False):
        if isinstance(v, dict) and not isinstance(v, Cache):
            value = Cache(self.name, _parent=self)
            for _k, _v in v.items():
                value.__setitem__(_k, _v, _supress_save=True)
        else:
            value = v

        self._props[str(k)] = value
        if self.auto_save and not _supress_save:
            self.save()

    def __getitem__(self, k):
        return self._props[str(k)]

    def setdefault(self, k, v):
        if k in self._props:
            return self._props[k]
        self[k] = v
        return v

    def update(self, blob):
        for k, v in blob.items():
            self[k] = v

    def load(self):
        self.touch()
        if self._parent:
            self._parent.load()
        with open(self.save_path) as f:
            raw = json.load(f)
        for k,v in raw.items():
            self.__setitem__(k, v, _supress_save=True)

    def save(self):
        self.touch()
        if self._parent:
            return self._parent.save()
        with open(self.save_path, 'w') as f:
            f.write(self.serialize())

    def serialize(self):
        return json.dumps({
            k: v.serialize() if hasattr(v, 'serialize') else v
            for k,v in self._props.items()
        })

    def touch(self):
        if self._touched:
            return
        dirname = os.path.dirname(self.save_path)
        if not os.path.exists(dirname):
            pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.save_path):
            with open(self.save_path, 'w') as f:
                f.write('{}')
        self._touched = True

    def __repr__(self):
        return self._props.__repr__()
