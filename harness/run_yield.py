"""Experiment entry point: EXP-SEMAEV-002.

Independent, clean-room replication of the factor-base yield effect studied by
the campaign at m=3 (H-FB-001 / EXP-FB-001, rejected_scoped), now at m=2 (S_3)
with a different implementation. For each toy instance it measures the m=2
decomposition yield of a matched random factor base (control) against two
structured bases (consecutive interval, arithmetic progression) and records the
structured/random yield ratio -- the quantity H-FB-001's >1.5x threshold is
stated in. One found decomposition per run is emitted as a verifiable
certificate.

Usage:
    python -m harness.run_yield
    python -m harness.run_yield --bits 12,14,16 --seeds 1,2,3 \
        --factor-base 20 --targets 300
"""
from __future__ import annotations

import argparse
import io
import time
from contextlib import redirect_stdout

from . import semaev
from .runner import RunResult, curve_id, write_run
from .toycurve import generate_instance

EXP_ID = "EXP-SEMAEV-002"
EXP_AREA = "SEMAEV"
DEFAULT_BITS = [12, 14, 16]
DEFAULT_SEEDS = [1, 2, 3]
DEFAULT_FACTOR_BASE = 20
DEFAULT_TARGETS = 300


def _yield_run(inst, seed, bits, L, targets, cmd, out_root) -> str:
    log = io.StringIO()
    started = time.time()
    with redirect_stdout(log):
        rb = semaev.factor_base_random(inst, L)
        ib = semaev.factor_base_interval(inst, L)
        ab = semaev.factor_base_ap(inst, L, step=3)
        y_rand, f_rand, cert = semaev.measure_yield(inst, rb, targets)
        y_int, _, cert_i = semaev.measure_yield(inst, ib, targets)
        y_ap, _, cert_a = semaev.measure_yield(inst, ab, targets)
        cert = cert or cert_i or cert_a
        r_int = (y_int / y_rand) if y_rand else None
        r_ap = (y_ap / y_rand) if y_rand else None
        print(f"yield random={y_rand:.4f} interval={y_int:.4f} ap={y_ap:.4f} "
              f"ratio_int={r_int} ratio_ap={r_ap}")
    finished = time.time()
    cid = curve_id(inst.p, inst.a, inst.b, bits)
    certificate = cert if cert else {"kind": "none"}
    rr = RunResult(
        run_suffix=f"yield-b{bits}-s{seed}", curve_id=cid, seed=seed,
        parameters={"field_bits": bits, "factor_base_size": L,
                    "decomposition_length": 2, "target_count": targets,
                    "solver": "enumeration_s3_yield"},
        metrics={"yield_random": round(y_rand, 5),
                 "yield_interval": round(y_int, 5),
                 "yield_ap": round(y_ap, 5),
                 "ratio_interval_over_random": None if r_int is None else round(r_int, 4),
                 "ratio_ap_over_random": None if r_ap is None else round(r_ap, 4),
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
            cmd = (f"python -m harness.run_yield --experiment {EXP_ID} "
                   f"--bits {bits} --seeds {seed} --factor-base {args.factor_base} "
                   f"--targets {args.targets}")
            written.append(_yield_run(inst, seed, bits, args.factor_base,
                                      args.targets, cmd, args.out))
    print(f"wrote {len(written)} run records:")
    for r in written:
        print(f"  {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
