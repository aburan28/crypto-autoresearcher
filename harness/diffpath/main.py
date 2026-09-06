"""Execute EXP-DIFFP-fe894e's run_plan in its DECLARED ORDER, under its gates.

    python3 -m harness.diffpath.main

Runs 1..6, each charged through harness.runner.run_wrapped with its ceiling
ARMED, each writing an immutable run directory under the task path, and each
gated exactly as the frozen contract's run_plan says:

    1 buildcheck               no gate
    2 equivalence-verification only if run 1 passed
    3 census-build             only if run 1 passed
    4 controls                 only if run 2's verified set is NONEMPTY
    5 observation-collision    only if run 4's CTL-PLANT passed
    6 nearby-object            only if run 1 passed

A gate that closes is recorded as NOT RUN with the gate named, and its ceiling
is reported AS UNSPENT rather than reallocated.
"""
from __future__ import annotations

import json
import os
import time

import yaml

from . import runs as R
from .census import build_census, scan_corpus
from . import adjudicator as ADJ
from . import equivalence as EQ

TASK_ROOT = os.path.join(R.REPO, R.TASK_DIR)


def _emit(suffix: str, fn, gens, out) -> dict:
    """Charge one run and record it; a deadline hit is a BUDGET OUTCOME."""
    t0 = time.monotonic()
    command = (f"python3 -m harness.diffpath.main   # run '{suffix}' of "
               f"{R.EXPERIMENT_ID}, ceiling {R.CEILINGS[suffix]}s armed")
    holder: dict = {}

    def call():
        res, raw = fn()
        holder["raw"] = raw
        return res

    try:
        run_id = R._charge(suffix, call, TASK_ROOT, command)
    except R.DeadlineExceeded as exc:
        rec = {"run_suffix": suffix, "state": "resource_exhaustion",
               "ceiling_seconds": R.CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": str(exc),
               "classification": ("resource_exhaustion -- a BUDGET OUTCOME. "
                                  "Never a negative mathematical result and "
                                  "never a finding about the difference space "
                                  "(AGENTS.md rule 5).")}
        out["runs"].append(rec)
        return rec
    except Exception as exc:                      # noqa: BLE001
        rec = {"run_suffix": suffix, "state": "implementation_error",
               "ceiling_seconds": R.CEILINGS[suffix],
               "wall_seconds": round(time.monotonic() - t0, 3),
               "reason": f"{type(exc).__name__}: {exc}",
               "classification": ("implementation_error -- infrastructure "
                                  "signal, never mathematical evidence.")}
        out["runs"].append(rec)
        return rec

    run_dir = os.path.join(TASK_ROOT, "runs", run_id)
    R.write_supplement(run_dir, suffix, R.CEILINGS[suffix], R.SEEDS, gens)
    with open(os.path.join(run_dir, "manifest.yaml"), encoding="utf-8") as fh:
        man = yaml.safe_load(fh)["run"]
    rec = {"run_suffix": suffix, "run_id": run_id, "state": "completed_valid",
           "run_dir": os.path.relpath(run_dir, R.REPO),
           "ceiling_seconds": R.CEILINGS[suffix],
           "wall_seconds": man["timing"]["wall_seconds"],
           "timing_source": man["timing"].get("timing_source"),
           "peak_rss_bytes": man["resources"]["peak_rss_bytes"],
           "experiment_id_in_manifest": man["experiment_id"],
           "code_path_fingerprint_in_manifest":
               "code_path_fingerprint" in man["inputs"]["parameters"],
           "metrics": man["result"]["metrics"]}
    out["runs"].append(rec)
    out["raw"][suffix] = holder.get("raw")
    return rec


def _not_run(suffix: str, gate: str, out) -> None:
    out["runs"].append({
        "run_suffix": suffix, "state": "not_run", "gate": gate,
        "ceiling_seconds": R.CEILINGS[suffix],
        "ceiling_status": "UNSPENT -- not reallocated to any other run",
    })


def main() -> int:
    os.makedirs(TASK_ROOT, exist_ok=True)
    out: dict = {"experiment_id": R.EXPERIMENT_ID, "runs": [], "raw": {}}

    # ---- run 1
    r1 = _emit("buildcheck", R.run_buildcheck, (), out)
    base_ok = (r1["state"] == "completed_valid"
               and r1["metrics"].get("ctl_base_passed") is True)

    if not base_ok:
        for s, g in (("equivalence-verification", "run 1 CTL-BASE did not pass"),
                     ("census-build", "run 1 CTL-BASE did not pass"),
                     ("controls", "run 1 CTL-BASE did not pass"),
                     ("observation-collision", "run 1 CTL-BASE did not pass"),
                     ("nearby-object", "run 1 CTL-BASE did not pass")):
            _not_run(s, g, out)
        _finish(out)
        return 1

    # ---- run 2
    r2 = _emit("equivalence-verification", R.run_equivalence, (), out)
    verified = sorted(out["raw"]["equivalence-verification"]["verified_generator_set"])

    # ---- run 3 (runs whether or not any generator verified)
    _emit("census-build", R.run_census, verified, out)

    # ---- run 4
    if not verified:
        _not_run("controls",
                 "run 2 verified NO generator: there is no defensible canonical "
                 "form and no adjudication is attempted (contract stopping_rules)",
                 out)
        _not_run("observation-collision", "run 4 did not run", out)
        _emit("nearby-object", R.run_nearby, (), out)
        _finish(out)
        return 0

    r4 = _emit("controls", lambda: R.run_controls(verified), verified, out)
    plant_ok = (r4["state"] == "completed_valid"
                and r4["metrics"].get("ctl_plant_passed") is True)
    null_clean = (r4["state"] == "completed_valid"
                  and r4["metrics"].get("ctl_null_strict_false_positives_total") == 0)

    # ---- run 5
    if not plant_ok:
        _not_run("observation-collision",
                 "run 4 CTL-PLANT did not pass; the contract stops before "
                 "CTL-OBS", out)
    elif not null_clean:
        _not_run("observation-collision",
                 "run 4 CTL-NULL returned a strict-mode false positive; the "
                 "contract STOPS and reports the colliding pair. The "
                 "equivalence is not repaired in-run by dropping a generator.",
                 out)
    else:
        _emit("observation-collision", lambda: R.run_obs(verified), verified, out)

    # ---- run 6 (gated only on run 1)
    _emit("nearby-object", R.run_nearby, (), out)
    _finish(out)
    return 0


def _finish(out: dict) -> None:
    """Write the three declared artifacts from the runs that actually ran."""
    raw = out["raw"]

    # --- equivalence-declaration.yaml
    if "equivalence-verification" in raw:
        eq = raw["equivalence-verification"]
        doc = {"equivalence_declaration": {
            "experiment_id": R.EXPERIMENT_ID,
            "task_id": "TASK-20260824-c6625a",
            "seed": eq["seed"],
            "quantifier_order": eq["quantifier_order"],
            "generators": eq["generators"],
            "verified_generator_set_STRICT": eq["verified_generator_set"],
            "excluded_generator_set": eq["excluded_generator_set"],
            "declared_non_generators": eq["declared_non_generators"],
            "strict_group_is_exactly_the_verified_subset": True,
            "two_verdicts_reported_separately": (
                "The adjudicator reports STRICT (verified generators only) and "
                "PERMISSIVE (all six declared, including the excluded ones) as "
                "two separate fields. They are never merged, averaged or "
                "reported as one number (IR-5). Excluding a real equivalence "
                "over-declares novelty; admitting a false one under-declares "
                "it; both bounds are reported so the direction of any error is "
                "visible."),
            "declared_interpretations": {
                "E1_vs_declared_non_generators": (
                    "E1 shifts the window OFFSET at CONSTANT LENGTH. A "
                    "different step_range LENGTH or extent is a "
                    "declared_non_generator and is never absorbed. This is the "
                    "only reading under which both frozen clauses hold, and it "
                    "is recorded as a stated choice."),
                "E6_gate": (
                    "E6's chaining-value clause was gated on the CONJUNCTION of "
                    "step ranges (0,0) and (0,3), fixed before the run, so that "
                    "the range could not be selected after seeing which passes. "
                    "A range in which no draw satisfies the conditions makes "
                    "the implication vacuous and is NOT reported as a pass."),
                "condition_set_not_in_membership_key": (
                    "The E5-normalised condition signature is REPORTED beside "
                    "every adjudication and is NOT part of the membership key, "
                    "because conditions here are derived from the witness pair "
                    "and are sufficient rather than necessary. Consequence, "
                    "stated: the canonical form is COARSER than 'path plus "
                    "conditions'."),
            },
        }}
        _write_yaml("equivalence-declaration.yaml", doc)

    # --- census.yaml
    if "census-build" in raw:
        cen = raw["census-build"]
        doc = {"census": {
            "experiment_id": R.EXPERIMENT_ID,
            "task_id": "TASK-20260824-c6625a",
            "counts": cen["counts"],
            "counts_note": (
                "readable / quarantined_not_read / acquisition_gap are THREE "
                "SEPARATE POPULATIONS and are NEVER SUMMED into one census "
                "size. Only `readable` entries are canonicalised or counted in "
                "an orbit; pointers contribute nothing to any covering number."),
            "readable_entries": cen["readable"],
            "quarantined_not_read_entries": cen["quarantined_not_read"],
            "acquisition_gap_entries": cen["acquisition_gap"],
            "shadow_census_planted_entries": [
                {k: v for k, v in e.items() if k != "obj"}
                for e in cen["shadow_census"]],
            "shadow_census_note": (
                "MANDATORY, not optional. A null control against a census with "
                "no plantable entry returns NON-MEMBER trivially and has "
                "measured nothing (IR-4). These synthetic entries are what make "
                "a false positive POSSIBLE. They are never counted as readable "
                "census entries and are never cited as published paths."),
            "corpus_scan": cen["corpus_scan"],
            "corpus_scan_candidates": cen["corpus_scan_candidates"],
            "sources_opened_and_found_to_carry_no_path_data": [
                c["path"] for c in cen["corpus_scan_candidates"]
                if not c["carries_path_data"]],
            "preregistered_prediction_P1": cen["preregistered_prediction_P1"],
            "orbit_count_readable_census": {
                "orbits": 0 if not cen["readable"] else None,
                "pointer_entries_excluded":
                    len(cen["quarantined_not_read"]) + len(cen["acquisition_gap"]),
                "note": ("Orbit count is over READABLE entries only. With "
                         f"{cen['counts']['readable']} readable entries the "
                         "orbit count is 0 and carries no information about "
                         "MD5's or SHA-1's difference space."),
            },
        }}
        _write_yaml("census.yaml", doc)

    # --- null-control-result.json
    if "controls" in raw:
        c = raw["controls"]
        doc = {
            "experiment_id": R.EXPERIMENT_ID,
            "task_id": "TASK-20260824-c6625a",
            "CTL_PLANT": c["CTL-PLANT"],
            "CTL_NULL": c["CTL-NULL"],
            "adjudication_modes": c.get("adjudication_modes"),
            "null_family_constructions": c.get("null_family_constructions"),
            "interpretation_limit": (
                "A passing control set licenses ONLY: 'the adjudicator recalls "
                "planted paths and their verified-generator images, and rejects "
                "the declared null draws, at these parameters, against this "
                "census.' It does NOT license 'the adjudicator identifies "
                "published paths correctly' -- untestable until the census has "
                "readable entries -- and it says nothing about MD5's or SHA-1's "
                "difference space. NO PATH IS CLAIMED NEW."),
        }
        with open(os.path.join(TASK_ROOT, "null-control-result.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, sort_keys=True, default=str)

    with open(os.path.join(TASK_ROOT, "run-index.json"), "w", encoding="utf-8") as fh:
        json.dump({k: v for k, v in out.items() if k != "raw"}, fh, indent=2,
                  sort_keys=True, default=str)
    with open(os.path.join(TASK_ROOT, "raw-observations.json"), "w",
              encoding="utf-8") as fh:
        json.dump(out["raw"], fh, indent=2, sort_keys=True, default=str)


def _write_yaml(name: str, doc: dict) -> None:
    with open(os.path.join(TASK_ROOT, name), "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, default_flow_style=False,
                       width=100)


if __name__ == "__main__":
    raise SystemExit(main())
