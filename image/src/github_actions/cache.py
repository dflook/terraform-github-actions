import os
from pathlib import Path

from github_actions.debug import debug


class ActionsCache:

    def __init__(self, cache_dir: Path, label: str=None):
        self._cache_dir = cache_dir
        self._label = label or self._cache_dir

    def __setitem__(self, key, value):
        if value is None:
            debug(f'Cache value for {key} should not be set to {value}')
            return

        path = os.path.join(self._cache_dir, key)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(os.path.join(self._cache_dir, key), 'w') as f:
            f.write(value)
            debug(f'Wrote {key} to {self._label}')

    def __getitem__(self, key):
        if os.path.isfile(os.path.join(self._cache_dir, key)):
            with open(os.path.join(self._cache_dir, key)) as f:
                debug(f'Read {key} from {self._label}')
                return f.read()

        raise IndexError(key)

    def __contains__(self, key):
        return os.path.isfile(os.path.join(self._cache_dir, key))
