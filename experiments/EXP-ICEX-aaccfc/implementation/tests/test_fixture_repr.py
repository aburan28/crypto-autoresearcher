"""v4c H-1: a failing test taking smoke_primary prints no frozen value under pytest's
default (long) traceback.

PYTEST_DONT_REWRITE (v4b A-3): this module evaluates frozen fixtures, so assertion
rewriting is disabled and a failing assert reports no compared values."""

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CONFTEST = Path(__file__).resolve().parent / "conftest.py"
UNITS_NUMBER_RE = re.compile(r"complete_units['\"]?\s*[:=]\s*-?\d")

PROBE_CONFTEST = f'''
import importlib.util
import pytest

_spec = importlib.util.spec_from_file_location("icex_impl_conftest", {str(CONFTEST)!r})
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
smoke_primary = _m.smoke_primary


@pytest.fixture(scope="session")
def smoke_plain(smoke_primary):
    return {{"complete_units": smoke_primary["complete_units"]}}
'''

PROBE_TESTS = '''"""PYTEST_DONT_REWRITE"""


def test_a_hidden(smoke_primary):
    assert smoke_primary["complete_units"] == -1, "withheld"


def test_b_plain(smoke_plain):
    assert smoke_plain["complete_units"] == -1, "withheld"
'''


def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def _unit_hashes(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, int) and not isinstance(v, bool) and "units" in str(k) and abs(v) >= 1000:
                out.add(_sha(str(v)))
            else:
                _unit_hashes(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _unit_hashes(v, out)
    return out


def _leaks(text, hashes):
    return any(_sha(tok) in hashes for tok in re.findall(r"\d+", text))


def test_failing_frozen_fixture_test_prints_no_values(smoke_primary, tmp_root):
    assert "values hidden" in repr(smoke_primary) and "values hidden" in str(smoke_primary)
    hashes = _unit_hashes(dict(smoke_primary), set())
    assert _sha(str(smoke_primary["complete_units"])) in hashes, "complete_units not among hashed values"
    d = tmp_root / "h1_probe"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir()
    try:
        (d / "pytest.ini").write_text("[pytest]\n")  # pytest defaults: --tb=auto, no addopts
        (d / "conftest.py").write_text(PROBE_CONFTEST)
        (d / "test_probe.py").write_text(PROBE_TESTS)
        env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        r = subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", str(d)],
                           capture_output=True, text=True, timeout=900, cwd=str(d), env=env)
        out = r.stdout + r.stderr
        assert r.returncode == 1 and "2 failed" in out, "probe did not fail as designed (output withheld)"
        parts = re.split(r"_+ test_b_plain _+", out)
        assert len(parts) == 2, "probe output not split into hidden/plain sections (output withheld)"
        hidden_part, plain_part = parts
        assert "values hidden" in hidden_part
        assert _leaks(plain_part, hashes) and UNITS_NUMBER_RE.search(plain_part), "probe insensitive"
        assert not _leaks(hidden_part, hashes), "a frozen units value appears in the hidden-fixture traceback"
        assert not UNITS_NUMBER_RE.search(hidden_part), "complete_units followed by a number appears"
    finally:
        shutil.rmtree(d, ignore_errors=True)
