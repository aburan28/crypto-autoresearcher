"""Experiment entry point: EXP-SEMAEV-003 (powered redesign of EXP-SEMAEV-002).

DEC-20260721-001 called EXP-SEMAEV-002 inconclusive: the bare 1.5x yield-ratio
threshold tripped only in low-count cells where the ratio is sampling noise.
This redesign fixes that with (a) many more targets, (b) a minimum-count power
gate (a cell is decisive only when found_random >= min_count), and (c) a Katz
95% confidence interval on each structured/random yield ratio, so the claim is
read from the interval, not a point estimate.

Usage:
    python -m harness.run_yield_powered
    python -m harness.run_yield_powered --bits 12,14,16 --seeds 1,2,3,4,5 \
        --factor-base 20 --targets 2000 --min-count 30
"""
from __future__ import annotations

import argparse
import io
import math
import time
from contextlib import redirect_stdout

from . import semaev
from .runner import RunResult, curve_id, write_run
from .toycurve import generate_instance

EXP_ID = "EXP-SEMAEV-003"
EXP_AREA = "SEMAEV"
DEFAULT_BITS = [12, 14, 16]
DEFAULT_SEEDS = [1, 2, 3, 4, 5]
DEFAULT_FACTOR_BASE = 20
DEFAULT_TARGETS = 2000
DEFAULT_MIN_COUNT = 30


def katz_log_ci(f1: int, n1: int, f2: int, n2: int, z: float = 1.96):
    """95% Katz log CI for the ratio of two proportions (f1/n1)/(f2/n2).

    Returns (ratio, lo, hi) or (None, None, None) if a count is zero (undefined).
    Wide intervals at small counts are the whole point: they keep a noisy ratio
    from reading as a real effect.
    """
    if f1 == 0 or f2 == 0 or n1 == 0 or n2 == 0:
        return None, None, None
    p1, p2 = f1 / n1, f2 / n2
    ratio = p1 / p2
    se = math.sqrt((1 - p1) / f1 + (1 - p2) / f2)
    return ratio, ratio * math.exp(-z * se), ratio * math.exp(z * se)


def _powered_run(inst, seed, bits, L, targets, min_count, cmd, out_root) -> str:
    log = io.StringIO()
    started = time.time()
    with redirect_stdout(log):
        rb = semaev.factor_base_random(inst, L)
        ib = semaev.factor_base_interval(inst, L)
        ab = semaev.factor_base_ap(inst, L, step=3)
        f_r, n_r, cert = semaev.measure_yield_counts(inst, rb, targets)
        f_i, n_i, cert_i = semaev.measure_yield_counts(inst, ib, targets)
        f_a, n_a, cert_a = semaev.measure_yield_counts(inst, ab, targets)
        cert = cert or cert_i or cert_a
        r_int, lo_int, hi_int = katz_log_ci(f_i, n_i, f_r, n_r)
        r_ap, lo_ap, hi_ap = katz_log_ci(f_a, n_a, f_r, n_r)
        powered = f_r >= min_count
        print(f"found random={f_r}/{n_r} interval={f_i}/{n_i} ap={f_a}/{n_a} "
              f"powered={powered}")
        if r_int is not None:
            print(f"  interval/random ratio={r_int:.3f} 95%CI=[{lo_int:.3f},{hi_int:.3f}]")
        if r_ap is not None:
            print(f"  ap/random ratio={r_ap:.3f} 95%CI=[{lo_ap:.3f},{hi_ap:.3f}]")
    finished = time.time()
    cid = curve_id(inst.p, inst.a, inst.b, bits)
    certificate = cert if cert else {"kind": "none"}

    def _rnd(v):
        return None if v is None else round(v, 4)

    rr = RunResult(
        run_suffix=f"powered-b{bits}-s{seed}", curve_id=cid, seed=seed,
        parameters={"field_bits": bits, "factor_base_size": L,
                    "decomposition_length": 2, "target_count": targets,
                    "min_count_gate": min_count, "solver": "enumeration_s3_yield"},
        metrics={"found_random": f_r, "made_random": n_r,
                 "found_interval": f_i, "found_ap": f_a,
                 "powered": powered,
                 "ratio_interval": _rnd(r_int), "ci_interval_lo": _rnd(lo_int),
                 "ci_interval_hi": _rnd(hi_int),
                 "ratio_ap": _rnd(r_ap), "ci_ap_lo": _rnd(lo_ap),
                 "ci_ap_hi": _rnd(hi_ap),
                 "structured_advantage_ci_excludes_1p5": bool(
                     (lo_int is not None and lo_int > 1.5) or
                     (lo_ap is not None and lo_ap > 1.5)),
                 "prime_order_n": inst.n},
        certificate=certificate, stdout=log.getvalue(),
        raw={"factor_base_random_x": rb, "factor_base_interval_x": ib,
             "factor_base_ap_x": ab})
    return write_run(EXP_ID, EXP_AREA, rr, status="completed_valid", command=cmd,
                     started=started, finished=finished, out_root=out_root)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", default=EXP_ID)
    ap.add_argument("--bits", default=",".join(map(str, DEFAULT_BITS)))
    ap.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    ap.add_argument("--factor-base", type=int, default=DEFAULT_FACTOR_BASE)
    ap.add_argument("--targets", type=int, default=DEFAULT_TARGETS)
    ap.add_argument("--min-count", type=int, default=DEFAULT_MIN_COUNT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.experiment != EXP_ID:
        print(f"unknown experiment {args.experiment}")
        return 2
    bits_list = [int(b) for b in args.bits.split(",") if b]
    seeds = [int(s) for s in args.seeds.split(",") if s]
    written = []
    for bits in bits_list:
        for seed in seeds:
            inst = generate_instance(seed=seed, field_bits=bits)
            cmd = (f"python -m harness.run_yield_powered --experiment {EXP_ID} "
                   f"--bits {bits} --seeds {seed} --factor-base {args.factor_base} "
                   f"--targets {args.targets} --min-count {args.min_count}")
            written.append(_powered_run(inst, seed, bits, args.factor_base,
                                        args.targets, args.min_count, cmd, args.out))
    print(f"wrote {len(written)} run records:")
    for r in written:
        print(f"  {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
