"""Writes trial-plan-v1.json from the specification alone plus the pilot's
schedule decision (spec execution.trial_plan_rule): cells, seeds, the chosen
count schedule, phases, output paths, draw procedures and the executor's
pre-data interpretations. It contains no drawn value."""
import datetime
import hashlib
import json

from common import (EXP_ID, CELLS, cell_label, cell_seeds, FIXED_SEEDS, C_STD, C_LOW, FIXED_COUNTS, FIX_A, FIX_B,
                    STREAMS, SEED_BASE, seed_table, dev_cell_seeds, DEV_FIXED_SEEDS)

INTERPRETATIONS = [
    {"id": "V2-RULINGS", "topic": "protocol version 2",
     "text": "The contract in force is the frozen specification (version 1) plus AMD-20260924-3a9f06 (protocol version 2). Implemented as ruled: C-1 first-match classification R0-R6; C-2 E3 success = R3 COLUMN at the target's first non-pivot column, with the PREFIX-first reading reported as E3_prefix_first_sensitivity only; C-3 C-CLASS / INV-10; C-4 C-REPLAYB v2 (a)-(d); C-5 INV-5 v2; C-6 T_strict-guided K_B with ONE PCG64(S_probe) stream consumed in cell order 1..4 and reference order U1..U3, at most 10 draws per reference, probe x = integers(0, 2^n) (the F-RANDX uniform-x routine); C-7 K_B(cell) = sum over unsat references; C-8 F-SAT / F-PLANT stop at N or on exhaustion of the enumerated populations E_SAT (oracle A over every non-degenerate subgroup abscissa, minus references and F-S3 targets) and E_PLANT; exact P_sat; C-9 E3 arm = union by x_R of F-SAT and F-PLANT, DB-5 UNDERPOWERED below 100, DB-7 NOT EVALUABLE on a void or underpowered conjunct; C-10 C-TR v2 with the point test [#E/2] lift(x) = O (cross-checked against the doubling image); C-11 modal per regime, cell, D and family with more than 100 non-degenerate targets; C-12 C-DELTA / C-RANKB also computed on F-NULLB and F-AFFB with their own failure route; C-13 manifest provenance; C-14 the 18 retired seeds replaced by old + 10000 (seed_table_C-14); C-15 dev seeds below 10^6, never a v2 seed; C-16 C-PILOT recorded FAILED pre-run, schedule C_std by its consequence, T_proj reported not binding; C-17 E_SAT by oracle A over all subgroup abscissae, cross-checked by the V x V solve (must be equal, else INV-3); C-18 x(2E) point test [#E/2] lift(x) = O cross-checked by the doubling image (a disagreement voids only the F-RANDX x(2E) split); C-19 stream 01 is ONE logged sequence per cell; C-20..C-23 the readings below confirmed; C-24 |E_PLANT| computed in the run; C-25 the prior (a)-(g) scored as written; C-26 memory caps recorded. No PENDING AMENDMENT mark remains."},
    {"id": "R-1", "topic": "F-AFF references (AMD C-19; spec null_families_A 'Stage-1 construction', reference_rule)",
     "text": "Stream 01 is ONE logged sequence per cell (generator instantiated once, raw draws logged; every reference scan reads the log from position 0 and pulls further draws past its end). F-AFF scans the c01 sequence in order, classifies each non-degenerate, non-duplicate x_R by its own oracle B, and takes the first 3 unsat and the first 2 sat (cap 300,000 draws, shortfall recorded)."},
    {"id": "R-2", "topic": "F-AFFB references (AMD C-19; spec null_families_B 'evaluated ... at the F-S3 references' x_R', reference_rule)",
     "text": "U_i := the x_R of F-S3's U_i wherever it is F-AFFB-unsat by oracle C; S_j := the x_R of F-S3's S_j wherever it is F-AFFB-sat. An unfilled role is filled, in role-index order, by the next x_R of the c01 sequence of the required F-AFFB class that is non-degenerate, not already an F-AFFB reference and not an F-S3 target (cap 300,000 draws, shortfall recorded). Each reference records its source."},
    {"id": "R-3", "topic": "F-RANDX stream (AMD C-20; seeds.formula stream 05 'randx'; reference_rule)",
     "text": "References are scanned first from stream 05; targets continue from the same generator instance: distinct x_R, not a reference x_R, degenerates kept, flagged, excluded from arm statistics and counted toward the target count. At cell 1 stream 05 is the replacement seed 2026092430105 (C-14)."},
    {"id": "R-4", "topic": "C-BREAK coverage (AMD C-21; spec C-BREAK 'Every regime-B ZERO-PIVOT first divergence against an unsat reference')",
     "text": "Every ZERO-PIVOT first divergence of every regime-B family's targets against every unsat reference they are scored against (own and F-S3) is re-verified. The 20 matched targets per cell are the 20 lowest-idx distinct F-S3 targets T_strict-matched to U1, filled from U2 then U3; each minor is taken on the pivots of the reference to which that target is matched."},
    {"id": "R-5", "topic": "C-DET and C-REV scope (AMD C-22; spec C-DET, C-REV)",
     "text": "C-DET: F-S3 U1-U3, S1-S2 and the modal plus the C-DET targets, in regime A at D = 3 and 4 and in regime B, in a separate process. C-REV: the C-REV targets plus F-S3 U1-U3 and S1-S2, reversed; pass/fail per instance on rank, pivot-column set and 1 in R_D; reversed retention is DATA."},
    {"id": "R-6", "topic": "PS0' choice of D (AMD C-23; spec C-PROPS)",
     "text": "Regime A: D = 4 if any non-degenerate unsat F-S3 target of the cell has 1 in R_4, else D = 3. Regime B: every cell where any non-degenerate unsat F-S3 target has 1 in R_66. Up to 20 lowest-idx qualifying targets per cell and regime."},
    {"id": "R-7", "topic": "F-NULLB draws (spec null_families_B: c_i iid uniform in F_{2^n} minus {0})",
     "text": "Each instance draws c_1..c_5 in that order, each integers(1, 2^n). Duplicate 5-tuples are rejections."},
    {"id": "R-8", "topic": "pilot (AMD affirmed_readings_no_change)",
     "text": "The pilot times build + column pass (solver) + row pass (C-PASS) per regime-B instance, 10 instances per cell with x_R = integers(0, 2^n) from a fresh PCG64(S_selftest); n = 17 uses the Stage-1 B, n = 19 a B = integers(1, 2^19) drawn first from the same generator. The regime-B elimination count per cell under C_std is common.b_elimination_count."},
    {"id": "R-9", "topic": "arm denominators",
     "text": "Arm statistics use non-degenerate targets only; retention against the modal uses targets 101.. only. MB3's N_unsat is the non-degenerate unsat F-S3 arm. DB-6 uses F-S3 at D = 4 (regime A) and D = 66 (regime B). DB-9's maximizing reference is the reference attaining retention_family (ties to the first in U1, U2, U3, modal order). DB-10 uses F-S3; TS1R is also reported for the other affine-route families."},
    {"id": "R-10", "topic": "order files",
     "text": "Regime-A row order depends on n (row = mu_index * n + k), so regime-A row-order files are written per (n, l, D); column-order files per (l, D); regime-B files per l."},
]

PHASES = [
    "0 selftest.py (C-SELF, C-FIX); driver --phase pilot: C-PROV (cprov.json), the timing pilot (pilot.json), the schedule decision, this trial plan",
    "1 per cell: curve, points, references and targets of every family, oracles A/B/C, witnesses, C-TR",
    "2 per cell: regime A (F-S3, F-SAT, F-PLANT, F-RANDX, F-AFF, F-NULLF2) at D = 3, 4 with forms and hull",
    "3 per cell: regime B (F-S3, F-SAT, F-PLANT, F-RANDX, F-NULLB, F-AFFB) at D = 66, delta, divergence classification",
    "4 per cell: regime-B fixed-schedule replays (ROW-ORDER divergers and 50 matched), K_B probes, C-BREAK determinants",
    "5 per cell: C-REV (both regimes)",
    "7a PS0' certificates (main process, after phase 5 of every cell)",
    "6 C-DET (separate process, --phase determinism)",
    "7b verifier/verify_cert.py (separate process, verify_command)",
    "8 aggregation, decision rules, run report (--resume)",
]


def write_plan(path, spec_path, spec_sha, run_id, schedule, pilot_sha, T_proj, dev=False, dev_offset=0,
               amendment=None, dev_exploration=None):
    counts = dict(C_STD if schedule == "C_std" else C_LOW)
    counts.update(FIXED_COUNTS)
    cells = []
    for cidx, n, l in CELLS:
        sd = dev_cell_seeds(cidx) if dev else cell_seeds(cidx)
        cells.append({"cidx": cidx, "n": n, "l": l, "label": cell_label(n, l), "seeds": sd,
                      "fixture_A": {f"D{D}": list(FIX_A[(n, l)][D]) for D in (3, 4)},
                      "fixture_B": {"D66": list(FIX_B[l])}})
    fixed = dict(DEV_FIXED_SEEDS) if dev else dict(FIXED_SEEDS)
    plan = {
        "experiment_id": EXP_ID, "run_id": run_id, "version": 1, "dev": dev,
        "protocol_version": 2 if amendment else 1, "amendment": amendment,
        "dev_exploration": dev_exploration,
        "spec_path": spec_path, "spec_sha256": spec_sha,
        "written_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "written_by": "impl/driver.py --phase pilot (make_trial_plan.write_plan)",
        "rule": "written from the specification alone after the pilot decision and before any frozen stream is drawn; contains no drawn value",
        "pilot": {"pilot_json_sha256": pilot_sha, "T_proj_single_worker_seconds": T_proj, "schedule": schedule},
        "schedule": schedule, "counts": counts,
        "seed_formula": f"seed(c, s) = {SEED_BASE} + 100*c + s; streams {STREAMS}; the 18 retired seeds of AMD-20260924-3a9f06 C-14 replaced by old + 10000 (seed_table)",
        "seed_table_C-14": seed_table(),
        "seeds_fixed": fixed, "cells": cells,
        "generator": "numpy.random.Generator(numpy.random.PCG64(seed)), one per stream",
        "phases": PHASES,
        "workers": {"initial": 1, "maximum": 2,
                    "rule": "a second worker only after the serial-versus-sharded byte-identity check on the 20 lowest-idx F-S3 targets of cell (17, 6), both regimes (regime A at D = 3 and 4), is recorded"},
        "outputs": ["selftest.json", "cprov.json", "pilot.json", "cells.json", "column-order-*.json", "row-order-*.json",
                    "references-<cell>.json", "oplogs-<cell>-<regime>-D<D>.jsonl.gz",
                    "targets-<cell>-<regime>-<family>[-D<D>].jsonl.gz", "regimeB-breaks-<cell>.json",
                    "pivot-hazards-<cell>.json", "ps0prime-certificates.jsonl.gz", "ps0prime-verification.json",
                    "cell-summary.json", "instrument-checks.json", "decision-rules.json", "sizing.json",
                    "manifest.yaml", "raw-result.json", "command.txt", "environment.json", "stdout.log",
                    "stderr.log", "run-report.md", "implementation.md"],
        "draw_procedures": {
            "curve19": "S_curve19: repeat A = integers(0, 2^19), B = integers(0, 2^19); reject B = 0 and orders not h*q (h in {2, 4}, q prime)",
            "points19": "S_pts19: repeat x = integers(0, 2^19) until liftable and [h]lift(x) != O; P = [h]lift(x); k_Q = integers(1, q); Q = [k_Q]P",
            "curve_target": "a = integers(0, q), b = integers(0, q); R = [a]P + [b]Q; redraw if R = O",
            "randx": "x_R = integers(0, 2^n)",
            "nullAff": "Stage-1 draw_affine_null on the cell's supports (bits integers(0, 2) on supp(E^0), then supp(E^j), j = 0..n-1)",
            "nullF2": "Stage-1: bits integers(0, 2) on the union support U (row-major positions)",
            "nullB": "c_1..c_5 = integers(1, 2^n) each, in order",
            "affB": "alpha_1..alpha_5 = integers(1, 2^n) each, drawn once",
            "plant": "i1 = integers(0, |F_V|), i2 = integers(0, |F_V|); Stage-1 rejections",
            "probe": "x = integers(0, 2^n); ONE PCG64(S_probe) instantiated once, consumed in cell order 1..4, references U1..U3, at most 10 draws per reference (AMD C-6); regenerated on resume by re-drawing the recorded per-cell draws",
            "stream01": "ONE logged sequence per cell (AMD C-19): raw (a, b) draws logged; F-S3, F-AFF and F-AFFB reference scans read the log from position 0",
        },
        "interpretations": INTERPRETATIONS,
    }
    txt = json.dumps(plan, indent=1)
    with open(path, "x") as f:
        f.write(txt)
    return hashlib.sha256(txt.encode()).hexdigest(), plan
