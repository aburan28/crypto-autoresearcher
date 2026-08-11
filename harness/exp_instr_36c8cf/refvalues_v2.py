"""CONTRACT VERSION 2 reference readers for EXP-INSTR-36c8cf.

experiments/EXP-INSTR-36c8cf/amendments/v1.yaml took the frozen contract from
version 1 to version 2. This module is ADDITIVE beside `refvalues.py`, which is
left exactly as the version-1 run RUN-INSTR-36c8cf-phaseA-2a5cd1 left it so that
run's code path stays re-executable and its pinned hashes stay valid.

NO TRANSCRIBED REFERENCE VALUES (invalidation rule; EXP-ICINV-4d33aa amendment
v2 change A4; CORR-20260807-a24675). Every frozen number used by the run --
including every number the amendment itself freezes -- is READ FROM ITS RECORD
AT RUN TIME here and returned together with the sha256 of the file it was read
from. Nothing below carries a reference literal.
"""
from __future__ import annotations

import os
import re

import yaml

from harness.exp_instr_36c8cf.refvalues import REPO, sha256_of, _text  # noqa: F401

INSTR_SPEC = "experiments/EXP-INSTR-36c8cf/specification.yaml"
INSTR_AMENDMENT_V1 = "experiments/EXP-INSTR-36c8cf/amendments/v1.yaml"
ICINV_SPEC = "experiments/EXP-ICINV-4d33aa/specification.yaml"


def _load(rel: str):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --------------------------------------------------------------------------
# the amendment's frozen parameters, parsed from the amendment itself
# --------------------------------------------------------------------------


def amendment_frozen_parameters() -> dict:
    """Every number change G1/G2/G3/G5 freezes, READ from amendments/v1.yaml.

    The amendment states its coverage both as a decimal and as an EXACT
    FRACTION; the exact fraction is what this reader returns and what the run
    computes with, so no rounding of a frozen parameter can enter through this
    path. The decimal is returned beside it only so a reader can see that the
    two agree.
    """
    doc = _load(INSTR_AMENDMENT_V1)["protocol_amendment"]
    changes = {c["id"]: c for c in doc["changes"]}

    g2 = changes["G2"]["to"]

    def _num(field: str) -> float:
        m = re.search(rf"{field}\s*:\s*([0-9.]+)", g2)
        if not m:
            raise RuntimeError(f"amendment G2 does not declare {field}")
        return float(m.group(1))

    def _frac(field: str) -> tuple[int, int]:
        m = re.search(rf"{field}\s*:\s*[0-9.]+\s*\(exact fraction (\d+)/(\d+)", g2)
        if not m:
            raise RuntimeError(f"amendment G2 does not declare {field} as an exact fraction")
        return int(m.group(1)), int(m.group(2))

    n_rows = int(_num("number_of_density_rows_gated"))
    lo_num, lo_den = _frac("lower_quantile_of_the_interval")
    hi_num, hi_den = _frac("upper_quantile_of_the_interval")
    cov_num, cov_den = _frac("per_row_central_coverage")
    alpha_num, alpha_den = _frac("per_row_two_sided_alpha")

    g3 = changes["G3"]["to"]
    # E2 seed rungs and the two extension seed ranges.
    rungs = [int(x) for x in re.search(
        r"E2\..*?(\d+),\s*then\s*(\d+),\s*then\s*(\d+)\.", g3, re.S).groups()]
    rung2_lo, rung2_hi = (int(x) for x in re.search(
        r"Rung 2 adds\s+seeds\s+(\d+)\s+to\s+(\d+)\s+inclusive", g3, re.S).groups())
    rung3_lo, rung3_hi = (int(x) for x in re.search(
        r"Rung 3 adds\s+seeds\s+(\d+)\s+to\s+(\d+)\s+inclusive", g3, re.S).groups())
    stability_pct = float(re.search(
        r"half-width\s+changes\s+by\s+less\s+than\s+(\d+(?:\.\d+)?)%\s+relative", g3, re.S).group(1))

    g5 = changes["G5"]["to"]
    d1_rows = [int(x) for x in re.search(r"\{([0-9,\s]+)\}", g5).group(1).split(",")]
    d1_T = int(re.search(r"target\s+count\s+T\s*=\s*(\d+)", g5).group(1))

    g1 = changes["G1"]["to"]
    median_p_tol = float(re.search(
        r"absolute\s+difference\s+of\s+median\s+p\s+at\s+most\s+(\d+(?:\.\d+)?)",
        g1, re.S).group(1))
    pct_decimals = re.search(
        r"published\s+precision\s+of\s+(\w+)\s+decimal\s+place", g1, re.S).group(1)

    return {
        "source_path": INSTR_AMENDMENT_V1,
        "source_sha256": sha256_of(INSTR_AMENDMENT_V1),
        "amendment_ordinal": doc["amendment_ordinal"],
        "version_from": doc["version_from"],
        "version_to": doc["version_to"],
        "approved_by": doc["approved_by"],
        "approved_at": str(doc["approved_at"]),
        "recorded_by_decision": doc["recorded_by_decision"],
        # G2
        "number_of_density_rows_gated": n_rows,
        "family_wise_error_target": _num("family_wise_error_target"),
        "per_row_two_sided_alpha_fraction": [alpha_num, alpha_den],
        "per_row_two_sided_alpha": alpha_num / alpha_den,
        "per_row_central_coverage_fraction": [cov_num, cov_den],
        "per_row_central_coverage": cov_num / cov_den,
        "lower_quantile_fraction": [lo_num, lo_den],
        "upper_quantile_fraction": [hi_num, hi_den],
        "lower_quantile": lo_num / lo_den,
        "upper_quantile": hi_num / hi_den,
        "realised_family_wise_error_as_declared": _num("realised_family_wise_error"),
        "declared_decimals_for_audit": {
            "per_row_two_sided_alpha": _num("per_row_two_sided_alpha"),
            "per_row_central_coverage": _num("per_row_central_coverage"),
            "lower_quantile_of_the_interval": _num("lower_quantile_of_the_interval"),
            "upper_quantile_of_the_interval": _num("upper_quantile_of_the_interval"),
        },
        # G3
        "seed_rungs": rungs,
        "rung2_extension_seed_range": [rung2_lo, rung2_hi],
        "rung3_extension_seed_range": [rung3_lo, rung3_hi],
        "stability_relative_half_width_pct": stability_pct,
        # G5 D1
        "d1_density_rows": d1_rows,
        "d1_target_count": d1_T,
        # G1
        "sr1_median_p_abs_tolerance": median_p_tol,
        "sr1_pct_of_mean_published_precision_decimals": pct_decimals,
    }


def instr_declared_seeds() -> dict:
    """The twelve contract seeds (replication.seeds), read from the contract."""
    spec = _load(INSTR_SPEC)["experiment"]
    return {"source_path": INSTR_SPEC, "source_sha256": sha256_of(INSTR_SPEC),
            "seeds": list(spec["replication"]["seeds"])}


def icinv_frozen_grid() -> dict:
    """The thirteen frozen density rows and T, CITED from the contract that owns
    them (EXP-ICINV-4d33aa inputs.parameters), which is what amendment change
    G5/D1 says they are cited from."""
    spec = _load(ICINV_SPEC)["experiment"]
    par = spec["inputs"]["parameters"]
    return {
        "source_path": ICINV_SPEC,
        "source_sha256": sha256_of(ICINV_SPEC),
        "factor_base_sizes": list(par["factor_base_sizes"]),
        "target_count_primary": par["target_count_primary"],
        "operating_density_target": par["operating_density_target"],
        "primes_required": list(par["primes_required"]),
        "seeds_of_that_contract": list(par["seeds"]),
    }


def sr3v3_reference_runs() -> dict:
    """THE REFERENCE RUNS THE REDESIGNED GATE COMPARES AGAINST, NAMED EXPLICITLY.

    Identified from the COMMITTED harness module that implements EXP-ICINV-4d33aa
    contract version 2 -- `harness.exp_icinv_fullgroup.BASELINE_RUNS_V2`, set by
    that contract's amendment v2 change A1 -- and then READ from each run's own
    record via that module's own `read_baseline_record`, which hashes both
    raw-result.json and manifest.yaml. No run id and no number is transcribed
    here.
    """
    from harness import exp_icinv_fullgroup as fg
    out = {
        "identified_from": {
            "module": "harness/exp_icinv_fullgroup.py",
            "symbol": "BASELINE_RUNS_V2",
            "sha256": sha256_of("harness/exp_icinv_fullgroup.py"),
            "why": ("EXP-ICINV-4d33aa amendment v2 change A1 fixes these as the "
                    "SR3 reference sweeps; the map lives in the committed module "
                    "that implements that contract, and every number is read "
                    "from the referenced run record rather than from the map."),
        },
        "baseline_primes_declared_by_that_module": list(fg.BASELINE_PRIMES),
        "runs": {},
    }
    for p, (exp_id, run_id) in sorted(fg.BASELINE_RUNS_V2.items()):
        rec = fg.read_baseline_record(exp_id, run_id)
        if rec is None:
            raise FileNotFoundError(f"reference run {run_id} not found")
        # the command that produced it, read from its own manifest
        man = _load(os.path.join("experiments", exp_id, "runs", run_id,
                                 "manifest.yaml"))["run"]
        rec["declared_command"] = man["code"]["command"]
        rec["declared_status"] = man["status"]
        rec["prime"] = p
        out["runs"][str(p)] = rec
    return out
