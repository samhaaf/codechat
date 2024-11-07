

class SingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class NamedSingletonMeta(type):
    _instances = {}

    def __call__(cls, name, *args, **kwargs):
        # if cls not in _instances
        if name not in cls._instances:
            cls._instances[name] = super().__call__(name, *args, **kwargs)
        return cls._instances[name]
