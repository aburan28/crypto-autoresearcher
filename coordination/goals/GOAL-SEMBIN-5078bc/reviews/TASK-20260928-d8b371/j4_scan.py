#!/usr/bin/env python3
"""TASK-20260928-d8b371 -- review joint J4 (scope and language) of
REVIEW-SEMBIN-20260928-04ec3c.

Mechanical half of the J4 attack. It does NOT judge wording; it makes the
hostile-quoter read reproducible by (a) extracting every sentence that names a
binary curve degree or a named curve, or uses the word "charge", from the four
texts under review, and (b) recomputing from raw-result.json and the frozen
inputs each fact the report's findings rest on.

Texts scanned (all committed):
  T1 experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/manifest.yaml
  T2 experiments/EXP-SEMBIN-04ec3c/specification.yaml   (incl. amendments)
  T3 ledger/hypotheses/H-SEMBIN-8e7ae3.yaml
  T4 the PR #1470 snapshot commit message, git show -s 3c97c0d40
     (the PR body itself could not be fetched: no gh CLI in this sandbox)
Absent and therefore not scanned: experiments/EXP-SEMBIN-04ec3c/RESULTS.md,
and any EV-* record proposed from it.

Standard library + git only. Deterministic.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
RUN = REPO / "experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773"
TEXTS = {
    "T1_manifest": RUN / "manifest.yaml",
    "T2_contract": REPO / "experiments/EXP-SEMBIN-04ec3c/specification.yaml",
    "T3_hypothesis": REPO / "ledger/hypotheses/H-SEMBIN-8e7ae3.yaml",
}
SNAPSHOT_COMMIT = "3c97c0d4057b81cd969583dedb74213a9a69bcd6"
DEGREES = ["97", "109", "131", "163", "191", "233", "239", "283", "409", "571"]
DEG_RE = re.compile(r"(?<![\d.^])(?:n\s*=\s*)?(" + "|".join(DEGREES) +
                    r")(?![\d.])|ECC2K?-\d+|[KB]-\d{3}|binary degree|"
                    r"degrees?\b", re.I)
CHARGE_RE = re.compile(r"\bcharg", re.I)


def sentences(text: str):
    flat = re.sub(r"\s+", " ", text)
    # split on sentence ends, keeping YAML keys as separators too
    for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9'\"(])|\s(?=[a-z_0-9]+:\s)", flat):
        s = s.strip()
        if len(s) > 12:
            yield s


def scan():
    out = {}
    texts = {k: p.read_text() for k, p in TEXTS.items()}
    texts["T4_commit_3c97c0d40"] = subprocess.run(
        ["git", "-C", str(REPO), "show", "-s", "--format=%B", SNAPSHOT_COMMIT],
        capture_output=True, text=True, check=True).stdout
    for key, text in texts.items():
        deg = [s for s in sentences(text) if DEG_RE.search(s)]
        chg = [s for s in sentences(text) if CHARGE_RE.search(s)]
        out[key] = {"degree_or_curve_sentences": deg, "charge_sentences": chg,
                    "n_degree": len(deg), "n_charge": len(chg)}
    return out


def facts():
    raw = json.loads((RUN / "raw-result.json").read_text())
    f = {}
    # F1: n = 131 is instantiated with a curve's subgroup order; others are 2^n
    vow = {c["n"]: c["log2_rho_vow"] for c in raw["mitm_store_free"]}
    f["F1_vow_column_by_degree"] = {str(n): vow[n] for n in sorted(vow)}
    f["F1_vow_minus_(n/2+log2_0.886)"] = {
        str(n): round(vow[n] - (n / 2 + math.log2(0.886)), 4) for n in sorted(vow)}
    f["F1_raw_result_names_a_curve"] = "ecc2k130_min_store" in raw["summary"]
    # F2: the two columns at n = 131, as the run computed them
    r = 680564733841876926932320129493409985129
    f["F2_published_equals_sqrt(pi*r/(4*131))"] = round(
        0.5 * math.log2(math.pi * r / (4 * 131)), 4)
    f["F2_gap_as_run_computed"] = round(vow[131] - 60.8090, 4)
    f["F2_gap_as_A7_and_plan_state"] = round(131 / 2 + math.log2(0.886) - 60.8090, 4)
    f["F2_log2_sqrt_131"] = round(0.5 * math.log2(131), 4)
    f["F2_controls_present_in_raw"] = sorted(raw["controls"])
    # F3: the 720
    free = {(c["n"], c["m"]) for c in raw["mitm_store_free"]
            if c["beats_vow"] and not c["degenerate"]}
    f["F3_store_free_subrho_distinct_(n,m)"] = len(free)
    f["F3_raw_reported"] = raw["controls"]["C-NULL-NO-MEMORY-CHARGE"]["subrho_cells_store_free"]
    # F4: the n = 131 minimum-store curve, against the manifest's P3b sentence
    f["F4_min_store_curve_131"] = {
        str(x["m"]): (x["log2_store_entries"] if x["reachable"] else "unreachable")
        for x in raw["min_store_for_subrho"] if x["n"] == 131}
    # F5: enum d-independence boolean, raw vs manifest
    f["F5_raw_enum_d_independent_everywhere"] = raw["summary"]["enum_d_independent_everywhere"]
    f["F5_raw_max_spread_bits"] = max(e["spread_over_d_bits"] for e in raw["P1_enum_probe"])
    # F6: C-FLOOR-REPRO offsets in A1's own sign convention (committed - recomputed)
    f["F6_A1_offsets_vs_2log2m"] = [
        dict(m=row["m"], offset_A1_sign=round(-row["offset_bits"], 3),
             signature=round(2 * math.log2(row["m"]), 3),
             departure=round(-row["offset_bits"] - 2 * math.log2(row["m"]), 3),
             within_1p5=abs(-row["offset_bits"] - 2 * math.log2(row["m"])) <= 1.5)
        for row in raw["controls"]["C-FLOOR-REPRO"]["rows"]]
    # F7: solve dates in the program's frozen input
    talk = (REPO / "inputs/BAILEY-2009-541-ECC2K130/talk-35minutes_text.md").read_text()
    f["F7_frozen_input_break_dates"] = [ln.strip() for ln in talk.splitlines()
                                        if re.match(r"\s*(1997|1998|1999|2000|2002|2004):", ln)]
    # F8: git ordering of approval vs implementation
    log = subprocess.run(["git", "-C", str(REPO), "log", "--format=%h %s", "--name-status",
                          "--", "experiments/EXP-SEMBIN-04ec3c/code"],
                         capture_output=True, text=True, check=True).stdout
    f["F8_commit_adding_driver"] = log.strip().splitlines()[:3]
    # F9: RESULTS.md
    f["F9_RESULTS_md_exists"] = (REPO / "experiments/EXP-SEMBIN-04ec3c/RESULTS.md").exists()
    return f


def main():
    res = {"scan": scan(), "facts": facts()}
    here = Path(__file__).resolve().parent
    (here / "j4_scan_output.json").write_text(json.dumps(res, indent=1) + "\n")
    for k, v in res["scan"].items():
        print(k, "degree/curve sentences:", v["n_degree"], "| 'charg' sentences:", v["n_charge"])
    for k, v in res["facts"].items():
        print(k, "=", v)


if __name__ == "__main__":
    main()
