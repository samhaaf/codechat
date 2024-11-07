


class Settable:
    def __init__(self, params=None):
        if params is None:
            params = {}
        if not isinstance(params, dict):
            params = {'value': params}
        super().__setattr__('params', params)

    def __getitem__(self, key):
        return self.params.get(key)

    def __setitem__(self, key, value):
        self.params[key] = value

    def __getattr__(self, name):
        return self.params.get(name)

    def __setattr__(self, key, value):
        if key == 'params' or hasattr(self, key):
            super().__setattr__(key, value)
        else:
            self[key] = value
