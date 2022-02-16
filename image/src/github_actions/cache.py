import os
from pathlib import Path


class ActionsCache:

    def __init__(self, cache_dir: Path):
        self._cache_dir = cache_dir

    def get(self, item, default=None):
        try:
            return self.__getitem__(item)
        except IndexError:
            if default is not None:
                self.__setitem__(item, default)
            return default

    def get_default_func(self, item, default):
        try:
            return self.__getitem__(item)
        except IndexError:
            v = default()
            if v is not None:
                self.__setitem__(item, v)
            return v

    def __setitem__(self, key, value):
        if value is None:
            return

        path = os.path.join(self._cache_dir, key)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(os.path.join(self._cache_dir, key), 'w') as f:
            f.write(value)

    def __getitem__(self, item):
        if os.path.isfile(os.path.join(self._cache_dir, item)):
            with open(os.path.join(self._cache_dir, item)) as f:
                return f.read()

        raise IndexError()

    def __contains__(self, item):
        return os.path.isfile(os.path.join(self._cache_dir, item))
