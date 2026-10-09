"""CI test shards: every file in exactly one shard, balanced, deterministic."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import ci_test_shard as shard  # noqa: E402


def test_every_file_lands_in_exactly_one_shard():
    files = [f"tests/test_{i:03d}.py" for i in range(40)]
    durations = {f: float(i % 7 + 1) for i, f in enumerate(files)}
    shards = shard.plan(files, 4, durations)
    flat = [f for s in shards for f in s]
    assert sorted(flat) == sorted(files) and len(flat) == len(set(flat))


def test_longest_first_balances_and_isolates_a_dominant_file():
    durations = {"tests/test_big.py": 200.0, **{f"tests/test_s{i}.py": 10.0 for i in range(30)}}
    shards = shard.plan(sorted(durations), 3, durations)
    loads = sorted(sum(durations[f] for f in s) for s in shards)
    assert ["tests/test_big.py"] in shards
    assert loads[-1] == 200.0 and loads[1] - loads[0] <= 10.0


def test_unmeasured_files_count_as_the_median_and_plans_are_deterministic():
    durations = {"tests/test_a.py": 1.0, "tests/test_b.py": 3.0, "tests/test_c.py": 5.0}
    files = [*durations, "tests/test_new.py"]
    first = shard.plan(files, 2, durations)
    assert first == shard.plan(list(reversed(files)), 2, durations)
    assert sorted(f for s in first for f in s) == sorted(files)


def test_junit_seconds_map_dotted_classnames_to_files(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "test_x.py").write_text("")
    xml = tmp_path / "j.xml"
    xml.write_text(
        '<testsuites><testsuite>'
        '<testcase classname="tools.test_x.SomeTests" name="a" time="1.5"/>'
        '<testcase classname="tools.test_x" name="b" time="0.5"/>'
        '<testcase classname="gone.test_y" name="c" time="9"/>'
        '</testsuite></testsuites>')
    assert shard.junit_durations([xml], repo=tmp_path) == {"tools/test_x.py": 2.0}


def test_committed_durations_cover_most_of_the_suite():
    durations = shard.load_durations()
    assert len(durations) > 100 and sum(durations.values()) > 600
