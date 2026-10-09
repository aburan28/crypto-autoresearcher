"""fast_yaml.safe_load: the same values and the same errors as yaml.safe_load."""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from orchestration import fast_yaml

REPO = Path(__file__).resolve().parents[1]
GOOD = "a: 1\nb: [x, 2.5, null, 2026-10-09]\nc: {d: yes}\n"
BAD = "a: 1\nb: [unclosed\nc: 2\n"
needs_libyaml = pytest.mark.skipif(fast_yaml.CSafeLoader is None, reason="no libyaml")


def _error(load, source) -> str:
    with pytest.raises(yaml.YAMLError) as caught:
        load(source)
    return str(caught.value)


def test_values_match_for_text_bytes_and_streams():
    expected = yaml.safe_load(GOOD)
    assert fast_yaml.safe_load(GOOD) == expected
    assert fast_yaml.safe_load(GOOD.encode()) == expected
    assert fast_yaml.safe_load(io.StringIO(GOOD)) == expected
    assert fast_yaml.safe_load(io.BytesIO(GOOD.encode())) == expected
    assert fast_yaml.safe_load("") is None


@needs_libyaml
def test_errors_are_the_pure_loaders_word_for_word(tmp_path):
    assert _error(fast_yaml.safe_load, BAD) == _error(yaml.safe_load, BAD)
    path = tmp_path / "bad.yaml"
    path.write_text(BAD)
    with path.open() as fast, path.open() as pure:
        message = _error(fast_yaml.safe_load, fast)
        assert message == _error(yaml.safe_load, pure)
    assert str(path) in message  # the mark names the file, not "<unicode string>"


@needs_libyaml
def test_unseekable_and_midway_streams_replay_what_was_read():
    class Pipe(io.StringIO):
        def seekable(self):
            return False

        def seek(self, *args):
            raise io.UnsupportedOperation("pipe")

    pipe = Pipe(BAD)
    pipe.name = "<stdin>"
    reference = io.StringIO(BAD)
    reference.name = "<stdin>"
    assert _error(fast_yaml.safe_load, pipe) == _error(yaml.safe_load, reference)

    def advanced(text):
        stream = io.StringIO("header: [\n" + text)
        stream.readline()
        return stream

    assert fast_yaml.safe_load(advanced(GOOD)) == yaml.safe_load(GOOD)
    assert _error(fast_yaml.safe_load, advanced(BAD)) == _error(yaml.safe_load, advanced(BAD))


def test_without_libyaml_it_is_safe_load(monkeypatch):
    monkeypatch.setattr(fast_yaml, "CSafeLoader", None)
    assert fast_yaml.safe_load(GOOD) == yaml.safe_load(GOOD)
    assert _error(fast_yaml.safe_load, BAD) == _error(yaml.safe_load, BAD)


def test_tools_copy_is_a_re_export():
    """`python3 tools/x.py` finds the one implementation through tools/fast_yaml.py."""
    probe = ("import sys; sys.path.insert(0, 'tools'); import fast_yaml, orchestration.fast_yaml as o; "
             "assert fast_yaml.safe_load is o.safe_load; print('ok')")
    out = subprocess.run([sys.executable, "-c", probe], cwd=REPO, capture_output=True, text=True)
    assert out.stdout.strip() == "ok", out.stderr
