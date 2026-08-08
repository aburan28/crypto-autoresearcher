#!/usr/bin/env python3
"""Reanalyze the prior volcano audit at its exact finite-density boundary."""
from __future__ import annotations
import hashlib, importlib.util, json, math, os, platform, sys, time
from pathlib import Path

RUN_ID = os.environ.get("ECDLP_RUN_ID", "RUN-ECDLP-122c4e-001")
OUT = Path(os.environ.get("ECDLP_OUT", "raw-result.json"))
SOURCE_ROOT = Path(os.environ.get("ECDLP_SOURCE_ROOT", ".")).resolve()
SOURCE_REL = {
    "specification.yaml": "experiments/EXP-ECDLP-03a8c9/specification.yaml",
    "run_volcano_audit.py": "experiments/EXP-ECDLP-03a8c9/runs/RUN-ECDLP-03a8c9-001/run_volcano_audit.py",
    "results.json": "experiments/EXP-ECDLP-03a8c9/runs/RUN-ECDLP-03a8c9-001/results.json",
    "manifest.yaml": "experiments/EXP-ECDLP-03a8c9/runs/RUN-ECDLP-03a8c9-001/manifest.yaml",
    "execution_report.yaml": "experiments/EXP-ECDLP-03a8c9/runs/RUN-ECDLP-03a8c9-001/execution_report.yaml",
}
EXPECTED = {
    "specification.yaml": "47382be1754a6c07e43e5cae92c9f14a88e19fc15a8cb93fa4194a07e8ed0d53",
    "run_volcano_audit.py": "e72da443c212a02a9ca12ebe5fff26df545c4bff353ec72f4245784d41f2a136",
    "results.json": "99286963dd515f09df7465cc6b9bc5b62c710c6c75e1b4105c1f9899c63887ef",
    "manifest.yaml": "e63a8267786013ea0dc90569abea453b82591e322b09c17d4e7cf81772a3e1cd",
    "execution_report.yaml": "67113b5f14a93a0699cb70089b270403edb62a5791d7f498d1380149a5cb7508",
}

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def load_source_module(path: Path):
    spec = importlib.util.spec_from_file_location("frozen_volcano_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen source module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main() -> dict:
    started = time.time()
    errors = []
    hashes = {}
    for name, rel in SOURCE_REL.items():
        p = SOURCE_ROOT / rel
        if not p.is_file():
            errors.append(f"missing source {rel}")
            continue
        hashes[name] = sha(p)
        if hashes[name] != EXPECTED[name]:
            errors.append(f"hash mismatch {name}: {hashes[name]} != {EXPECTED[name]}")
    if errors:
        out = {"run_id": RUN_ID, "valid": False, "validity_reason": errors, "source_hashes": hashes}
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=2) + "\n")
        return out
    src = load_source_module(SOURCE_ROOT / SOURCE_REL["run_volcano_audit.py"])
    prior = json.loads((SOURCE_ROOT / SOURCE_REL["results.json"]).read_text())
    summaries = prior["stages"]["stage2_treatment"]["per_curve_summary"]
    if len(summaries) != 60:
        raise RuntimeError(f"expected 60 summaries, got {len(summaries)}")
    B = 1_000_000
    lower_B = max(1, B // 1000)
    rows = []
    sparse_total = sparse_pass = 0
    lower_total = lower_pass = 0
    g3_exceed = g3_explained = 0
    g3_error_max = 0.0
    valid_deviations = []
    for summary in summaries:
        curve = {"p": int(summary["p"]), "t": int(summary["t"])}
        result = src.process_curve(curve, B)
        reported_g3 = float(summary["G3"])
        g3_error = abs(result["G3_excursion"] - reported_g3)
        g3_error_max = max(g3_error_max, g3_error)
        if g3_error > 1e-6:
            errors.append(f"G3 mismatch p={curve['p']}: {result['G3_excursion']} != {reported_g3}")
        sparse_levels = 0
        sparse_ok = 0
        normalized = []
        for level in result["level_data"]:
            abs_df = abs(int(level["D_f"]))
            sparse = 4 * B < abs_df
            if sparse:
                sparse_levels += 1; sparse_total += 1
                expected_rho = 2 * math.isqrt(B)
                if level["rho_f"] == expected_rho:
                    sparse_ok += 1; sparse_pass += 1
                else:
                    errors.append(f"sparse rho mismatch p={curve['p']} f={level['f']}")
            else:
                kap = level["kappa_num"] / level["kappa_den"]
                base = result["level_data"][0]["h_f"] * result["level_data"][0]["rho_f"]
                if base and kap:
                    normalized.append(abs((level["product"] / (base * kap)) - 1.0))
            lower_rho = src.rho_count(int(level["D_f"]), lower_B)
            if 4 * lower_B < abs_df:
                lower_total += 1
                if lower_rho == 2 * math.isqrt(lower_B):
                    lower_pass += 1
                else:
                    errors.append(f"lower-B sparse control mismatch p={curve['p']} f={level['f']}")
        if normalized:
            valid_deviations.extend(normalized)
        if result["G3_excursion"] > 4.0:
            g3_exceed += 1
            if sparse_levels == len(result["level_data"]):
                g3_explained += 1
        rows.append({"bits": summary["bits"], "p": curve["p"], "t": curve["t"],
                     "D_K": result["D_K"], "c": result["c"],
                     "levels": len(result["level_data"]), "sparse_levels": sparse_levels,
                     "sparse_identity_pass": sparse_ok == sparse_levels,
                     "g3_recomputed": result["G3_excursion"], "g3_reported": reported_g3,
                     "g3_exceeds_4": result["G3_excursion"] > 4.0,
                     "all_levels_sparse": sparse_levels == len(result["level_data"]),
                     "density_valid_normalized_max": max(normalized) if normalized else None})
    controls = {
        "source_hashes": not errors,
        "prior_g3_reproduction": g3_error_max <= 1e-6,
        "sparse_row_identity": sparse_total == sparse_pass,
        "lower_B_sparse_control": lower_total == lower_pass,
    }
    out = {"run_id": RUN_ID, "valid": not errors, "validity_reason": errors or "all checks passed",
           "source_hashes": hashes, "inputs": {"B": B, "lower_B": lower_B, "curve_count": len(rows)},
           "controls": controls, "metrics": {"sparse_level_count": sparse_total,
             "sparse_level_identity_pass_rate": sparse_pass / sparse_total if sparse_total else None,
             "prior_g3_exceedance_count": g3_exceed, "g3_exceedance_explained_rate": g3_explained / g3_exceed if g3_exceed else None,
             "density_valid_normalized_deviation_max": max(valid_deviations) if valid_deviations else None,
             "prior_g3_reproduction_max_abs_error": g3_error_max, "lower_B_control_pass_rate": lower_pass / lower_total if lower_total else None},
           "rows": rows, "scope": "60 prior ordinary prime-field toy summaries; no new curve generation or ECDLP solve",
           "elapsed_seconds": time.time() - started}
    if not all(controls.values()):
        out["valid"] = False
        out["validity_reason"] = {"errors": errors, "controls": controls}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out

if __name__ == "__main__":
    result = main(); print(json.dumps(result["metrics"], sort_keys=True))
    sys.exit(0 if result["valid"] else 2)

