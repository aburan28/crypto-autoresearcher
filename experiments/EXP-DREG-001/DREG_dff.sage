# DREG_dff.sage -- EXP-DREG-001 first-fall-degree (d_ff) ladder driver.
#
# Measures d_ff(n, ti) for the boolean chained Semaev m=3 system (sem arm) and
# the T11 support-matched null (null arm), max_D=6, >=8 targets per n, exactly
# per the EXP-DREG-001 secondary metric ("d_ff(n) with max_D=6").
#
# Method: identical algorithm to src/ic_first_fall_fast.py::first_fall_degree
# (degree-<=D boolean Macaulay rows, GF(2) sparse echelon, first D whose row
# space contains a degree-<=1 polynomial), reimplemented monoset-native so both
# arms (sem monosets and boolean_null monosets) go through one code path.
# Systems come from src/h012_peel_rank.py::build_system (same generators and
# seeds as the h012 series: seed0=2026, rng = Random(seed0 + 1000*ti + n)).
#
# Per-target wall cap: a target whose current D-level exceeds the cap is
# recorded as censored (d_ff null), never as evidence (AGENTS rule 5).
#
# Run:
#   sage experiments/EXP-DREG-001/DREG_dff.sage --n-list 12 --targets 8 \
#        --which both --max-D 6 --per-target-cap 90 \
#        --out experiments/EXP-DREG-001/runs/RUN-DREG-001-DFF-N12/raw-result.json

import sys, os, time, json, signal, argparse
from pathlib import Path

WS = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WS / "src"))

from sage.all import GF, Matrix
from h012_peel_rank import build_system, boolean_null, semireg_rank_pred
from ic_first_fall_fast import mono_deg, multiply


class _Cap(Exception):
    pass


def _alarm(signum, frame):
    raise _Cap()


def first_fall_monosets(polys, nvars, max_D):
    """Monoset-native copy of ic_first_fall_fast.first_fall_degree.
    Returns (d_ff, n_rows, n_cols) or (None, rows_attempted, None)."""
    polys = [f for f in polys if f]
    for D in range(2, max_D + 1):
        rows = []
        col_index = {}

        def col_of(mono):
            if mono not in col_index:
                col_index[mono] = len(col_index)
            return col_index[mono]

        from itertools import combinations
        for f in polys:
            fdeg = max((mono_deg(m) for m in f), default=0)
            if fdeg > D:
                continue
            max_mult = D - fdeg
            mults = [frozenset()]
            for md in range(1, max_mult + 1):
                for combo in combinations(range(nvars), md):
                    mults.append(frozenset(combo))
            for mu in mults:
                prod = multiply(f, mu)
                if not prod:
                    continue
                if max(mono_deg(m) for m in prod) > D:
                    continue
                rows.append(set(col_of(m) for m in prod))
        if not rows:
            continue
        ncols = len(col_index)
        M = Matrix(GF(2), len(rows), ncols, sparse=True)
        for ri, row in enumerate(rows):
            for c in row:
                M[ri, c] = 1
        M = M.echelon_form()
        deg_le1_cols = set(c for mono, c in col_index.items() if mono_deg(mono) <= 1)
        for row in M.rows():
            nz = row.nonzero_positions()
            if not nz:
                continue
            if all(c in deg_le1_cols for c in nz):
                return D, len(rows), ncols
    return None, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-list", default="12")
    ap.add_argument("--t", type=int, default=3)
    ap.add_argument("--targets", type=int, default=8)
    ap.add_argument("--max-D", type=int, default=6)
    ap.add_argument("--which", default="both", choices=["sem", "null", "both"])
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--per-target-cap", type=float, default=90.0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rec = {"experiment": "EXP-DREG-001 d_ff ladder",
           "driver": "DREG_dff.sage (monoset-native ic_first_fall_fast algorithm)",
           "t": int(args.t), "max_D": int(args.max_D), "seed": int(args.seed),
           "targets": int(args.targets),
           "per_target_cap_s": float(args.per_target_cap), "runs": []}

    signal.signal(signal.SIGALRM, _alarm)

    arms = ["sem", "null"] if args.which == "both" else [args.which]
    for n in [int(x) for x in args.n_list.split(",")]:
        for ti in range(args.targets):
            t0 = time.time()
            built = build_system(n, args.t, ti, args.seed)
            if built is None:
                rec["runs"].append({"n": n, "ti": ti, "arm": None,
                                    "status": "invalid",
                                    "reason": "build_system failed (no decomposable R)"})
                continue
            rng, nb, sem_monosets, eq_degs = built
            build_s = time.time() - t0
            pred, HF = semireg_rank_pred(eq_degs, nb, args.max_D + 1)
            for arm in arms:
                monosets = sem_monosets if arm == "sem" else boolean_null(sem_monosets, nb, rng)
                entry = {"n": n, "ti": ti, "arm": arm, "nb": nb,
                         "n_eqs": len(monosets),
                         "eq_degs_hist": {str(d): eq_degs.count(d) for d in sorted(set(eq_degs))},
                         "sr_pred_maxD": int(pred[args.max_D]),
                         "build_s": float(round(build_s, 2))}
                signal.setitimer(signal.ITIMER_REAL, args.per_target_cap)
                t1 = time.time()
                try:
                    d_ff, nr, nc = first_fall_monosets(monosets, nb, args.max_D)
                    entry.update({"status": "resolved", "d_ff": d_ff,
                                  "last_D_rows": nr, "last_D_cols": nc,
                                  "ff_s": float(round(time.time() - t1, 2))})
                except _Cap:
                    entry.update({"status": "censored",
                                  "reason": f"per-target cap {args.per_target_cap}s",
                                  "d_ff": None,
                                  "ff_s": float(round(time.time() - t1, 2))})
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                rec["runs"].append(entry)
                with open(out_path, "w") as fh:
                    json.dump(rec, fh, indent=1)
                print(f"[dff n={n} ti={ti} {arm}] {entry['status']} "
                      f"d_ff={entry.get('d_ff')} ({entry.get('ff_s', 0)}s)", flush=True)
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
