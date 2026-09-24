"""
Wraps python-hcl
"""

from __future__ import annotations

import atexit
import multiprocessing
import multiprocessing.context
import multiprocessing.pool
from pathlib import Path
from typing import Callable, Optional, Tuple, TypeVar

import hcl2  # type: ignore

from github_actions.debug import debug
import terraform.fallback_parser

T = TypeVar('T')

#: A parsed document, or the reason it couldn't be parsed. Exactly one is set.
ParseResult = Tuple[Optional[dict], Optional[str]]

#: How long a single parse is allowed to take before the parser is killed
PARSE_TIMEOUT = 10


class ParseError(Exception):
    """The parser rejected the input."""


class ParseTimeout(Exception):
    """The parser took too long and was killed."""


def _load_path(path: str) -> ParseResult:
    try:
        with open(path) as f:
            return hcl2.load(f), None
    except Exception as e:
        return None, str(e)


def _load_str(hcl: str) -> ParseResult:
    try:
        return hcl2.loads(hcl), None
    except Exception as e:
        return None, str(e)


class _Parser:
    """
    Runs the hcl parser in a worker process.

    The parser can hang on some inputs, such as unterminated strings. An in-process timeout
    can't interrupt that, so the parse has to happen somewhere that can be killed instead.

    One worker is reused for every parse and is only replaced when it has to be killed, so a
    module with many files pays for one worker rather than one per file. Parse failures are
    returned rather than raised, so that they don't have to survive being pickled - lark's
    exceptions don't.
    """

    def __init__(self) -> None:
        self._pool: Optional[multiprocessing.pool.Pool] = None

        # Leaving the worker to be collected during interpreter shutdown makes a mess of stderr
        atexit.register(self._discard_worker)

    def _worker(self) -> multiprocessing.pool.Pool:
        if self._pool is None:
            context: multiprocessing.context.BaseContext

            try:
                context = multiprocessing.get_context('fork')
            except ValueError:
                # Without fork the worker has to start a fresh interpreter.
                # It is still only started once.
                context = multiprocessing.get_context()

            self._pool = context.Pool(1)

        return self._pool

    def _discard_worker(self) -> None:
        if self._pool is not None:
            self._pool.terminate()
            self._pool = None

    def parse(self, parse_func: Callable[[T], ParseResult], arg: T) -> dict:
        """
        Call parse_func(arg) in the worker process.

        :raises ParseError: If the input could not be parsed.
        :raises ParseTimeout: If the parse took longer than PARSE_TIMEOUT seconds.
        """

        try:
            document, error = self._worker().apply_async(parse_func, (arg,)).get(PARSE_TIMEOUT)
        except multiprocessing.TimeoutError:
            debug('TimeoutExpired')
            # The worker is still stuck in the parse, so it is no use to anyone else
            self._discard_worker()
            raise ParseTimeout
        except Exception:
            # Something happened to the worker itself, so don't keep using it
            self._discard_worker()
            raise

        if document is None:
            raise ParseError(error)

        return document


_parser = _Parser()


def load(path: Path) -> dict:
    try:
        return _parser.parse(_load_path, str(path))
    except ParseTimeout:
        debug(f'Unable to load {path}')
        raise ValueError(f'Unable to load {path}')
    except Exception as e:
        debug(f'Failed to load {path}')
        debug(str(e))
        return terraform.fallback_parser.parse(Path(path))


def loads(hcl: str) -> dict:
    try:
        return _parser.parse(_load_str, hcl)
    except ParseTimeout:
        pass
    except Exception as e:
        debug('Failed to parse hcl')
        debug(str(e))

    debug('Unable to load hcl')
    raise ValueError('Unable to load hcl')
