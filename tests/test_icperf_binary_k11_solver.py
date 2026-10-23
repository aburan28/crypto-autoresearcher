"""Software controls for the bounded k11 solver runner; no archived target run."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

from tools.icperf_binary_circuit_xcnf_verify import parse
from tools.icperf_binary_k11_solver import (
    blocked_formula,
    check_xcnf_model,
    collect,
    parse_model,
    primary_bits,
    solver_call,
)


def test_primary_block_goes_before_xor_and_excludes_only_that_assignment():
    raw = b"p cnf 2 2\n1 0\nx1 2 0\n"
    blocked = blocked_formula(raw, 2, [1])
    nvars, clauses, xors = parse(blocked)
    assert nvars == 2 and len(clauses) == 2 and len(xors) == 1
    assert clauses[1] == [-1, 2]
    check_xcnf_model([False, True, False], clauses[:1], xors)
    with pytest.raises(ValueError, match="CNF"):
        check_xcnf_model([False, True, False], clauses, xors)
    with pytest.raises(ValueError, match="XOR"):
        check_xcnf_model([False, True, True], clauses[:1], xors)


def test_model_parser_rejects_missing_or_conflicting_literals():
    values = parse_model("s SATISFIABLE\nv 1 -2 0\n", 2)
    assert primary_bits(values, 2) == 1
    for bad in ("s SATISFIABLE\nv 1 0\n",
                "s SATISFIABLE\nv 1 -1 -2 0\n",
                "s SATISFIABLE\nv 1 -2 3 0\n"):
        with pytest.raises(ValueError):
            parse_model(bad, 2)


def test_solver_loop_retains_models_and_blocks_rejected_primary(tmp_path):
    solver = shutil.which("cryptominisat5")
    if solver is None:
        pytest.skip("CryptoMiniSat unavailable")
    raw = b"p cnf 3 2\n1 2 0\nx1 2 3 0\n"
    seen = []

    def certify(assignment):
        seen.append(assignment)
        return {"result": {"certified": len(seen) == 2}}

    result = collect(raw, 2, Path(solver), 10, 512 << 20,
                     2, 7, tmp_path / "run", certify)
    assert result["status"] == "point_relation_certified"
    assert len(result["attempts"]) == len(seen) == 2
    assert seen[0] != seen[1]
    assert result["blocked_primary_count"] == 1
    assert all(row["full_xcnf_model_verified"] for row in result["attempts"])
    assert all((tmp_path / "run" / f"attempt-{i:04d}" / "stdout.txt").exists()
               for i in (1, 2))
    assert all((tmp_path / "run" / f"attempt-{i:04d}" / "attempt.json").exists()
               for i in (1, 2))


def test_model_cap_is_censored_after_checked_rejection(tmp_path):
    solver = shutil.which("cryptominisat5")
    if solver is None:
        pytest.skip("CryptoMiniSat unavailable")
    result = collect(b"p cnf 1 1\n1 0\n", 1, Path(solver), 10, 512 << 20,
                     1, 3, tmp_path / "capped", lambda _: {"result": {"certified": False}})
    assert result["status"] == "model_cap_censored"
    assert result["blocked_primary_count"] == 1
    assert result["attempts"][0]["outcome"] == "rejected_primary"


def test_rss_watchdog_keeps_raw_process_outputs(tmp_path):
    result = solver_call([sys.executable, "-c", "import time; time.sleep(5)"],
                         tmp_path, 3, 1 << 20)
    assert result["rss_watchdog_tripped"]
    assert not result["wall_timeout"]
    assert (tmp_path / "stdout.txt").exists()
    assert (tmp_path / "stderr.txt").exists()
