#!/usr/bin/env python3
"""TASK-20260928-3f90b8 / joint J2 -- does the A1-amended C-FLOOR-REPRO still
have failure power?

Builds WRONG implementations of EXP-SEMBIN-04ec3c as real code: each mutant is
the committed driver with an exact, count-checked textual patch. Every mutant
is run END TO END with the committed command line, and its raw output is then
graded by the following, all re-implemented here from the contract text and
not from the producer's code:

  A1(i)   structural gate  -- ordering, strict monotone decrease in m, margin
                              signs vs 2^60.8090 incl. m=3 above / m=4 below
  A1(ii)  offset signature -- positive, monotone increasing in m, and within
                              1.5 bits of 2*log2(m) at every row
  C-M3-ANCHOR              -- read from the mutant's own output
  producer gate            -- the `passed` field the committed code computes
  PROPOSED gate            -- transcription/identity tests (see bottom)

and its load-bearing outputs (P2, P4, P5) are recorded, so that "passes every
gate" can be set beside "changes the answer".

Reads only committed bytes: the driver's sha256 must equal the digest the run
recorded in runs/RUN-SEMBIN-c68773/artifact-digests.json. Mutant raw outputs
are written to a temporary directory and only summaries are kept.

Usage: python3 j2_mutation_harness.py [--out j2_results.json]
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
DRIVER = os.path.join(REPO, "experiments/EXP-SEMBIN-04ec3c/code/memory_charged_family.py")
DRIVER_SHA256 = "75cd2252948e09e38149ec6d13c339e54e0a100fe3ecb235ed90ab59ec0fe998"
RAW_SHA256 = "9569c9c099172ea9f6367b79a3f0cce7cfa1b781f0650a56f48cfae54e8e5126"
HERE = os.path.dirname(os.path.abspath(__file__))

PUBLISHED_RHO = 60.8090
# A1's own reference offsets (committed minus "standard balance"), quoted from
# specification.yaml coordinator_amendments_pre_approval[A1].finding.
A1_REFERENCE_OFFSETS = {2: 1.92, 3: 3.08, 4: 4.00, 5: 4.77, 6: 5.42, 8: 6.50}

# --------------------------------------------------------------------------
# mutants: (id, description, why_wrong, [(old, new, expected_count), ...])
# --------------------------------------------------------------------------
MUTANTS = [
    ("M0-committed", "the committed driver, unmodified (reference)", None, []),
    ("M1-drop-mfact",
     "decomposition probability computed as |F|^m/N instead of |F|^m/(m! N): "
     "the m! term is dropped from the yield",
     "contradicts cost_model.decomposition_probability (p = |F|^m/(m! * N)) "
     "and cost_model.trials_per_relation (m! * N / |F|^m)",
     [("relation = d + log2_factorial(m) + (nn - m * d) + oracle_t",
       "relation = d + (nn - m * d) + oracle_t", 1)]),
    ("M1b-drop-mfact-use-E",
     "M1 plus the curve order 2^n used in place of the prime subgroup order "
     "(this is the 'standard balance' reconstruction quoted in A1)",
     "contradicts decomposition_probability (m! dropped) AND its explicit "
     "instruction to use the prime subgroup order N rather than #E",
     [("relation = d + log2_factorial(m) + (nn - m * d) + oracle_t",
       "relation = d + (nn - m * d) + oracle_t", 1),
      ("    if n == 131:\n        return ECC2K130_LOG2_R\n    return float(n)",
       "    return float(n)", 1)]),
    ("M2-mitm-offbyone",
     "MITM tabulates floor((m-1)/2) summands instead of floor(m/2), probing "
     "with the rest: an off-by-one in the ORACLE EXPONENT that is invisible "
     "at m = 3 and pessimistic by one factor |F| at every even m",
     "contradicts oracle_models MITM (cost |F|^ceil(m/2), memory |F|^floor(m/2)) "
     "and MITM_CAPPED (s = min(floor(m/2), ...))",
     [("        s = m // 2\n        return math.ceil(m / 2) * d, s * d, s",
       "        s = (m - 1) // 2\n        return (m - s) * d, s * d, s", 1),
      ("        if budget_log2_entries is None:\n            s = m // 2",
       "        if budget_log2_entries is None:\n            s = (m - 1) // 2", 1),
      ("            s = min(m // 2, max(0, s_max))",
       "            s = min((m - 1) // 2, max(0, s_max))", 1)]),
    ("M3-mitm-swap",
     "MITM time and store exponents swapped (time |F|^floor(m/2), store "
     "|F|^ceil(m/2)): optimistic by one factor |F| at every odd m",
     "contradicts oracle_models MITM",
     [("        s = m // 2\n        return math.ceil(m / 2) * d, s * d, s",
       "        s = math.ceil(m / 2)\n        return (m // 2) * d, s * d, s", 1)]),
    ("M4-budget-ceil",
     "MITM_CAPPED rounds the store budget UP (s_max = ceil(log2 B / d)), so "
     "the tabulated store can exceed the declared budget B by up to d bits",
     "contradicts oracle_models MITM_CAPPED (s = min(floor(m/2), "
     "floor(log2(B)/d)), memory |F|^s <= B)",
     [("            s_max = 0 if d <= 0 else int(budget_log2_entries // d)",
       "            s_max = 0 if d <= 0 else math.ceil(budget_log2_entries / d)", 1)]),
]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def build_mutant(src: str, patches) -> str:
    out = src
    for old, new, count in patches:
        found = out.count(old)
        if found != count:
            raise SystemExit(f"patch anchor matched {found} times, expected {count}: {old!r}")
        out = out.replace(old, new)
    return out


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# graders, re-implemented from the contract text
# --------------------------------------------------------------------------
def a1_structural_gate(rows) -> dict:
    ms = [r["m"] for r in rows]
    com = {r["m"]: r["committed_log2"] for r in rows}
    rec = {r["m"]: r["recomputed_log2"] for r in rows}
    ordering = sorted(ms, key=lambda m: com[m]) == sorted(ms, key=lambda m: rec[m])
    strictly_dec = all(rec[ms[i]] > rec[ms[i + 1]] for i in range(len(ms) - 1))
    signs = all((com[m] < PUBLISHED_RHO) == (rec[m] < PUBLISHED_RHO) for m in ms)
    m3_above = rec[3] > PUBLISHED_RHO
    m4_below = rec[4] < PUBLISHED_RHO
    return {"ordering_preserved": ordering, "strict_monotone_decrease": strictly_dec,
            "all_margin_signs_agree": signs, "m3_strictly_above": m3_above,
            "m4_strictly_below": m4_below,
            "passes": bool(ordering and strictly_dec and signs and m3_above and m4_below)}


def a1_signature(offsets: dict) -> dict:
    """A1(ii): positive, monotone increasing in m, within 1.5 bits of 2*log2(m)."""
    ms = sorted(offsets)
    dep = {m: round(offsets[m] - 2 * math.log2(m), 4) for m in ms}
    positive = all(offsets[m] > 0 for m in ms)
    monotone = all(offsets[ms[i]] <= offsets[ms[i + 1]] + 1e-9 for i in range(len(ms) - 1))
    within = all(abs(dep[m]) <= 1.5 for m in ms)
    return {"offsets": {m: round(offsets[m], 4) for m in ms},
            "departure_from_2log2m": dep,
            "rows_departing_more_than_1p5": [m for m in ms if abs(dep[m]) > 1.5],
            "positive": positive, "monotone_increasing": monotone,
            "within_1p5_bits_everywhere": within,
            "passes": bool(positive and monotone and within)}


def proposed_gate(mod) -> dict:
    """Transcription/identity tests against the contract text.

    (a) yield identity: with the FREE oracle, relation_phase - d must equal
        log2(N) - log2(C(2^d, m)) (the exact count of m-subsets over the
        group order), to within 0.05 bits, at d >= 16.
    (b) oracle closed forms at EVERY m in 2..16, both parities.
    (c) budget invariant: tabulated store s*d never exceeds log2 B.
    """
    fails = []
    for d in (16.0, 24.0, 32.0):
        for m in range(2, 17):
            c = mod.cost_at(163, m, "FREE", d, None)
            got = c.log2_relation_phase - d
            log2_binom = (math.lgamma(2 ** d + 1) - math.lgamma(m + 1)
                          - math.lgamma(2 ** d - m + 1)) / math.log(2)
            want = mod.subgroup_log2(163) - log2_binom
            if abs(got - want) > 0.05:
                fails.append(f"yield identity d={d} m={m}: got {got:.3f} want {want:.3f}")
    for m in range(2, 17):
        d = 10.0
        if mod.oracle_log2("ENUM", m, d, None)[:2] != ((m - 1) * d, 0.0):
            fails.append(f"ENUM closed form m={m}")
        t, st, _ = mod.oracle_log2("MITM", m, d, None)
        if (t, st) != (math.ceil(m / 2) * d, (m // 2) * d):
            fails.append(f"MITM closed form m={m}: got ({t},{st})")
        for b in (30.0, 45.0, 80.0):
            s_want = min(m // 2, int(b // d))
            t, st, s = mod.oracle_log2("MITM_CAPPED", m, d, b)
            if (t, st, s) != ((m - s_want) * d, s_want * d, s_want):
                fails.append(f"MITM_CAPPED closed form m={m} B={b}: got s={s}")
            if st > b + 1e-9:
                fails.append(f"budget invariant violated m={m} B={b}: store {st} > {b}")
    return {"passes": not fails, "n_failures": len(fails), "first_failures": fails[:6]}


def downstream(raw: dict) -> dict:
    s = raw["summary"]
    p5 = raw["P5_subrho_cells_at_budget_le_2_80"]
    over_budget = [c for c in raw["mitm_capped"]
                   if c["budget_log2_entries"] is not None
                   and c["s_tabulated"] * c["d"] > c["budget_log2_entries"] + 1e-9]
    by_deg = raw["min_store_by_degree"]
    return {
        "P2_first_m_below_published_at_131_store_free":
            s["mitm_store_free_first_m_below_published_rho_at_131"],
        "P4_ecc2k130_min_store": s["ecc2k130_min_store"],
        "min_store_by_degree_97": by_deg.get("97"),
        "P5_any_subrho_cell_at_budget_le_2_80": s["any_subrho_cell_at_budget_le_2_80"],
        "P5_n_cells": len(p5),
        "P5_degrees_hit": sorted({c["n"] for c in p5}),
        "P5_example_cells": [
            {k: c[k] for k in ("n", "m", "budget_log2_entries", "d", "s_tabulated",
                               "log2_total", "log2_rho_vow", "log2_store_entries")}
            for c in sorted(p5, key=lambda c: (c["n"], c["budget_log2_entries"], c["m"]))[:4]],
        "capped_cells_whose_store_exceeds_their_budget": len(over_budget),
        "null_control": raw["controls"]["C-NULL-NO-MEMORY-CHARGE"],
    }


def grade(raw: dict, mod) -> dict:
    fr = raw["controls"]["C-FLOOR-REPRO"]
    rows = fr["rows"]
    a1_convention = {r["m"]: r["committed_log2"] - r["recomputed_log2"] for r in rows}
    code_convention = {r["m"]: r["offset_bits"] for r in rows}
    return {
        "producer_gate_passed": fr["passed"],
        "A1_structural_gate": a1_structural_gate(rows),
        "A1_signature_A1_convention": a1_signature(a1_convention),
        "A1_signature_code_field_literal": a1_signature(code_convention),
        "C_M3_ANCHOR_passed": raw["controls"]["C-M3-ANCHOR"]["passed"],
        "C_M3_ANCHOR_detail": {k: raw["controls"]["C-M3-ANCHOR"][k]["log2_total_min"]
                               for k in ("ENUM", "MITM")},
        "proposed_transcription_gate": proposed_gate(mod),
        "floor_rows_recomputed": {r["m"]: r["recomputed_log2"] for r in rows},
        "downstream": downstream(raw),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "j2_results.json"))
    args = ap.parse_args()

    got = sha256_file(DRIVER)
    if got != DRIVER_SHA256:
        raise SystemExit(f"driver sha256 {got} != recorded {DRIVER_SHA256}; refusing")
    src = open(DRIVER).read()

    results = {"task_id": "TASK-20260928-3f90b8", "joint": "J2",
               "driver": os.path.relpath(DRIVER, REPO), "driver_sha256": got,
               "python": sys.version.split()[0],
               "sanity_A1_reference_offsets_vs_signature":
                   a1_signature(dict(A1_REFERENCE_OFFSETS)),
               "mutants": {}}
    diffdir = os.path.join(HERE, "j2_mutants")
    os.makedirs(diffdir, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for mid, desc, why_wrong, patches in MUTANTS:
            msrc = build_mutant(src, patches)
            mpath = os.path.join(tmp, f"{mid.replace('-', '_')}.py")
            with open(mpath, "w") as fh:
                fh.write(msrc)
            if patches:
                diff = "".join(difflib.unified_diff(
                    src.splitlines(True), msrc.splitlines(True),
                    fromfile="a/" + os.path.relpath(DRIVER, REPO),
                    tofile="b/" + os.path.relpath(DRIVER, REPO) + f" ({mid})"))
                with open(os.path.join(diffdir, f"{mid}.diff"), "w") as fh:
                    fh.write(diff)
            rawp = os.path.join(tmp, f"{mid}.json")
            subprocess.run([sys.executable, mpath, "--out", rawp], check=True)
            raw_sha = sha256_file(rawp)
            raw = json.load(open(rawp))
            mod = load_module(mpath, mid.replace("-", "_"))
            g = grade(raw, mod)
            g.update({"description": desc, "why_wrong": why_wrong,
                      "raw_result_sha256": raw_sha,
                      "raw_identical_to_committed_run": raw_sha == RAW_SHA256,
                      "passes_every_declared_gate": bool(
                          g["producer_gate_passed"]
                          and g["A1_structural_gate"]["passes"]
                          and g["A1_signature_A1_convention"]["passes"]
                          and g["C_M3_ANCHOR_passed"])})
            results["mutants"][mid] = g
            print(f"{mid:22s} gate={g['A1_structural_gate']['passes']!s:5s} "
                  f"sig={g['A1_signature_A1_convention']['passes']!s:5s} "
                  f"m3={g['C_M3_ANCHOR_passed']!s:5s} "
                  f"proposed={g['proposed_transcription_gate']['passes']!s:5s} "
                  f"P2={g['downstream']['P2_first_m_below_published_at_131_store_free']} "
                  f"P4={g['downstream']['P4_ecc2k130_min_store'] and (g['downstream']['P4_ecc2k130_min_store']['m_minimising_store'], g['downstream']['P4_ecc2k130_min_store']['min_log2_store_entries'])} "
                  f"P5={g['downstream']['P5_any_subrho_cell_at_budget_le_2_80']}"
                  f"({g['downstream']['P5_n_cells']})", flush=True)
    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=False)
        fh.write("\n")


if __name__ == "__main__":
    main()
