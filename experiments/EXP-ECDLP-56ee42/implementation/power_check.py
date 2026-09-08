#!/usr/bin/env python3
"""C2a synthetic power check (V3-RA-2 as pinned by V4-CHG-6; budget/invocation
split per V5-CHG-2; RC-3 reuse per DEC-20260908-a491ff).

For each rung (T17-T25; T27 NOT-COMPUTED per the v3 carve-out) and each
repetition rep in 0..N-1:
  1. Synthesize a NULL placement of m0 fiber-0 (value 0) and m1 fiber-1
     (value 1) values at uniformly random positions (seed_placement).
  2. Pre-shuffle baseline A_noDC (the ratio's denominator).
  3. 8 genuine full-shuffle draws (seed_genuine): max ratio.
  4. 8 reading-2 broken-shuffle draws (seed_reading2): min ratio.
     Reading 2 (binary statistic, V3-CHG-3): fix exactly ONE arbitrary
     maximum-tied (fiber-1) position, freely permute every other position.
     Reading 1 (fix ALL max-tied) is degenerate for a binary statistic
     (identical to the no-op), so it is reported as ratio = 1.0 exactly,
     not simulated.
  5. Separation in this repetition iff
         max(genuine ratio) < min(reading-2 ratio) - 0.05.
C2a is BLOCKING iff separation holds in ALL N repetitions at EVERY rung
actually computed; otherwise DIAGNOSTIC ONLY.

Modes:
  --time-only   V5-RA-2: time ONE full repetition (17 FFTs) at each of
                 T17-T25 on the production infrastructure, extrapolate the
                 aggregate cost for the full N schedule under the required
                 invocation split, and print the regime decision inputs.
  --full --n N  Run the full N-repetition schedule and write
                 power_check_results.yaml.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

EXP_ROOT = Path(__file__).resolve().parent.parent
CACHE = EXP_ROOT / "runs" / "stage-cache"
BASE = 0x56EE42

# Frozen ladder (T, p, N).  rung_idx per the frozen ladder order.
LADDER = [(17, 131101, 131113), (19, 524309, 525361), (21, 2097169, 2098321),
          (23, 8388617, 8391797), (25, 33554473, 33557891),
          (27, 134217757, 134234689)]
RUNG_IDX = {T: i for i, (T, _, _) in enumerate(LADDER)}
COMPUTED_RUNGS = [17, 19, 21, 23, 25]   # T27 NOT-COMPUTED (v3 carve-out)

# V4-CHG-6 seed schedule (disjoint namespaces from the real NULL-2 range).
def seed_placement(rep, rung_idx):
    return BASE + 90000 + 1000 * rep + 10 * rung_idx

def seed_genuine(rep, rung_idx, draw_idx):
    return BASE + 190000 + 1000 * rep + 10 * rung_idx + draw_idx

def seed_reading2(rep, rung_idx, draw_idx):
    return BASE + 290000 + 1000 * rep + 10 * rung_idx + draw_idx


def a_nodc(n: int, v: np.ndarray) -> float:
    """A_noDC: largest non-DC Fourier coefficient magnitude, / n."""
    V = np.fft.fft(v)
    return float(np.max(np.abs(V[1:])) / n)


def genuine_shuffle(v: np.ndarray, seed: int) -> np.ndarray:
    """NULL-2: full random permutation of the values (multiset-preserving)."""
    rng = np.random.default_rng(seed & 0xFFFFFFFFFFFFFFFF)
    return v[rng.permutation(len(v))]


def reading2_shuffle(v: np.ndarray, seed: int) -> np.ndarray:
    """Reading 2 (binary statistic, V3-CHG-3): fix exactly ONE arbitrary
    maximum-tied (value-1) position, freely permute every other position."""
    n = len(v)
    ones = np.where(v == 1)[0]
    if len(ones) == 0:
        return v.copy()
    fixed = int(ones[0])
    other = np.array([i for i in range(n) if i != fixed], dtype=np.int64)
    rng = np.random.default_rng(seed & 0xFFFFFFFFFFFFFFFF)
    vals = v[other]
    v_new = v.copy()
    v_new[other] = vals[rng.permutation(len(other))]
    return v_new


def fiber_counts(T: int, p: int, N: int) -> tuple[int, int]:
    """Exact per-rung comparator (top_bit_fiber) fiber counts over the N
    subgroup points, from the stage-cache x-coordinates (V3-RA-1 data).
    top_bit_fiber(x, p) = 1 iff x >= 2^(p.bit_length()-1)."""
    xs = np.load(CACHE / f"rung_T{T}_x.npy")
    top = 1 << (p.bit_length() - 1)
    m1 = int(np.sum(xs >= top))
    m0 = int(N - m1)
    return m0, m1


def one_repetition(n: int, m0: int, m1: int, rep: int, rung_idx: int,
                   time_only: bool = False) -> dict:
    """One full repetition (17 FFTs): 1 pre-shuffle baseline + 8 genuine +
    8 reading-2.  Returns the per-draw ratios and the separation verdict."""
    t0 = time.time()
    rng = np.random.default_rng(seed_placement(rep, rung_idx) & 0xFFFFFFFFFFFFFFFF)
    v = np.zeros(n, dtype=np.float64)
    v[:m1] = 1.0
    v_placed = v[rng.permutation(n)]
    A_pre = a_nodc(n, v_placed)
    genuine = []
    for d in range(8):
        v_s = genuine_shuffle(v_placed, seed_genuine(rep, rung_idx, d))
        genuine.append(a_nodc(n, v_s) / A_pre)
    reading2 = []
    for d in range(8):
        v_s = reading2_shuffle(v_placed, seed_reading2(rep, rung_idx, d))
        reading2.append(a_nodc(n, v_s) / A_pre)
    dt = time.time() - t0
    max_g = max(genuine)
    min_r2 = min(reading2)
    separated = max_g < min_r2 - 0.05
    return {
        "A_noDC_pre": A_pre,
        "genuine_ratios": genuine,
        "reading2_ratios": reading2,
        "reading1_ratio": 1.0,  # degenerate for binary: identical to no-op
        "max_genuine": max_g,
        "min_reading2": min_r2,
        "separated": separated,
        "seconds": dt,
    }


def time_only() -> int:
    print("=== V5-RA-2: production timing, one full repetition (17 FFTs) ===")
    print("(uses V3-RA-1's exact per-rung fiber counts; the rep-0 result is")
    print(" saved for RC-3 reuse as repetition 0 of the full schedule, same seed)")
    print(f"{'rung':>5} {'n':>12} {'m1':>6} {'1 rep (s)':>12} {'x20 (s)':>12} {'x10 (s)':>12}")
    per_rung = {}
    rep0 = {}
    for T in COMPUTED_RUNGS:
        _, p, n = next(r for r in LADDER if r[0] == T)
        m0, m1 = fiber_counts(T, p, n)
        r = one_repetition(n, m0, m1, rep=0, rung_idx=RUNG_IDX[T])
        dt = r["seconds"]
        per_rung[T] = dt
        rep0[f"T{T}"] = {
            "m0": m0, "m1": m1,
            "A_noDC_pre": r["A_noDC_pre"],
            "max_genuine": r["max_genuine"],
            "min_reading2": r["min_reading2"],
            "separated": r["separated"],
            "seed_placement": seed_placement(0, RUNG_IDX[T]),
        }
        print(f"T{T:<4} {n:>12} {m1:>6} {dt:>12.4f} {dt*20:>12.2f} {dt*10:>12.2f}")
    # Save rep-0 for RC-3 reuse (same seed, same m0/m1 as the full schedule).
    (EXP_ROOT / "runs" / "power_check_rep0.json").write_text(
        json.dumps(rep0, indent=2) + "\n")
    # Invocation split: INVOCATION 1 = {T17,T19,T21,T23}, INVOCATION 2 = {T25}.
    inv1_20 = sum(per_rung[T] for T in [17, 19, 21, 23]) * 20
    inv2_20 = per_rung[25] * 20
    inv1_10 = sum(per_rung[T] for T in [17, 19, 21, 23]) * 10
    inv2_10 = per_rung[25] * 10
    grand_20 = inv1_20 + inv2_20
    grand_10 = inv1_10 + inv2_10
    print()
    print(f"INVOCATION 1 {{T17,T19,T21,T23}}: x20={inv1_20:.1f}s  x10={inv1_10:.1f}s")
    print(f"INVOCATION 2 {{T25}}:            x20={inv2_20:.1f}s  x10={inv2_10:.1f}s")
    print(f"Grand total T17-T25:            x20={grand_20:.1f}s "
          f"({grand_20/3600:.4f} CPU-h)   x10={grand_10:.1f}s ({grand_10/3600:.4f} CPU-h)")
    print()
    # Regime decision (V5-CHG-2 stopping_rule_and_fallback):
    #   N=20 proceeds iff grand_20 <= 4 CPU-h (80% of 5 CPU-h) AND each
    #   invocation <= 7200s.  Else N=10 iff grand_10 <= 4 CPU-h AND each
    #   invocation <= 7200s.  Else STOP.
    four_cpu_h = 4 * 3600
    n20_ok = (grand_20 <= four_cpu_h and inv1_20 <= 7200 and inv2_20 <= 7200)
    n10_ok = (grand_10 <= four_cpu_h and inv1_10 <= 7200 and inv2_10 <= 7200)
    if n20_ok:
        regime = "N=20 proceeds"
    elif n10_ok:
        regime = "N=10 fallback triggered"
    else:
        regime = "STOP-infrastructure-budget triggered"
    print(f"REGIME DECISION (pre-registered rule): {regime}")
    print(f"  N=20 fits 4-CPU-h & 7200s/invocation: {n20_ok}")
    print(f"  N=10 fits 4-CPU-h & 7200s/invocation: {n10_ok}")
    return 0


def full(n_reps: int) -> int:
    out = {
        "record": "power_check_results",
        "experiment": "EXP-ECDLP-56ee42",
        "task": "TASK-20260908-d54138",
        "method": "V3-RA-2 as pinned by V4-CHG-6; invocation split per V5-CHG-2",
        "n_repetitions": n_reps,
        "pass_fraction_required": f"{n_reps}/{n_reps} (100% unanimity)",
        "separation_criterion": "max(genuine ratio) < min(reading-2 ratio) - 0.05",
        "t27": "NOT-COMPUTED (v3 carve-out; memory ceiling)",
        "rc3_reuse": ("Each rung's single V5-RA-2 confirmation repetition is "
                      "REUSED as repetition 0 of this schedule, same seed "
                      "(rep=0 of the V4-CHG-6 seed_schedule); it is not a "
                      "discarded measurement."),
        "rungs": {},
    }
    # RC-3 reuse: rep 0 is the V5-RA-2 confirmation repetition (same seed,
    # same m0/m1), saved by --time-only.  Reuse it; run reps 1..N-1 fresh.
    rep0_path = EXP_ROOT / "runs" / "power_check_rep0.json"
    rep0 = json.loads(rep0_path.read_text()) if rep0_path.exists() else {}

    all_separated = True
    for T in COMPUTED_RUNGS:
        p, N = next((r[1], r[2]) for r in LADDER if r[0] == T)
        m0, m1 = fiber_counts(T, p, N)
        rung_idx = RUNG_IDX[T]
        reps = []
        for rep in range(n_reps):
            if rep == 0 and f"T{T}" in rep0:
                r0 = rep0[f"T{T}"]
                reps.append({
                    "rep": 0,
                    "seed_placement": r0["seed_placement"],
                    "max_genuine": r0["max_genuine"],
                    "min_reading2": r0["min_reading2"],
                    "separated": r0["separated"],
                    "seconds": None,  # reused from V5-RA-2 confirmation
                    "rc3_reused": True,
                })
                if not r0["separated"]:
                    all_separated = False
                continue
            r = one_repetition(N, m0, m1, rep, rung_idx)
            reps.append({
                "rep": rep,
                "seed_placement": seed_placement(rep, rung_idx),
                "max_genuine": r["max_genuine"],
                "min_reading2": r["min_reading2"],
                "separated": r["separated"],
                "seconds": round(r["seconds"], 3),
            })
            if not r["separated"]:
                all_separated = False
        n_sep = sum(1 for r in reps if r["separated"])
        out["rungs"][f"T{T}"] = {
            "p": p, "N": N, "m0": m0, "m1": m1,
            "separated_reps": f"{n_sep}/{n_reps}",
            "all_separated": n_sep == n_reps,
            "repetitions": reps,
        }
        print(f"T{T}: m0={m0} m1={m1} separated {n_sep}/{n_reps}")
    out["c2a_blocking"] = all_separated
    out["c2a_verdict"] = ("BLOCKING" if all_separated else "DIAGNOSTIC ONLY")
    out_path = EXP_ROOT / "runs" / "power_check_results.yaml"
    out_path.write_text(_dump_yaml(out) + "\n")
    print(f"\nC2a verdict: {out['c2a_verdict']}")
    print(f"written: {out_path}")
    return 0


def _yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if any(c in s for c in ":#{}[]&*!|>'\"%@`") or s != s.strip() or s == "":
        return json.dumps(s)
    return s


def _dump_yaml(obj, indent=0) -> str:
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{k}:")
                lines.append(_dump_yaml(v, indent + 1))
            elif isinstance(v, dict):
                lines.append(f"{pad}{k}: {{}}")
            elif isinstance(v, list):
                lines.append(f"{pad}{k}: []")
            else:
                lines.append(f"{pad}{k}: {_yaml_scalar(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_dump_yaml(item, indent + 1))
            else:
                lines.append(f"{pad}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{pad}{_yaml_scalar(obj)}")
    return "\n".join(lines)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--time-only", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args(argv)
    if args.time_only:
        return time_only()
    if args.full:
        return full(args.n)
    ap.error("use --time-only or --full")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
