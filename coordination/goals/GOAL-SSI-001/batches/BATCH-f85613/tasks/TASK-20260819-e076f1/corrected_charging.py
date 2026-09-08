#!/usr/bin/env python3
"""
TASK-20260819-e076f1 (BATCH-f85613, GOAL-SSI-001) -- standalone corrected
van-Oorschot-Wiener charging law for EXP-WESOVOW-001.

STANDALONE: Python 3 stdlib + numpy only. Does NOT import anything from
experiments/EXP-WESOVOW-001/. Reads three committed inputs as plain text/JSON
(never imported as code):

  1. experiments/EXP-WESOVOW-001/cost_model.py            (read as TEXT, to
     extract the FIELD_SIZES list and the PAPER_PAIRS literal dict by
     regex -- this is "reading a committed input", not importing the module)
  2. experiments/EXP-WESOVOW-001/specification.yaml        (read as TEXT, to
     extract scenario_definitions.field_sizes_log2p / memory_budgets_log2w_entries
     / overhead_scenarios.c_values -- a hand-rolled parser for these three flat
     numeric lists only; no PyYAML, which is not stdlib/numpy)
  3. experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json (read as
     JSON, for the committed per_field optimal.log2T / optimal.log2M, the
     committed van_oorschot_wiener block, and the committed crossover block)

It writes ONLY recomputed_table.json, in its own directory (CWD-independent:
resolved relative to this script's own path).

Two charging laws are implemented:

  AS_RUN (reverse-engineered from RUN-WESOVOW-001/raw-result.json's own
  numbers and its own embedded "model.formulas.T_w_vOW" string,
  "T_full / sqrt(min(w, M))"):

      log2T_w = log2T_full - 0.5 * min(log2w, log2M) + overhead_bits
      log2w_star = 2 * (log2T_full + overhead_bits - log2T_DG)

  This is a memory-COUNT square root, not a memory-RATIO square root: it does
  NOT reduce to log2T_full at w = M in general (it reduces to
  log2T_full - 0.5*log2M), and it makes T(w) *smaller* as w shrinks below M
  (attacker-favourable, wrong direction of a genuine time-memory tradeoff).

  CORRECTED (per ledger/corrections/CORR-20260808-c792f8 and the red-team
  report at coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/reviews/
  TASK-20260806-9536f4/red_team_report.md section 4, derived independently
  here from the paper's own stated law, paper l.39: "time essentially
  sqrt(N^3/w) = p^{1/2+o(1)}/w^{1/2}", i.e. T(w) = T_full * sqrt(M/w) for
  w <= M and T(w) = T_full for w >= M):

      log2T_w = log2T_full + 0.5 * max(0, log2M - log2w) + overhead_bits
      log2w_star = log2M + 2 * (log2T_full + overhead_bits - log2T_DG)

Both laws are evaluated at BOTH anchors:

  fitted_opt   -- RUN-WESOVOW-001/raw-result.json per_field "optimal" log2T
                  and log2M (the B-grid-optimized, Dickman-fitted values)
  paper_pairs  -- cost_model.py's own PAPER_PAIRS literal (log2time, log2memory)
                  read as text from cost_model.py, i.e. the paper's raw
                  Section 4.1 pairs before any optimizer fit

No SageMath, no g6k, no network access. Deterministic: no randomness is used.
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))

COST_MODEL_PY = os.path.join(REPO_ROOT, "experiments", "EXP-WESOVOW-001", "cost_model.py")
SPEC_YAML = os.path.join(REPO_ROOT, "experiments", "EXP-WESOVOW-001", "specification.yaml")
RAW_RESULT_JSON = os.path.join(
    REPO_ROOT, "experiments", "EXP-WESOVOW-001", "runs", "RUN-WESOVOW-001", "raw-result.json"
)

OUT_PATH = os.path.join(HERE, "recomputed_table.json")


def _fail(msg):
    sys.stderr.write("FATAL: " + msg + "\n")
    sys.exit(1)


def read_text(path):
    if not os.path.isfile(path):
        _fail(f"committed input not found at resolved path: {path}")
    with open(path, "r") as f:
        return f.read()


# --------------------------------------------------------------- parse inputs
def parse_cost_model_literals(text):
    """Extract FIELD_SIZES and PAPER_PAIRS from cost_model.py SOURCE TEXT via
    regex only -- the module is never imported/executed."""
    m = re.search(r"FIELD_SIZES\s*=\s*\[([^\]]*)\]", text)
    if not m:
        _fail("could not locate FIELD_SIZES literal in cost_model.py text")
    field_sizes = [int(x.strip()) for x in m.group(1).split(",") if x.strip()]

    m = re.search(r"PAPER_PAIRS\s*=\s*\{([^}]*)\}", text, re.DOTALL)
    if not m:
        _fail("could not locate PAPER_PAIRS literal in cost_model.py text")
    body = m.group(1)
    pairs = {}
    for pm in re.finditer(r"(\d+)\s*:\s*\(([\d.]+)\s*,\s*([\d.]+)\)", body):
        p, t, mem = pm.groups()
        pairs[int(p)] = (float(t), float(mem))
    if not pairs:
        _fail("PAPER_PAIRS literal matched but no (log2time, log2memory) entries parsed")
    return field_sizes, pairs


def parse_spec_scenario_lists(text):
    """Hand-rolled extraction of three flat numeric YAML lists (no PyYAML,
    which is neither stdlib nor numpy)."""

    def flat_list_after(label):
        m = re.search(re.escape(label) + r":\s*\n((?:\s*-\s*[\d.]+\s*\n?)+)", text)
        if not m:
            _fail(f"could not locate flat list '{label}:' in specification.yaml text")
        return [float(x) for x in re.findall(r"-\s*([\d.]+)", m.group(1))]

    field_sizes = [int(x) for x in flat_list_after("field_sizes_log2p")]
    memory_budgets = [int(x) for x in flat_list_after("memory_budgets_log2w_entries")]
    c_values = flat_list_after("c_values")
    return field_sizes, memory_budgets, c_values


# ---------------------------------------------------------------- the two laws
def as_run_law(log2Tfull, log2M, log2w, overhead_bits):
    """Reverse-engineered from RUN-WESOVOW-001's own committed numbers:
    log2T(w) = log2Tfull - 0.5*min(log2w, log2M) + overhead_bits."""
    return log2Tfull - 0.5 * min(log2w, log2M) + overhead_bits


def as_run_crossover(log2Tfull, log2TDG, overhead_bits):
    return 2.0 * (log2Tfull + overhead_bits - log2TDG)


def corrected_law(log2Tfull, log2M, log2w, overhead_bits):
    """T(w) = T_full * sqrt(M / min(w, M)):
    log2T(w) = log2Tfull + 0.5*max(0, log2M - log2w) + overhead_bits."""
    return log2Tfull + 0.5 * max(0.0, log2M - log2w) + overhead_bits


def corrected_crossover(log2Tfull, log2M, log2TDG, overhead_bits):
    return log2M + 2.0 * (log2Tfull + overhead_bits - log2TDG)


def main():
    cost_model_text = read_text(COST_MODEL_PY)
    spec_text = read_text(SPEC_YAML)
    with open(RAW_RESULT_JSON, "r") as f:
        raw = json.load(f)

    cm_field_sizes, paper_pairs = parse_cost_model_literals(cost_model_text)
    spec_field_sizes, memory_budgets, c_values = parse_spec_scenario_lists(spec_text)

    if sorted(cm_field_sizes) != sorted(spec_field_sizes):
        _fail(
            f"field size lists disagree between cost_model.py {cm_field_sizes} "
            f"and specification.yaml {spec_field_sizes}"
        )
    field_sizes = spec_field_sizes

    anchors = {}
    for b2p in field_sizes:
        key = f"log2p={b2p}"
        opt = raw["per_field"][key]["optimal"]
        anchors.setdefault("fitted_opt", {})[b2p] = {
            "log2Tfull": opt["log2T"],
            "log2M": opt["log2M"],
            "source": f"runs/RUN-WESOVOW-001/raw-result.json per_field.{key}.optimal.{{log2T,log2M}}",
        }
        pt, pm = paper_pairs[b2p]
        anchors.setdefault("paper_pairs", {})[b2p] = {
            "log2Tfull": pt,
            "log2M": pm,
            "source": "cost_model.py PAPER_PAIRS literal (text-parsed, not imported)",
        }

    results = {
        "task_id": "TASK-20260819-e076f1",
        "generated_by": "corrected_charging.py (standalone, stdlib+numpy only)",
        "committed_inputs": {
            "cost_model_py": os.path.relpath(COST_MODEL_PY, REPO_ROOT),
            "specification_yaml": os.path.relpath(SPEC_YAML, REPO_ROOT),
            "raw_result_json": os.path.relpath(RAW_RESULT_JSON, REPO_ROOT),
        },
        "laws": {
            "as_run": "log2T(w) = log2Tfull - 0.5*min(log2w, log2M) + overhead_bits "
                      "(reverse-engineered from RUN-WESOVOW-001's own committed numbers "
                      "and its embedded formulas.T_w_vOW string)",
            "corrected": "log2T(w) = log2Tfull + 0.5*max(0, log2M - log2w) + overhead_bits "
                         "(derived from the paper's own stated law l.39: "
                         "T(w) = T_full*sqrt(M/w), w<=M; T(w)=T_full, w>=M)",
        },
        "field_sizes": field_sizes,
        "memory_budgets_log2w": memory_budgets,
        "overhead_c_values": c_values,
        "per_anchor": {},
        "rg1_reproduction_check": {},
        "rg2_cap_check": {},
    }

    for anchor_name, per_field in anchors.items():
        anchor_block = {}
        for b2p in field_sizes:
            a = per_field[b2p]
            log2Tfull = a["log2Tfull"]
            log2M = a["log2M"]
            log2TDG = b2p / 2.0

            vow = {}
            for lw in memory_budgets:
                row = {}
                for c in c_values:
                    overhead_bits = c * math.sqrt(b2p)
                    as_run_t = as_run_law(log2Tfull, log2M, lw, overhead_bits)
                    corr_t = corrected_law(log2Tfull, log2M, lw, overhead_bits)
                    row[f"c={c}"] = {
                        "overhead_bits": overhead_bits,
                        "as_run_log2T_w": as_run_t,
                        "as_run_beats_baseline": bool(log2TDG - as_run_t > 0.0),
                        "corrected_log2T_w": corr_t,
                        "corrected_beats_baseline": bool(log2TDG - corr_t > 0.0),
                        "delta_corrected_minus_as_run_bits": corr_t - as_run_t,
                    }
                vow[f"w=2^{lw}"] = row

            crossover = {}
            for c in c_values:
                overhead_bits = c * math.sqrt(b2p)
                as_run_wstar = as_run_crossover(log2Tfull, log2TDG, overhead_bits)
                corr_wstar = corrected_crossover(log2Tfull, log2M, log2TDG, overhead_bits)
                crossover[f"c={c}"] = {
                    "as_run_log2w_star": as_run_wstar,
                    "as_run_feasible_at_or_below_M": bool(as_run_wstar <= log2M),
                    "corrected_log2w_star": corr_wstar,
                    "corrected_feasible_at_or_below_M": bool(corr_wstar <= log2M),
                }

            anchor_block[f"log2p={b2p}"] = {
                "anchor_log2Tfull": log2Tfull,
                "anchor_log2M": log2M,
                "anchor_source": a["source"],
                "baseline_log2TDG": log2TDG,
                "van_oorschot_wiener": vow,
                "crossover": crossover,
            }
        results["per_anchor"][anchor_name] = anchor_block

    # ---------------------------------------------------- RG-1 reproduction gate
    # Recompute the committed van_oorschot_wiener log2T_w values under the
    # AS_RUN law at the fitted_opt anchor and diff against raw-result.json.
    max_abs_diff = 0.0
    per_field_diffs = {}
    for b2p in field_sizes:
        key = f"log2p={b2p}"
        committed_vow = raw["per_field"][key]["van_oorschot_wiener"]
        recomputed_vow = results["per_anchor"]["fitted_opt"][key]["van_oorschot_wiener"]
        diffs = {}
        for lw_key, committed_row in committed_vow.items():
            for c_key, committed_cell in committed_row.items():
                committed_val = committed_cell["log2T_w"]
                recomputed_val = recomputed_vow[lw_key][c_key]["as_run_log2T_w"]
                d = abs(committed_val - recomputed_val)
                max_abs_diff = max(max_abs_diff, d)
                diffs[f"{lw_key}/{c_key}"] = {
                    "committed": committed_val,
                    "recomputed_as_run_law": recomputed_val,
                    "abs_diff": d,
                }
        per_field_diffs[key] = diffs
    results["rg1_reproduction_check"] = {
        "law_used": "as_run (reverse-engineered)",
        "anchor_used": "fitted_opt",
        "tolerance_abs": 1e-9,
        "max_abs_diff_observed": max_abs_diff,
        "pass": bool(max_abs_diff <= 1e-9),
        "note": ("Also separately checked in defect_localization.md / control_report.md "
                 "against cost_model.py's CURRENT source-code formula, which does NOT "
                 "match raw-result.json (that check is reported there, not here, since "
                 "it fails and this script's per_field_diffs is the as_run-law identity "
                 "check that is expected, by construction, to pass)."),
        "per_field_diffs": per_field_diffs,
    }

    # ---------------------------------------------------------- RG-2 cap check
    rg2 = {}
    for anchor_name, per_field in anchors.items():
        rg2[anchor_name] = {}
        for b2p in field_sizes:
            a = per_field[b2p]
            log2Tfull = a["log2Tfull"]
            log2M = a["log2M"]
            as_run_at_M = as_run_law(log2Tfull, log2M, log2M, 0.0)
            corrected_at_M = corrected_law(log2Tfull, log2M, log2M, 0.0)
            rg2[anchor_name][f"log2p={b2p}"] = {
                "log2M": log2M,
                "log2Tfull": log2Tfull,
                "as_run_log2T_at_w_eq_M": as_run_at_M,
                "as_run_equals_Tfull": bool(abs(as_run_at_M - log2Tfull) <= 1e-9),
                "corrected_log2T_at_w_eq_M": corrected_at_M,
                "corrected_equals_Tfull": bool(abs(corrected_at_M - log2Tfull) <= 1e-9),
            }
    results["rg2_cap_check"] = rg2

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2, sort_keys=False)

    print(f"wrote {OUT_PATH}")
    print(f"RG-1 (as_run law reproduces raw-result.json to 1e-9): "
          f"{results['rg1_reproduction_check']['pass']} "
          f"(max_abs_diff={max_abs_diff:.3e})")
    for b2p in field_sizes:
        r2 = rg2["fitted_opt"][f"log2p={b2p}"]
        print(f"  RG-2 log2p={b2p}: as_run T(M)==Tfull? {r2['as_run_equals_Tfull']}  "
              f"corrected T(M)==Tfull? {r2['corrected_equals_Tfull']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
