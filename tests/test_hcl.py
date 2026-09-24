import time
from pathlib import Path

import pytest

import terraform.hcl
from terraform.hcl import ParseTimeout, _Parser, _load_str, load, loads

UNPARSEABLE = '''\
terraform {
  required_version = "1.2.3"
  backend "s3" {}
}

variable "secret" {
  sensitive = true
}

broken = "unterminated
'''


def _sleep(seconds: int):
    """Stands in for a parse that hangs, which can only be stopped by killing the worker."""

    time.sleep(seconds)
    return {}, None


def test_loads():
    assert loads('a = 1') == {'a': 1}


def test_loads_rejects_unparseable_hcl():
    with pytest.raises(ValueError):
        loads('a = "unterminated')


def test_load(tmp_path: Path):
    path = tmp_path / 'main.tf'
    path.write_text('terraform {\n  required_version = "1.2.3"\n}\n')

    assert load(path) == {'terraform': [{'required_version': '1.2.3'}]}


def test_load_falls_back_for_unparseable_files(tmp_path: Path):
    path = tmp_path / 'main.tf'
    path.write_text(UNPARSEABLE)

    assert load(path) == {
        'terraform': [{'required_version': '1.2.3'}, {'backend': [{'s3': {}}]}],
        'variable': [{'secret': {'sensitive': True}}],
    }


def test_the_worker_is_reused():
    parser = _Parser()

    assert parser.parse(_load_str, 'a = 1') == {'a': 1}
    worker = parser._pool

    assert parser.parse(_load_str, 'b = 2') == {'b': 2}
    assert parser._pool is worker


def test_a_parse_failure_doesnt_lose_the_worker():
    parser = _Parser()

    assert parser.parse(_load_str, 'a = 1') == {'a': 1}
    worker = parser._pool

    with pytest.raises(Exception):
        parser.parse(_load_str, 'a = "unterminated')

    assert parser._pool is worker


def test_a_hung_parse_is_killed(monkeypatch):
    monkeypatch.setattr(terraform.hcl, 'PARSE_TIMEOUT', 1)
    parser = _Parser()

    with pytest.raises(ParseTimeout):
        parser.parse(_sleep, 60)

    # The parser is still usable with a replacement worker
    assert parser.parse(_load_str, 'a = 1') == {'a': 1}
