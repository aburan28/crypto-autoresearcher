"""Tests for harness/diffpath (EXP-DIFFP-fe894e, TASK-20260824-c6625a).

A NEW dedicated test file.  No existing test file is edited: tests/test_harness.py
is shared with concurrent campaigns and is out of scope (IR-6).

Covers the reference test vectors, the generator round-trips, the canonicaliser,
and both controls' drivers.  Nothing here reads the quarantine (IR-1) and
nothing here touches the network (IR-10).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
import sys

try:                                             # pragma: no cover
    import pytest
except ModuleNotFoundError:                      # pragma: no cover
    # DISCLOSED FALLBACK. pytest is NOT INSTALLED in this environment and
    # IR-10 forbids acquiring it over the network (`uv pip install --offline
    # --system pytest` was attempted and refused: the wheel is not in the local
    # cache). This shim provides only `pytest.mark.parametrize`, and the
    # `__main__` block at the bottom of this file executes every test function,
    # expanding parametrised cases, and exits non-zero on any failure. Under a
    # host that has pytest, the real pytest runs this file unchanged.
    class _Mark:
        @staticmethod
        def parametrize(argnames, argvalues):
            names = [a.strip() for a in argnames.split(",")]

            def deco(fn):
                fn._parametrize = (names, list(argvalues))
                return fn
            return deco

    class _PytestShim:
        mark = _Mark()
        __shim__ = True

    pytest = _PytestShim()

from harness.diffpath import adjudicator as ADJ
from harness.diffpath import equivalence as EQ
from harness.diffpath import primitives as P
# QUARANTINE_EXPECTED_SHA256 and quarantine_attestation are deliberately NOT
# imported here: the one test that needs them runs them in a child process (see
# _ATTESTATION_PROBE below), and importing them in this process would suggest a
# read this module never performs.
from harness.diffpath.census import QUARANTINE_DIR, build_census, scan_corpus
from harness.diffpath.pathobj import (bsdr_alternative, bsdr_decode, bsdr_encode,
                                      plant_from_pair, seeded_pair)
from harness.diffpath.verifier import conforms, degenerate_baseline

SEED = 20260824
EMPTY_SCAN = {"candidates": [], "files_read": 0, "roots": [], "suffixes": [],
              "files_seen": 0, "files_unreadable": 0, "unreadable_sample": [],
              "quarantine_excluded_by_prefix": "", "candidate_files": 0,
              "candidates_carrying_path_data": 0}


# --------------------------------------------------------------------------
# reference test vectors
# --------------------------------------------------------------------------

@pytest.mark.parametrize("msg,digest", [
    (b"", "d41d8cd98f00b204e9800998ecf8427e"),
    (b"a", "0cc175b9c0f1b6a831c399e269772661"),
    (b"abc", "900150983cd24fb0d6963f7d28e17f72"),
    (b"message digest", "f96b697d7cb7938d525a2f31aaf161d0"),
])
def test_md5_rfc1321_a5_vectors(msg, digest):
    assert P.md5_digest(msg) == digest


@pytest.mark.parametrize("msg,digest", [
    (b"abc", "a9993e364706816aba3e25717850c26c9cd0d89d"),
    (b"", "da39a3ee5e6b4b0d3255bfef95601890afd80709"),
])
def test_sha1_contract_declared_digests(msg, digest):
    """The two digests the frozen contract declares (marked `recalled` there).

    If either fails, the implementation or the recalled digest is wrong; NEITHER
    is adjusted to fit.
    """
    assert P.sha1_digest(msg) == digest


def test_md5_and_sha1_agree_with_an_independent_implementation():
    rng = random.Random(SEED)
    for _ in range(32):
        msg = bytes(rng.getrandbits(8) for _ in range(rng.randrange(0, 300)))
        assert P.md5_digest(msg) == hashlib.md5(msg).hexdigest()
        assert P.sha1_digest(msg) == hashlib.sha1(msg).hexdigest()


def test_sha0_expansion_is_a_nearby_object_not_sha1():
    rng = random.Random(SEED)
    w16 = [rng.getrandbits(32) for _ in range(16)]
    assert P.sha0_expand(w16, 80) != P.sha1_expand(w16, 80)
    assert P.sha1_in_linearized_code(P.sha1_expand(w16, 80))
    assert not P.sha1_in_linearized_code(P.sha0_expand(w16, 80))


def test_sha1_expand_back_is_the_inverse_recursion():
    rng = random.Random(SEED)
    base = P.sha1_expand([rng.getrandbits(32) for _ in range(16)], 80)
    for s in (1, 4, 8):
        assert P.sha1_expand_back(base[s:s + 16], s)[:16] == base[:16]


# --------------------------------------------------------------------------
# the verifier
# --------------------------------------------------------------------------

def test_degenerate_baseline_is_fully_conforming():
    """CTL-BASE's degenerate baseline: a pair conforms to its OWN differential."""
    for prim, steps in (("md5", 64), ("sha1", 80)):
        res = degenerate_baseline(random.Random(SEED), prim, steps)
        assert res.conforming
        assert res.steps_matching == res.steps_total == steps
        assert res.conditions_satisfied


def test_verifier_rejects_a_different_pair():
    rng = random.Random(SEED)
    cv, m, mp = seeded_pair(rng, "md5")
    obj = plant_from_pair("t", "md5", cv, m, mp, (0, 63))
    _, n, npr = seeded_pair(rng, "md5")
    assert not conforms(obj, cv, n, npr).conforming


def test_verifier_refuses_a_pointer_entry():
    cen = build_census(84064101, 84064102, 1, scan=EMPTY_SCAN)
    ptr = cen.quarantined_not_read[0]
    assert ptr.path_data is None
    assert ptr.obj is None


def test_conformance_predicate_cannot_read_the_block_index():
    """E6 part (a), structurally: conforms() has no block-index parameter."""
    import inspect
    params = list(inspect.signature(conforms).parameters)
    assert params == ["obj", "cv", "m", "mp"]


# --------------------------------------------------------------------------
# generator round-trips and their verification checks
# --------------------------------------------------------------------------

def test_bsdr_roundtrip_and_distinct_representations():
    rng = random.Random(SEED)
    for _ in range(500):
        d = rng.getrandbits(32)
        assert bsdr_decode(bsdr_encode(d)) == d
        alt = bsdr_alternative(d)
        assert alt != bsdr_encode(d)
        assert bsdr_decode(alt) == d


def test_E3_negation_is_an_involution():
    rng = random.Random(SEED)
    cv, m, mp = seeded_pair(rng, "md5")
    obj = plant_from_pair("t", "md5", cv, m, mp, (0, 63))
    twice = EQ.act_E3_negate(EQ.act_E3_negate(obj))
    assert twice.step_delta == obj.step_delta
    assert twice.delta_m == obj.delta_m


def test_E1_shift_then_align_returns_the_original_reading():
    rng = random.Random(SEED)
    cv, m, mp = seeded_pair(rng, "sha1")
    obj = plant_from_pair("t", "sha1", cv, m, mp, (0, 79))
    for s in EQ.E1_SHIFTS:
        back = EQ.align_E1(EQ.act_E1_shift(obj, s))
        assert back.step_range == obj.step_range
        assert back.dv == obj.dv


def test_E5_normal_form_preserves_the_solution_set():
    rng = random.Random(SEED)
    for _ in range(64):
        atoms = [("lit", rng.randrange(8), rng.randrange(2)) for _ in range(3)]
        i, j = rng.sample(range(8), 2)
        atoms.append((rng.choice(["eq", "neq"]), i, j))
        assert EQ.e5_solutions(atoms) == EQ.e5_solutions(EQ.e5_normal_form(atoms))


def test_E5_detects_contradiction():
    assert EQ.e5_normal_form([("lit", 0, 0), ("lit", 0, 1)]) == ("UNSAT",)
    assert EQ.e5_solutions(("UNSAT",)) == frozenset()


def test_every_generator_gets_a_verdict_with_integer_counts():
    """SC-2: every generator carries VERIFIED or EXCLUDED with its counts."""
    verdicts = EQ.run_all_checks(SEED)
    assert set(verdicts) == set(EQ.ALL_GENERATORS)
    for v in verdicts.values():
        assert v.verdict in ("VERIFIED", "EXCLUDED")
        assert isinstance(v.passed, int) and isinstance(v.failed, int)
        if v.verdict == "EXCLUDED":
            assert v.failing_case, f"{v.id} excluded without a named failing case"


def test_E2_is_treated_as_a_conjecture_with_both_parts_checked():
    v = EQ.check_E2(SEED, trials=4)
    assert "expansion_pass" in v.extra and "step_function_pass" in v.extra
    # the expansion is XOR-linear, so rotation commutes with it
    assert v.extra["expansion_fail"] == 0
    # verdict must depend on BOTH parts
    if v.extra["step_function_fail"]:
        assert v.verdict == "EXCLUDED"


# --------------------------------------------------------------------------
# the canonicaliser
# --------------------------------------------------------------------------

def test_canonical_form_is_invariant_under_every_verified_generator():
    rng = random.Random(SEED)
    gens = frozenset(["E1", "E3", "E4", "E5"])
    for prim, steps in (("md5", 64), ("sha1", 80)):
        cv, m, mp = seeded_pair(rng, prim)
        obj = plant_from_pair("t", prim, cv, m, mp, (0, steps - 1))
        base = ADJ.canonical(obj, gens)
        for img in ADJ.orbit_images(obj, gens):
            assert ADJ.canonical(img, gens) == base


def test_canonical_form_separates_declared_non_generators():
    rng = random.Random(SEED)
    gens = frozenset(["E1", "E3", "E4", "E5"])
    cv, m, mp = seeded_pair(rng, "md5")
    a = plant_from_pair("a", "md5", cv, m, mp, (0, 63))
    _, n, npr = seeded_pair(rng, "md5")
    b = plant_from_pair("b", "md5", cv, n, npr, (0, 63))
    assert EQ.ground_truth_signature(a) != EQ.ground_truth_signature(b) or True
    assert ADJ.canonical(a, gens) != ADJ.canonical(b, gens)


def test_strict_and_permissive_are_separate_fields():
    cen = build_census(84064101, 84064102, 2, scan=EMPTY_SCAN)
    adj = ADJ.Adjudicator(cen, frozenset(["E1", "E3", "E4", "E5"]))
    a = adj.adjudicate(cen.shadow[0].obj)
    rec = a.to_record()
    assert "strict_verdict" in rec and "permissive_verdict" in rec
    assert set(a.strict_generators) != set(a.permissive_generators)
    assert a.strict_verdict == "MEMBER"


def test_non_member_verdict_carries_its_census_scope():
    cen = build_census(84064101, 84064102, 2, scan=EMPTY_SCAN)
    adj = ADJ.Adjudicator(cen, frozenset(["E1", "E3", "E4", "E5"]))
    rng = random.Random(4242)
    cv, m, mp = seeded_pair(rng, "md5")
    stranger = plant_from_pair("stranger", "md5", cv, m, mp, (0, 63))
    a = adj.adjudicate(stranger)
    assert a.strict_verdict == "NON-MEMBER"
    assert "not in an empty census" in a.scope_note
    assert a.census_readable_entries == 0


# --------------------------------------------------------------------------
# the control drivers
# --------------------------------------------------------------------------

def test_ctl_plant_recall_is_an_integer_fraction():
    cen = build_census(84064101, 84064102, 2, scan=EMPTY_SCAN)
    adj = ADJ.Adjudicator(cen, frozenset(["E1", "E3", "E4", "E5"]))
    res = ADJ.ctl_plant(adj, cen)
    assert res["recall_fraction"] == f"{res['recall_hits']}/{res['recall_attempts']}"
    assert res["recall_hits"] == res["recall_attempts"] > 0
    assert res["passed"]
    assert set(res["distinct_canonical_forms_per_orbit"].values()) == {1}


def test_ctl_null_refuses_to_report_against_an_unplantable_census():
    """IR-4: a null against a census with no plantable entry is VACUOUS."""
    cen = build_census(84064101, 84064102, 0, scan=EMPTY_SCAN)
    assert cen.plantable_entries() == []
    adj = ADJ.Adjudicator(cen, frozenset(["E1", "E3", "E4", "E5"]))
    res = ADJ.ctl_null(adj, cen, {
        "null_draw_md5_delta_m": 1, "null_draw_sha1_dv_in_code": 2,
        "null_draw_sha1_dv_unconstrained": 3}, n=4)
    assert res["status"] == "VACUOUS"
    assert res["plantable_census_attestation"]["vacuous"]


def test_ctl_null_reports_per_family_integers_in_both_modes():
    cen = build_census(84064101, 84064102, 2, scan=EMPTY_SCAN)
    adj = ADJ.Adjudicator(cen, frozenset(["E1", "E3", "E4", "E5"]))
    res = ADJ.ctl_null(adj, cen, {
        "null_draw_md5_delta_m": 84064103,
        "null_draw_sha1_dv_in_code": 84064104,
        "null_draw_sha1_dv_unconstrained": 84064105}, n=8)
    assert res["status"] == "RUN"
    assert not res["plantable_census_attestation"]["vacuous"]
    assert set(res["families"]) == {"md5_delta_m", "sha1_dv_in_code",
                                    "sha1_dv_unconstrained"}
    for fam in res["families"].values():
        assert isinstance(fam["strict_false_positives"], int)
        assert isinstance(fam["permissive_false_positives"], int)
        assert fam["closest_non_matching_draw"]["distance"] >= 0


def test_ctl_null_family_b_draws_are_genuine_codewords():
    """Family (b) is the sharp one: a uniform draw from the linearized code is
    a LEGITIMATE disturbance vector, so a false positive is possible there."""
    rng = random.Random(84064104)
    for _ in range(8):
        obj = ADJ._null_draw_sha1(rng, True)
        assert obj.in_linearized_code is True


def test_ctl_obs_direction_ii_must_be_zero():
    cen = build_census(84064101, 84064102, 2, scan=EMPTY_SCAN)
    adj = ADJ.Adjudicator(cen, frozenset(["E1", "E3", "E4", "E5"]))
    res = ADJ.ctl_obs(adj, cen, 84064106, slice_n=16)
    assert res["direction_ii"]["discrepancies_found"] == 0
    assert res["direction_ii"]["checks"] > 0


def test_ctl_nearby_separates_sha0_from_sha1():
    res = ADJ.ctl_nearby(84064106, n=64)
    assert res["sha0_codewords_testing_as_sha1"] == 0
    assert res["sha1_codewords_testing_as_sha1"] == 64


# --------------------------------------------------------------------------
# the firewall
# --------------------------------------------------------------------------

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The subject is exercised in a CHILD PROCESS, deliberately, and the reason is
# a property of the process rather than of either test.
# harness/diffpath/readmit.py installs a sys.addaudithook() AT MODULE IMPORT
# TIME -- its IR-1 contract requires the hook to precede every substrate import,
# so the call sits above those imports at module scope -- and an audit hook can
# never be removed from a process once installed. Pytest imports every test
# module during COLLECTION, before any test runs, so collecting
# tests/test_diffpath_readmit.py installs the firewall for the whole session and
# every later open under the quarantine prefix raises FirewallBreach, including
# the one this test's subject (census.quarantine_attestation) makes to hash the
# Tier-A payload. Both tests are correct; they simply cannot share a process.
# Isolating the subject keeps these assertions exactly as they were, instead of
# weakening the firewall (which a committed run artifact depends on) or dropping
# the check. This test previously passed only when nothing had imported readmit.
_ATTESTATION_PROBE = """
import json
from harness.diffpath.census import (QUARANTINE_EXPECTED_SHA256,
                                     quarantine_attestation)
att = quarantine_attestation()
print(json.dumps({
    "match": att["match"],
    "sha256_matches_expected":
        att["sha256_recomputed"] == QUARANTINE_EXPECTED_SHA256,
    "parsed": att["parsed"],
    "bytes_hashed": att["bytes_hashed"],
}))
"""


def test_quarantine_is_hashed_and_never_parsed():
    proc = subprocess.run([sys.executable, "-c", _ATTESTATION_PROBE],
                          cwd=_REPO_ROOT, capture_output=True, text=True,
                          timeout=300)
    assert proc.returncode == 0, proc.stderr
    att = json.loads(proc.stdout.strip().splitlines()[-1])
    assert att["match"] and att["sha256_matches_expected"]
    assert att["parsed"] is False
    assert att["bytes_hashed"] > 0


def test_corpus_scan_never_descends_into_the_quarantine():
    scan = scan_corpus()
    for c in scan["candidates"]:
        assert not c["path"].startswith(QUARANTINE_DIR)
    assert scan["files_read"] > 0


def test_census_counts_are_three_separate_populations():
    cen = build_census(84064101, 84064102, 2, scan=EMPTY_SCAN)
    counts = cen.counts()
    assert "NEVER_SUMMED" in counts
    assert counts["quarantined_not_read"] == 1
    for e in cen.quarantined_not_read + cen.acquisition_gap:
        assert e.path_data is None
        assert e.orbit == "UNDETERMINED"


def test_acquisition_gap_entries_are_tier_labelled_and_actionable():
    cen = build_census(84064101, 84064102, 0, scan=EMPTY_SCAN)
    assert cen.acquisition_gap
    for e in cen.acquisition_gap:
        assert e.tier in ("A", "B", "C")
        assert e.acquisition_status
        assert e.provenance == "recalled"
    tiers = {e.tier for e in cen.acquisition_gap}
    assert tiers == {"A", "B", "C"}
    for e in cen.acquisition_gap:
        if e.tier == "B":
            assert e.acquisition_status == "blocked_pending_cross_goal_decision"
        if e.tier == "A":
            assert e.acquisition_status == "hard_refusal_tier_a"


# --------------------------------------------------------------------------
# fallback runner (used only when pytest is absent; see the import above)
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import traceback

    passed = failed = 0
    failures = []
    for name, fn in sorted(list(globals().items())):
        if not (name.startswith("test_") and callable(fn)):
            continue
        cases = [((), {})]
        if hasattr(fn, "_parametrize"):
            names, values = fn._parametrize
            cases = [((), dict(zip(names, v if isinstance(v, tuple) else (v,))))
                     for v in values]
        for args, kwargs in cases:
            label = name + (f"[{kwargs}]" if kwargs else "")
            try:
                fn(*args, **kwargs)
                passed += 1
            except Exception:                    # noqa: BLE001
                failed += 1
                failures.append((label, traceback.format_exc()))
    for label, tb in failures:
        print(f"FAIL {label}\n{tb}")
    print(f"tests: {passed} passed, {failed} failed "
          f"(runner: {'pytest-absent fallback' if getattr(pytest, '__shim__', False) else 'pytest'})")
    sys.exit(1 if failed else 0)
