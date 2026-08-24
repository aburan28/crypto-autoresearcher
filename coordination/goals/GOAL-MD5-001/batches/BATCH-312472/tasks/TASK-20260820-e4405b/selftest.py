#!/usr/bin/env python3
"""Self-test suite for TASK-20260820-e4405b (RANK 2, GOAL-MD5-001 BATCH-312472).

Covers, object by object (expected vs observed, failing check named):
  T1  known-false real crypto: two messages with different MD5 digests,
      claimed digest = the real digest of m1            -> verified:false
  T2  tampered digest on a non-colliding pair           -> verified:false
  T3  m1 == m2                                          -> verified:false
  T4  single-implementation agreement is insufficient
      (MOCK implementations, logic level)               -> verified:false
  T5  mock true path (MOCK implementations, logic level
      ONLY -- tests the decision logic, NOT real MD5
      agreement)                                        -> verified:true
  T9  BCP-2 J5 fix: solver-provided verified_by cleared
      and replaced by wrapper recomputation             -> verified:false
  T10 BCP-2 pin-mechanism distinctness assertion logic
      (real registry distinct; aliased registry not)
  T7  wrapper-measured wall_seconds (new API; real run
      record written under this task directory)
  T8  no-regression: legacy write_run timing formula
      unchanged (real run record written under this
      task directory)

T6 (coverage boundary) is stated in the report, not run: the end-to-end
true path (a genuine colliding pair verified by two real independent
implementations) is UNTESTED within this budget and is named OPEN.

BCP-2 (the concurrent task's artifact) LANDED during this task, after the
card was written. Its field names match the card's schema; its two
additions for this kind (verified_by wrapper-population, the J5 fix; and
the pin-mechanism recording with distinctness assertion, INV-13) are
implemented in harness/runner.py and covered by T1/T9/T10 here. The diff
is flagged in the self-test report, not silently absorbed.

THE QUARANTINED PAYLOAD
  coordination/goals/GOAL-MD5-001/quarantine/MD5-COLLISION-PATH-WANG-2004-199.yaml
IS NEVER READ BY THIS SUITE. Every object here is known-false or mock; no
genuine collision pair is used or generated.

Writes exactly TWO run records, both under this task directory
(selftest-runs/EXP-MD5CERT-e4405b/runs/), and nothing else.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE
for _ in range(10):
    if os.path.isdir(os.path.join(REPO, "harness")):
        break
    REPO = os.path.dirname(REPO)
sys.path.insert(0, REPO)

from harness import runner  # noqa: E402

OUT_ROOT = os.path.join(HERE, "selftest-runs", "EXP-MD5CERT-e4405b")
RESULTS_PATH = os.path.join(HERE, "selftest-results.json")

# --- test messages (known-false: their real MD5 digests DIFFER) -----------
M1 = "hello world".encode().hex()
M2 = "goodbye world".encode().hex()
D1 = hashlib.md5(b"hello world").hexdigest()    # real digest of m1
D2 = hashlib.md5(b"goodbye world").hexdigest()  # real digest of m2
assert D1 != D2, "test messages must have different digests"
# tampered digest: first hex digit of D1 flipped
TAMPERED = ("6" if D1[0] != "6" else "5") + D1[1:]
assert TAMPERED != D1


def cert(m1_hex: str, m2_hex: str, digest_hex: str,
         impls=("IMPL-1", "IMPL-3")) -> dict:
    return {"kind": "md5_collision_pair",
            "statement": {"messages": [m1_hex, m2_hex],
                          "digest": digest_hex,
                          "implementations": list(impls)}}


def precondition_pinned_pair() -> dict:
    """The two pinned imports must be distinct at runtime (the pin's
    independence claim, re-checked here against the live build)."""
    import _md5
    h1 = hashlib.md5(b"precondition")
    h3 = _md5.md5(b"precondition")
    return {
        "impl1_type": type(h1).__name__,
        "impl3_type": type(h3).__name__,
        "distinct_types": type(h1) is not type(h3),
        "empty_string_vector_agree": (
            hashlib.md5(b"").hexdigest() == _md5.md5(b"").hexdigest()
            == "d41d8cd98f00b204e9800998ecf8427e"),
    }


def main() -> int:
    results: dict = {
        "task": "TASK-20260820-e4405b",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "precondition_pinned_pair": precondition_pinned_pair(),
        "objects": [],
    }

    # --- T1..T3: known-false objects through the PRODUCTION dispatch
    # (runner._verify -> pinned pair, no mock) -----------------------------
    t1 = cert(M1, M2, D1)
    c1 = dict(t1)
    v1, verifier1 = runner._verify(c1)
    pin1 = c1.get("pin_mechanism", {})
    vb1 = c1.get("verified_by", [])
    results["objects"].append({
        "id": "T1",
        "name": "known-false real crypto: distinct digests, claimed digest = MD5(m1)",
        "label": "real crypto, production dispatch (pinned pair)",
        "object": t1,
        "expected": {"verified": False,
                     "checks": ["digest_mismatch_impl1_m2",
                                "digest_mismatch_impl3_m2"]},
        "observed": {"verified": v1, "verifier": verifier1,
                     "checks": c1.get("failing_checks", [])},
        "bcp2_pin_mechanism_recorded": {
            "present": bool(pin1),
            "distinct": pin1.get("distinct"),
            "impl1_module_file": pin1.get("IMPL-1", {}).get("module_file"),
            "impl1_runtime_type": pin1.get("IMPL-1", {}).get("runtime_type"),
            "impl3_module_file": pin1.get("IMPL-3", {}).get("module_file"),
            "impl3_runtime_type": pin1.get("IMPL-3", {}).get("runtime_type"),
        },
        "bcp2_verified_by_wrapper_populated": {
            "entries": len(vb1),
            "impl1_digest_m1": (vb1[0].get("computed_digest_m1")
                                if len(vb1) > 0 else None),
            "impl3_digest_m2": (vb1[1].get("computed_digest_m2")
                                if len(vb1) > 1 else None),
        },
    })

    t2 = cert(M1, M2, TAMPERED)
    c2 = dict(t2)
    v2, _ = runner._verify(c2)
    results["objects"].append({
        "id": "T2",
        "name": "tampered digest (first hex digit of MD5(m1) flipped) on a "
                "non-colliding pair",
        "label": "real crypto, production dispatch (pinned pair)",
        "object": t2,
        "expected": {"verified": False,
                     "checks": ["digest_mismatch_impl1_m1",
                                "digest_mismatch_impl1_m2",
                                "digest_mismatch_impl3_m1",
                                "digest_mismatch_impl3_m2"]},
        "observed": {"verified": v2,
                     "checks": c2.get("failing_checks", [])},
    })

    t3 = cert(M1, M1, D1)
    c3 = dict(t3)
    v3, _ = runner._verify(c3)
    results["objects"].append({
        "id": "T3",
        "name": "m1 == m2 (identical messages, correct digest)",
        "label": "real crypto, production dispatch (pinned pair)",
        "object": t3,
        "expected": {"verified": False, "checks": ["m1_equals_m2"]},
        "observed": {"verified": v3, "checks": c3.get("failing_checks", [])},
    })

    # --- T4: single-implementation agreement is insufficient.
    # With the REAL pinned pair this object is unproducible: both are
    # correct MD5 and agree on every input, so no real object exists where
    # one implementation agrees and the other does not. Demonstrated with
    # MOCK implementations through the documented test seam (logic level).
    # IMPL-1 agrees with the claimed digest on BOTH messages; IMPL-3
    # disagrees on m2. 3 of 4 digests match -> must still be rejected.
    class _MockHash:
        """Logic-level stand-in for a hash object: carries a fixed digest."""
        def __init__(self, digest_hex: str):
            self._d = digest_hex

        def hexdigest(self) -> str:
            return self._d

    def mock_impl1_agrees(data: bytes) -> _MockHash:
        return _MockHash(D1)

    def mock_impl3_disagrees_m2(data: bytes) -> _MockHash:
        return _MockHash(D1 if data == b"hello world" else "f" * 32)

    t4 = cert(M1, M2, D1)
    v4, fails4 = runner._verify_md5_collision_pair(
        dict(t4), impls={"IMPL-1": mock_impl1_agrees,
                         "IMPL-3": mock_impl3_disagrees_m2})
    results["objects"].append({
        "id": "T4",
        "name": "single-implementation agreement insufficient: mock IMPL-1 "
                "agrees on both messages, mock IMPL-3 disagrees on m2 "
                "(3 of 4 digests match)",
        "label": "MOCK implementations, logic level (test seam); unproducible "
                 "with the real pinned pair because both are correct MD5",
        "object": t4,
        "expected": {"verified": False,
                     "checks": ["digest_mismatch_impl3_m2",
                                "implementations_disagree"]},
        "observed": {"verified": v4, "checks": fails4},
    })

    # --- T5: mock true path. LOGIC LEVEL ONLY: two distinct mock functions
    # agree on a chosen digest for distinct m1/m2. This tests the decision
    # logic (m1 != m2 AND all four digests equal claimed -> verified), NOT
    # real MD5 agreement.
    CHOSEN = "ab" * 16

    def mock_a(data: bytes) -> _MockHash:
        return _MockHash(CHOSEN)

    def mock_b(data: bytes) -> _MockHash:
        return _MockHash(CHOSEN)

    assert mock_a is not mock_b, "mocks must be distinct functions"
    t5 = cert(M1, M2, CHOSEN)
    v5, fails5 = runner._verify_md5_collision_pair(
        dict(t5), impls={"IMPL-1": mock_a, "IMPL-3": mock_b})
    results["objects"].append({
        "id": "T5",
        "name": "mock true path: two distinct mock implementations agree on "
                "a chosen digest for distinct m1/m2",
        "label": "MOCK implementations, logic level ONLY -- tests the "
                 "decision logic, NOT real MD5 agreement",
        "object": t5,
        "expected": {"verified": True, "checks": []},
        "observed": {"verified": v5, "checks": fails5},
    })

    # --- T9 (BCP-2 J5 fix): a solver-provided verified_by must be CLEARED
    # and replaced exclusively by the wrapper's own recomputation. Same
    # known-false object as T1, plus a fabricated verified_by.
    FAKE_VB = [{"implementation": "IMPL-1",
                "computed_digest_m1": "0" * 32,
                "computed_digest_m2": "0" * 32},
               {"implementation": "IMPL-3",
                "computed_digest_m1": "0" * 32,
                "computed_digest_m2": "0" * 32}]
    t9 = cert(M1, M2, D1)
    t9["verified_by"] = FAKE_VB
    c9 = dict(t9)
    v9, _ = runner._verify(c9)
    vb9 = c9.get("verified_by", [])
    results["objects"].append({
        "id": "T9",
        "name": "BCP-2 J5 fix: solver-provided verified_by cleared and "
                "replaced by wrapper recomputation",
        "label": "real crypto, production dispatch (pinned pair)",
        "object": {**t9, "note": "verified_by field shown as solver-provided "
                                 "input; cleared by the wrapper"},
        "expected": {"verified": False,
                     "checks": ["digest_mismatch_impl1_m2",
                                "digest_mismatch_impl3_m2"],
                     "verified_by_is_wrapper_computed": True},
        "observed": {"verified": v9,
                     "checks": c9.get("failing_checks", []),
                     "verified_by_equals_fake": vb9 == FAKE_VB,
                     "verified_by_impl1_m1": (vb9[0].get("computed_digest_m1")
                                              if len(vb9) > 0 else None),
                     "verified_by_impl3_m2": (vb9[1].get("computed_digest_m2")
                                              if len(vb9) > 1 else None)},
    })

    # --- T10 (BCP-2 pin_mechanism_requirement): the distinctness assertion
    # logic, tested directly on the assertion function (logic level).
    # Real pinned registry -> distinct True; aliased registry (both entries
    # the same function) -> distinct False. The full failure path through
    # the dispatch (verified:false, pinned_pair_not_distinct) is NOT
    # exercised end-to-end: it would require aliasing the real pinned
    # imports, which this task does not do to the production registry.
    real_pin, real_distinct = runner._md5_pin_mechanism(runner._MD5_IMPL_FUNCS)
    aliased = {"IMPL-1": runner._md5_impl1_hash, "IMPL-3": runner._md5_impl1_hash}
    alias_pin, alias_distinct = runner._md5_pin_mechanism(aliased)
    results["objects"].append({
        "id": "T10",
        "name": "BCP-2 pin-mechanism distinctness assertion: real registry "
                "distinct, aliased registry not distinct",
        "label": "logic level: _md5_pin_mechanism called directly; the "
                 "dispatch-level failure path (pinned_pair_not_distinct) is "
                 "not exercised end-to-end (would require aliasing the real "
                 "pinned imports)",
        "object": {"real_registry": "runner._MD5_IMPL_FUNCS",
                   "aliased_registry": "both entries = runner._md5_impl1_hash"},
        "expected": {"real_distinct": True, "aliased_distinct": False},
        "observed": {"real_distinct": real_distinct,
                     "aliased_distinct": alias_distinct,
                     "real_record": real_pin,
                     "aliased_record": alias_pin},
    })

    # --- T7: wrapper-measured wall_seconds (new API). The wrapped call
    # sleeps 0.05 s; a caller that "wanted" to claim a fabricated 0.001 s
    # bracket cannot: run_wrapped has no started/finished parameters, and
    # the record must carry the wrapper-measured value.
    def slow_fn() -> runner.RunResult:
        time.sleep(0.05)
        return runner.RunResult(
            run_suffix="selftest-wrapper", curve_id="N/A", seed=0,
            parameters={"selftest": "wrapper-timing"}, metrics={},
            certificate={"kind": "none"}, stdout="selftest T7\n")

    t7_wall_before = time.monotonic()
    run_id7 = runner.run_wrapped(
        "EXP-MD5CERT-e4405b", "MD5CERT", slow_fn,
        status="completed_valid", command="python3 selftest.py T7",
        out_root=OUT_ROOT)
    t7_wall_after = time.monotonic()
    m7 = _read_manifest(OUT_ROOT, run_id7)
    timing7 = m7["timing"]
    results["wrapper_timing"] = {
        "id": "T7",
        "run_id": run_id7,
        "manifest_path": os.path.relpath(
            os.path.join(OUT_ROOT, "runs", run_id7, "manifest.yaml"), REPO),
        "wrapped_call": "time.sleep(0.05) inside fn",
        "fabricated_caller_bracket": "not expressible: run_wrapped has no "
                                     "started/finished parameters",
        "observed": {
            "wall_seconds": timing7["wall_seconds"],
            "timing_source": timing7.get("timing_source"),
            "started_at": timing7["started_at"],
            "finished_at": timing7["finished_at"],
        },
        "checks": {
            "timing_source_is_wrapper": timing7.get("timing_source") == "wrapper",
            "wall_seconds_ge_sleep": timing7["wall_seconds"] >= 0.049,
            "wall_seconds_exceeds_fabricated_0p001":
                timing7["wall_seconds"] > 0.001,
            "wall_seconds_sane_lt_5": timing7["wall_seconds"] < 5.0,
        },
        "outer_monotonic_bracket_seconds": round(t7_wall_after - t7_wall_before, 6),
    }

    # --- T8: no-regression, legacy path. write_run with explicit
    # started/finished (the old API) must produce the old formula
    # wall_seconds = finished - started and NO timing_source key.
    rr8 = runner.RunResult(
        run_suffix="selftest-legacy", curve_id="N/A", seed=0,
        parameters={"selftest": "legacy-timing"}, metrics={},
        certificate={"kind": "none"}, stdout="selftest T8\n")
    run_id8 = runner.write_run(
        "EXP-MD5CERT-e4405b", "MD5CERT", rr8,
        status="completed_valid", command="python3 selftest.py T8",
        started=1000.0, finished=1000.001, out_root=OUT_ROOT)
    m8 = _read_manifest(OUT_ROOT, run_id8)
    timing8 = m8["timing"]
    results["legacy_timing"] = {
        "id": "T8",
        "run_id": run_id8,
        "manifest_path": os.path.relpath(
            os.path.join(OUT_ROOT, "runs", run_id8, "manifest.yaml"), REPO),
        "caller_supplied": {"started": 1000.0, "finished": 1000.001},
        "observed": {
            "wall_seconds": timing8["wall_seconds"],
            "timing_source_present": "timing_source" in timing8,
            "started_at": timing8["started_at"],
            "finished_at": timing8["finished_at"],
        },
        "checks": {
            "old_formula_finished_minus_started":
                timing8["wall_seconds"] == round(1000.001 - 1000.0, 6),
            "no_timing_source_key": "timing_source" not in timing8,
            "started_at_matches_caller_epoch":
                timing8["started_at"] == runner._iso(1000.0),
            "finished_at_matches_caller_epoch":
                timing8["finished_at"] == runner._iso(1000.001),
        },
    }

    results["run_records_written"] = [
        {"run_id": run_id7, "path": os.path.relpath(
            os.path.join(OUT_ROOT, "runs", run_id7), REPO)},
        {"run_id": run_id8, "path": os.path.relpath(
            os.path.join(OUT_ROOT, "runs", run_id8), REPO)},
    ]

    # --- verdicts ----------------------------------------------------------
    all_pass = True
    for obj in results["objects"]:
        exp, obs = obj["expected"], obj["observed"]
        if obj["id"] == "T1":
            pm = obj["bcp2_pin_mechanism_recorded"]
            vb = obj["bcp2_verified_by_wrapper_populated"]
            obj["pass"] = (obs["verified"] == exp["verified"]
                           and obs["checks"] == exp["checks"]
                           and pm["present"] is True
                           and pm["distinct"] is True
                           and pm["impl1_module_file"]
                           != pm["impl3_module_file"]
                           and pm["impl1_runtime_type"]
                           != pm["impl3_runtime_type"]
                           and vb["entries"] == 2
                           and vb["impl1_digest_m1"] == D1
                           and vb["impl3_digest_m2"] == D2)
        elif obj["id"] == "T9":
            obj["pass"] = (obs["verified"] == exp["verified"]
                           and obs["checks"] == exp["checks"]
                           and obs["verified_by_equals_fake"] is False
                           and obs["verified_by_impl1_m1"] == D1
                           and obs["verified_by_impl3_m2"] == D2)
        elif obj["id"] == "T10":
            obj["pass"] = (obs["real_distinct"] == exp["real_distinct"]
                           and obs["aliased_distinct"]
                           == exp["aliased_distinct"])
        else:
            obj["pass"] = (obs["verified"] == exp["verified"]
                           and obs["checks"] == exp["checks"])
        all_pass = all_pass and obj["pass"]
    for block in ("wrapper_timing", "legacy_timing"):
        results[block]["pass"] = all(results[block]["checks"].values())
        all_pass = all_pass and results[block]["pass"]
    pre = results["precondition_pinned_pair"]
    results["precondition_pinned_pair"]["pass"] = (
        pre["distinct_types"] and pre["empty_string_vector_agree"])
    all_pass = all_pass and results["precondition_pinned_pair"]["pass"]
    results["all_pass"] = all_pass

    with open(RESULTS_PATH, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0 if all_pass else 1


def _read_manifest(out_root: str, run_id: str) -> dict:
    import yaml
    with open(os.path.join(out_root, "runs", run_id, "manifest.yaml"),
              encoding="utf-8") as fh:
        return yaml.safe_load(fh)["run"]


if __name__ == "__main__":
    sys.exit(main())
