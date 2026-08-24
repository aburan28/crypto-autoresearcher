"""Read every reference value from its committed record AT RUN TIME.

NO TRANSCRIBED REFERENCE VALUES. Each reader returns both the parsed values and
the sha256 of the file it parsed, so baseline-provenance.json can bind them.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RED_TEAM_NOTES = ("coordination/goals/GOAL-ENDO-001/batches/BATCH-cb71b5/"
                  "reviews/red-team/red_team_notes.md")
ICINV_V2_AMENDMENT = "experiments/EXP-ICINV-4d33aa/amendments/v2.yaml"
INSTR_SPEC = "experiments/EXP-INSTR-36c8cf/specification.yaml"
# The two committed p = 4001 runs that carry per-class rate_m3. Both are read
# and their per-class rate_m3 vectors are compared; a disagreement is fatal.
P4001_RUNS = [
    "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json",
    "experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-b/raw-result.json",
]


def sha256_of(rel: str) -> str:
    with open(os.path.join(REPO, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _text(rel: str) -> str:
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def nullc_published_profile() -> dict:
    """NULL-C power profile, parsed from red_team_notes.md section 5.

    The table is the only committed statement of the profile SR1 must
    reproduce. Its GENERATING CONSTRUCTION (how the between-class mean shift was
    applied) and its PERMUTATION SEEDS are NOT recorded anywhere in that record;
    this reader therefore returns exactly what the record contains and nothing
    inferred.
    """
    txt = _text(RED_TEAM_NOTES)
    sec = txt.split("## 5.")[1].split("## 6.")[0]
    rows = []
    pat = re.compile(r"^\s*(\d+\.\d+)\s+(\d+\.\d+)%\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$")
    for line in sec.splitlines():
        m = pat.match(line)
        if m:
            rows.append({
                "delta": float(m.group(1)),
                "pct_of_mean_published": float(m.group(2)),
                "median_p_published": float(m.group(3)),
                "power_at_0_05_published": float(m.group(4)),
            })
    if not rows:
        raise RuntimeError(f"could not parse the NULL-C profile table from {RED_TEAM_NOTES}")
    reps = re.search(r"(\d+)\s+repetitions each", sec)
    return {
        "source_path": RED_TEAM_NOTES,
        "source_sha256": sha256_of(RED_TEAM_NOTES),
        "source_section": "section 5",
        "rows": rows,
        "repetitions_per_cell": int(reps.group(1)) if reps else None,
        "planting_construction_recorded": False,
        "permutation_seeds_recorded": False,
        "provenance_gap": (
            "red_team_notes.md section 5 states the profile but records neither "
            "the planting construction that produced the delta > 0 rows nor the "
            "permutation seeds used for the 12 repetitions. red_team_report.yaml "
            "objection O3 restates the profile and adds no construction either. "
            "The delta = 0 row is construction-free and IS reproducible."),
    }


def detection_bound_table() -> dict:
    """Section 6 chi-square detection bounds. Recorded; used by Phase B."""
    txt = _text(RED_TEAM_NOTES)
    sec = txt.split("## 6.")[1].split("## 7.")[0]
    rows = []
    pat = re.compile(r"^\s*(.+?)\s+n=\s*(\d+)\s+T=(\d+)\s*->\s*var-ratio\s*>=\s*"
                     r"(\d+\.\d+),\s*excess sd >=\s*(\d+\.\d+)% of the mean\s*$")
    for line in sec.splitlines():
        m = pat.match(line)
        if m:
            rows.append({"label": m.group(1).strip(), "n": int(m.group(2)),
                         "T": int(m.group(3)), "var_ratio_floor": float(m.group(4)),
                         "excess_sd_pct": float(m.group(5))})
    return {"source_path": RED_TEAM_NOTES, "source_sha256": sha256_of(RED_TEAM_NOTES),
            "source_section": "section 6", "rows": rows}


def superseded_band_slacks() -> dict:
    """The [1.3, 3.6] band and its hull slacks, read from amendment v2 A5."""
    txt = _text(ICINV_V2_AMENDMENT)
    blk = txt.split("A5_new_standing_caution_on_the_band:")[1].split("A6_")[0]
    floor_slack = re.search(r"floor slack (\d+\.\d+)", blk)
    ceil_slack = re.search(r"ceiling slack (\d+\.\d+)", blk)
    band = re.search(r"\[(\d+\.\d+),\s*(\d+\.\d+)\]", blk)
    if not (floor_slack and ceil_slack and band):
        raise RuntimeError("could not parse A5 band/slacks from amendment v2")
    return {
        "source_path": ICINV_V2_AMENDMENT,
        "source_sha256": sha256_of(ICINV_V2_AMENDMENT),
        "source_key": "post_review_notes.A5_new_standing_caution_on_the_band",
        "band_low": float(band.group(1)),
        "band_high": float(band.group(2)),
        "floor_slack": float(floor_slack.group(1)),
        "ceiling_slack": float(ceil_slack.group(1)),
        "statement_read_from_record": (
            "the band is the outward-rounded hull of the committed rows it "
            "gates; 1.3 is a hull edge, not an independent threshold"),
    }


def p4001_rate_m3_by_class() -> dict:
    """Per-class rate_m3 at p = 4001, read from the committed run records.

    Both committed runs are read and compared; the returned vectors are used
    only if they agree exactly.
    """
    loaded = []
    for rel in P4001_RUNS:
        with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
            raw = json.load(fh)["raw"]
        groups = {int(k): [r["rate_m3"] for r in v["rows"]]
                  for k, v in raw["per_class"].items()}
        loaded.append({
            "path": rel, "sha256": sha256_of(rel), "p": raw["p"],
            "params": raw["params"], "groups": groups,
        })
    agree = all(x["groups"] == loaded[0]["groups"] for x in loaded)
    return {
        "sources": [{k: v for k, v in x.items() if k != "groups"} for x in loaded],
        "sources_agree_exactly": agree,
        "groups": loaded[0]["groups"] if agree else None,
        "class_sizes": {k: len(v) for k, v in loaded[0]["groups"].items()} if agree else None,
    }


def instr_spec_declared_fields() -> dict:
    """Machine check: does the FROZEN contract declare a numeric SR3 v3 interval
    coverage, and a numeric nominal level?

    The check is deliberately mechanical rather than asserted, so the STOP is
    auditable. It searches the whole contract text for any numeric coverage /
    nominal-level declaration attached to the SR3 v3 central interval.
    """
    txt = _text(INSTR_SPEC)
    cov_pat = re.compile(
        r"(coverage|central interval|nominal level)[^\n]{0,120}?"
        r"(\d{1,3}(?:\.\d+)?\s*%|0\.\d+)", re.IGNORECASE)
    hits = [m.group(0).strip() for m in cov_pat.finditer(txt)]
    # Exclude the sampler-coverage sense, which is a different quantity.
    hits = [h for h in hits if "sampler" not in h.lower()]
    return {
        "source_path": INSTR_SPEC,
        "source_sha256": sha256_of(INSTR_SPEC),
        "numeric_interval_coverage_declared": bool(hits),
        "matches": hits,
        "phrases_found_without_a_number": sorted(set(
            re.findall(r"declared central interval|declared nominal level|"
                       r"interval coverage|declared level", txt, re.IGNORECASE))),
    }
