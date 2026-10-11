#!/usr/bin/env python3
"""EXP-SSIQ-4ecc58 Stages 0-1: ordered-key holonomy census (Python dual-route).

Stage 0 freezes panel primes, N, S, thresholds, Cayley/iso twin fixtures.
Stage 1 measures H_N for first two p > 7^4 and N in {5,7}.

Observations only. No Magma/Sage/AUXIN/Bedrock. No isogeny walk. No attack.
No exponent claim. Crypto-size Deuring Stage 2 is NOT authorized.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from meters import (  # noqa: E402
    abelianisation_order,
    cayley_holonomy_zn,
    gl2_S_size,
    holonomy_both,
    index_gls,
    iso_checks,
    random_subgroup_same_order,
    rmax_from_ab,
    sl_cap,
)
from ntheory import (  # noqa: E402
    enumerate_order_elements,
    enumerate_spine_elements,
    integer_nth_root,
    miller_rabin,
    next_prime_3mod4,
    sl2_order,
    split_ij,
)

EXPERIMENT_ID = "EXP-SSIQ-4ecc58"
HYPOTHESIS_ID = "H-SSIQ-d724f2"
APPROVED_BY = "DEC-20261003-9f9c4f"
EXP_ROOT = Path(__file__).resolve().parents[1]

BIT_FLOORS = [1 << k for k in (10, 11, 12, 13, 14)]
N_PANEL = [5, 7]
S23 = [2, 3]
MAX_SUM = 12
COORD = 4
STAB_PREFIXES = [100, 200, 400]
NULL_SEED = 2026100303
P_GT_N4 = True


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = ["---"]
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif v is None:
            lines.append(f"{k}: null")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            s = str(v).replace('"', '\\"')
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


def panel_primes() -> list[int]:
    return [next_prime_3mod4(lo) for lo in BIT_FLOORS]


def stage1_cells(primes: list[int]) -> list[dict]:
    # First two panel primes (2^10, 2^11 floors) x N in {5,7}.
    # Readable iff p > N^4 (N=5 yes; N=7 reported unread).
    take = primes[:2]
    cells = []
    for p in take:
        for N in N_PANEL:
            cells.append(
                {
                    "id": f"p{p}_N{N}",
                    "p": p,
                    "N": N,
                    "S": list(S23),
                    "p_gt_N4": p > N**4,
                    "role": "census",
                }
            )
    return cells


def obligations() -> list[dict]:
    return [
        {
            "id": 1,
            "claim": "A key satisfying K1-K3 with isogeny-determined labels is path independent.",
            "nearby": "Must hold on Cayley Z/n (key g(x)=x).",
        },
        {
            "id": 2,
            "claim": "Path independence iff the key is trivial on holonomy H_N.",
            "nearby": "Must hold on the F_p-spine (abelian holonomy).",
        },
        {
            "id": 3,
            "claim": "H_N contains SL_2(Z/N) for p large against N (strong approximation; recalled).",
            "nearby": "Census index==1 is the measurement; not a proof of Kneser-Eichler.",
        },
        {
            "id": 4,
            "claim": "SL_2(Z/N) is perfect for N coprime to 6, so abelian keys factor through det=degree.",
            "nearby": "Must NOT prove the spine key is impossible.",
        },
        {
            "id": 5,
            "claim": "Degree-only alphabet is about X=p^{1/6} < M=p^{1/3}.",
            "nearby": "Arithmetic table; no sampling.",
        },
        {
            "id": 6,
            "claim": "Ordered merge with alphabet < M has superlinear false pairs.",
            "nearby": "Bookkeeping; not measured on this card.",
        },
        {
            "id": 7,
            "claim": "Streaming memory is O(M^{1/2}) when K1-K3 hold (Schroeppel-Shamir).",
            "nearby": "Cayley positive control; recalled four-list shape.",
        },
    ]


def run_stage0(run_dir: Path) -> dict:
    t0 = time.time()
    primes = panel_primes()
    if not all(miller_rabin(p) and p % 4 == 3 for p in primes):
        raise RuntimeError("panel primes failed MR or 3 mod 4")
    cells = stage1_cells(primes)
    cay = cayley_holonomy_zn(12, [1, 5])
    p_fix = primes[0]
    N_fix = 5
    split = split_ij(N_fix, p_fix)
    twin_ok = bool(cay["twin_ok"] and cay["abelian"] and cay["full"] and split is not None)
    iso = {}
    if split is not None:
        i_mat, j_mat = split
        elems = enumerate_order_elements(p_fix, MAX_SUM, COORD)
        iso = iso_checks(elems, N_fix, i_mat, j_mat)
        hol = holonomy_both(elems[:80], N_fix, i_mat, j_mat)
        twin_ok = twin_ok and hol["agree"] and iso["one_is_I"] and iso["det_bad"] == 0
        iso["hol_agree"] = hol["agree"]
        iso["|H_fix|"] = hol["|H|"]
        iso["n_elems"] = len(elems)
    fixtures = {
        "cayley_z12": cay,
        "iso_pN": {"p": p_fix, "N": N_fix, **iso},
        "proves_too_much": {
            "PTM-CAYLEY": "A derivation that forbids the Cayley/spine key is wrong.",
            "PTM-RANDOM": "A derivation that still produces a key on a random regular graph (no covering) proves too much.",
        },
        "obligations": obligations(),
    }
    predictions = {
        "schema": "crypto.autoresearch.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "frozen_at_stage": 0,
        "formula": "E-CLOSED iff index[GL2_S:H_N]==1 and | (H_N cap SL2)^ab |==1 for every Stage-1 cell with p>N^4 and N in {5,7}",
        "bit_floors": BIT_FLOORS,
        "panel_primes": primes,
        "N_panel": N_PANEL,
        "S": S23,
        "max_sum": MAX_SUM,
        "coord": COORD,
        "stab_prefixes": STAB_PREFIXES,
        "null_seed": NULL_SEED,
        "cells": cells,
        "stage2_authorized": False,
        "crypto_deuring_authorized": False,
        "exponent_moved": False,
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage0" / "preregistered-predictions.json", predictions)
    write_json(EXP_ROOT / "stage0" / "fixtures.json", fixtures)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "outcome": "O-STAGE0-OK" if twin_ok else "O-ARTIFACT",
        "twin_ok": twin_ok,
        "fixtures_ok": twin_ok,
        "panel_primes": primes,
        "n_stage1_cells": len(cells),
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 0,
            "run_dir": str(run_dir),
            "outcome": raw["outcome"],
            "twin_ok": twin_ok,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def _measure_cell(p: int, N: int, rng: random.Random) -> dict:
    split = split_ij(N, p)
    if split is None:
        return {"artifact": "no_split", "p": p, "N": N}
    i_mat, j_mat = split
    elems = sorted(enumerate_order_elements(p, MAX_SUM, COORD), key=lambda t: (t[4], t[0], t[1], t[2], t[3]))
    hol = holonomy_both(elems, N, i_mat, j_mat)
    iso = iso_checks(elems, N, i_mat, j_mat)
    flags = list(hol["flags"]) + list(iso["flags"])
    if not hol["agree"]:
        flags.append("twin_H")
    if iso["det_bad"]:
        flags.append("det_ne_nrd")
    H = hol["H_a"]
    Hsl = sl_cap(H, N)
    ab = abelianisation_order(Hsl, N)
    idx = index_gls(H, N, S23)
    rmax = rmax_from_ab(H, N)
    M = integer_nth_root(p, 3)
    # stabilisation
    stab = []
    sizes = []
    for k in STAB_PREFIXES:
        k_eff = min(k, len(elems))
        hk = holonomy_both(elems[:k_eff], N, i_mat, j_mat)
        stab.append({"k": k, "k_eff": k_eff, "|H|": hk["|H|"], "agree": hk["agree"]})
        sizes.append((k_eff, hk["|H|"]))
    by_eff = {}
    for k_eff, sz in sizes:
        by_eff.setdefault(k_eff, set()).add(sz)
    undetermined = any(len(v) > 1 for v in by_eff.values()) or len({sz for _, sz in sizes}) > 1
    spine_e = sorted(enumerate_spine_elements(p, MAX_SUM, COORD), key=lambda t: (t[4], t[0], t[2]))
    sh = holonomy_both(spine_e, N, i_mat, j_mat)
    spine_ab = abelianisation_order(sl_cap(sh["H_a"], N), N) if sh["agree"] else None
    # spine holonomy should be abelian: |H| == |H_ab| roughly — check derived trivial on whole H
    spine_abelian = False
    if sh["agree"] and sh["H_a"]:
        from meters import derived_subgroup

        der = derived_subgroup(sh["H_a"], N)
        spine_abelian = der <= {mid_el(N)} or len(der) == 1
    null = random_subgroup_same_order(len(H), N, rng)
    null_ab = None
    if null is not None:
        null_ab = abelianisation_order(sl_cap(null, N), N)
    return {
        "p": p,
        "N": N,
        "p_gt_N4": p > N**4,
        "n_elems": len(elems),
        "n_gens": hol["n_gens"],
        "|H|": hol["|H|"],
        "|H_cap_SL|": len(Hsl),
        "|SL2|": sl2_order(N),
        "|GL2_S|": gl2_S_size(N, S23),
        "index": idx,
        "ab_sl": ab,
        "R_max": rmax,
        "M_cbrt_p": M,
        "R_max_lt_M": (rmax is not None and rmax < M),
        "twin_ok": hol["agree"],
        "iso_ok": iso["one_is_I"] and iso["det_bad"] == 0,
        "stab": stab,
        "undetermined": undetermined,
        "spine_|H|": sh["|H|"],
        "spine_twin_ok": sh["agree"],
        "spine_abelian": spine_abelian,
        "spine_ab_sl": spine_ab,
        "null_|H|": None if null is None else len(null),
        "null_ab_sl": null_ab,
        "artifact_flags": flags,
        "contains_SL2": hol["|H|"] >= sl2_order(N) and len(Hsl) == sl2_order(N),
    }


def mid_el(n: int):
    from ntheory import mid

    return mid(n)


def run_stage1(run_dir: Path) -> dict:
    t0 = time.time()
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    fix_path = EXP_ROOT / "stage0" / "fixtures.json"
    if not pred_path.is_file() or not fix_path.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "reason": "missing Stage-0 freeze",
            "claims": {"break": False, "exponent_move": False},
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {"experiment_id": EXPERIMENT_ID, "stage": 1, "outcome": "O-IMPEDIMENT", "amazon_bedrock": "NOT_USED"},
        )
        return raw
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    fixtures = json.loads(fix_path.read_text(encoding="utf-8"))
    rng = random.Random(NULL_SEED)
    artifact_flags: list[str] = []
    panels: dict[str, Any] = {}
    control_rows: list[dict[str, Any]] = []
    cay = fixtures.get("cayley_z12") or {}
    control_rows.append({"control": "cayley_z12", **{k: cay.get(k) for k in ("abelian", "full", "twin_ok", "order")}})
    if not cay.get("abelian") or not cay.get("full"):
        artifact_flags.append("cayley_fail")
    iso = fixtures.get("iso_pN") or {}
    control_rows.append({"control": "iso_one_I", "one_is_I": iso.get("one_is_I"), "det_bad": iso.get("det_bad")})
    if iso.get("one_is_I") is False or iso.get("det_bad"):
        artifact_flags.append("iso_fail")

    for cell in pred.get("cells") or []:
        cid = cell["id"]
        p, N = int(cell["p"]), int(cell["N"])
        row = _measure_cell(p, N, rng)
        panels[cid] = row
        control_rows.append(
            {
                "control": "spine",
                "cell": cid,
                "spine_abelian": row.get("spine_abelian"),
                "spine_twin_ok": row.get("spine_twin_ok"),
            }
        )
        if row.get("artifact"):
            artifact_flags.append(f"{cid}_{row['artifact']}")
        if not row.get("twin_ok", True):
            artifact_flags.append(f"{cid}_twin")
        if not row.get("iso_ok", True):
            artifact_flags.append(f"{cid}_iso")
        if row.get("spine_abelian") is False:
            artifact_flags.append(f"{cid}_spine_nonabelian")
        if row.get("undetermined"):
            artifact_flags.append(f"{cid}_undetermined")
        artifact_flags.extend(f"{cid}_{f}" for f in (row.get("artifact_flags") or [])[:8])

    readable = [
        v
        for v in panels.values()
        if v.get("p_gt_N4") and not v.get("undetermined") and v.get("twin_ok") and v.get("iso_ok")
    ]
    if artifact_flags and any(
        x.endswith("_spine_nonabelian") or x.endswith("_twin") or x.endswith("_iso") or "no_split" in x
        for x in artifact_flags
    ):
        outcome = "O-ARTIFACT"
    elif not readable:
        outcome = "O-INCONCLUSIVE"
    else:
        closed_hits = []
        open_hits = []
        for v in readable:
            idx = v.get("index")
            ab = v.get("ab_sl")
            if idx == 1 and ab == 1:
                closed_hits.append(True)
            elif idx is not None and (idx > 1) and (ab is not None and ab > 1):
                open_hits.append(True)
            elif idx == 1 and ab is not None and ab > 1:
                # extra abelian quotient of SL despite index 1
                open_hits.append(True)
            else:
                closed_hits.append(False)
        if open_hits:
            outcome = "O-OPEN"
        elif all(closed_hits) and closed_hits:
            outcome = "O-CLOSED"
        else:
            outcome = "O-MIXED"

    write_json(EXP_ROOT / "stage1" / "panels.json", panels)
    write_json(EXP_ROOT / "stage1" / "control-table.json", {"rows": control_rows, "artifact_flags": artifact_flags})
    results = "\n".join(
        [
            "# RESULTS EXP-SSIQ-4ecc58 Stages 0-1",
            "",
            f"outcome: {outcome}",
            f"hypothesis: {HYPOTHESIS_ID}",
            f"approved_by: {APPROVED_BY}",
            "",
            "Exactly one O-* label. Holonomy census. No exponent claim.",
            "Amazon Bedrock: NOT_USED. Magma/Sage: not used.",
            "",
            f"artifact_flags: {artifact_flags}",
            f"panels: {json.dumps({k: {'|H|': v.get('|H|'), 'index': v.get('index'), 'ab_sl': v.get('ab_sl'), 'R_max': v.get('R_max')} for k,v in panels.items()})}",
            "",
        ]
    )
    write_text(EXP_ROOT / "RESULTS.md", results)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "outcome": outcome,
        "artifact_flags": artifact_flags,
        "n_readable": len(readable),
        "panels_summary": {
            k: {
                "|H|": v.get("|H|"),
                "index": v.get("index"),
                "ab_sl": v.get("ab_sl"),
                "R_max": v.get("R_max"),
            }
            for k, v in panels.items()
        },
        "claims": {"break": False, "exponent_move": False},
        "amazon_bedrock": "NOT_USED",
        "wall_clock_seconds": time.time() - t0,
        "pred_n_cells": len(pred.get("cells") or []),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "run_dir": str(run_dir),
            "outcome": outcome,
            "amazon_bedrock": "NOT_USED",
        },
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(args.trial_plan).read_text(encoding="utf-8"))
    if plan.get("experiment_id") != EXPERIMENT_ID:
        print("trial-plan experiment_id mismatch", file=sys.stderr)
        return 2
    if args.stage == 0:
        raw = run_stage0(run_dir)
    else:
        raw = run_stage1(run_dir)
    print(json.dumps({"outcome": raw.get("outcome"), "stage": args.stage}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
