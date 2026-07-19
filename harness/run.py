"""Experiment entry point: EXP-SEMAEV-001.

Runs the matched pair for each toy instance and writes immutable run records:

  * a Pollard-rho baseline solve (control; emits a discrete_log certificate),
  * an S_3 Groebner decomposition measurement (emits a decomposition
    certificate when the target decomposes, else kind: none).

The primary quantity is the Groebner cost versus field bit size (KN-OPEN-002);
the rho baseline is recorded as matched context, never equated to the Groebner
cost without a cost model (baseline discipline, docs/evidence-and-reproducibility).

Usage:
    python -m harness.run --experiment EXP-SEMAEV-001
    python -m harness.run --experiment EXP-SEMAEV-001 --bits 8,10,12 --seeds 1,2 \
        --factor-base 14 --out experiments/EXP-SEMAEV-001
"""
from __future__ import annotations

import argparse
import io
import time
from contextlib import redirect_stdout

from . import rho, semaev
from .runner import RunResult, curve_id, write_run
from .toycurve import generate_instance

EXP_ID = "EXP-SEMAEV-001"
EXP_AREA = "SEMAEV"
DEFAULT_BITS = [8, 10, 12]
DEFAULT_SEEDS = [1, 2]
DEFAULT_FACTOR_BASE = 14


def _rho_run(inst, seed, bits, cmd, out_root) -> str:
    log = io.StringIO()
    started = time.time()
    with redirect_stdout(log):
        res = rho.solve(inst)
        print(f"rho: solved={res.solved} k={res.k} "
              f"group_ops={res.group_operations} iters={res.iterations}")
    finished = time.time()
    cid = curve_id(inst.p, inst.a, inst.b, bits)
    if res.solved:
        cert = {"kind": "discrete_log",
                "statement": {"curve": {"p": inst.p, "a": inst.a, "b": inst.b},
                              "P": list(inst.P), "Q": list(inst.Q), "k": res.k}}
        valid, reason, status = True, None, "completed_valid"
    else:
        cert = {"kind": "none"}
        valid, reason, status = False, res.reason, "cancelled_by_budget"
    rr = RunResult(
        run_suffix=f"rho-b{bits}-s{seed}", curve_id=cid, seed=seed,
        parameters={"field_bits": bits, "prime_order_n": inst.n, "solver": "pollard_rho"},
        metrics={"group_operations": res.group_operations,
                 "iterations": res.iterations, "solved": res.solved},
        certificate=cert, valid=valid, invalid_reason=reason,
        stdout=log.getvalue(),
        raw={"n": inst.n, "recovered_k": res.k})
    return write_run(EXP_ID, EXP_AREA, rr, status=status, command=cmd,
                     started=started, finished=finished, out_root=out_root)


def _gb_run(inst, seed, bits, factor_base, cmd, out_root) -> str:
    log = io.StringIO()
    started = time.time()
    with redirect_stdout(log):
        m = semaev.measure_s3_decomposition(inst, factor_base_size=factor_base)
        baseline = rho.solve(inst)
        print(f"gb: basis_size={m.groebner_basis_size} "
              f"max_degree(proxy)={m.groebner_basis_max_degree} "
              f"seconds={m.groebner_seconds:.4f} decomp={m.decomposition_found}")
    finished = time.time()
    cid = curve_id(inst.p, inst.a, inst.b, bits)
    cert = m.certificate if m.decomposition_found else {"kind": "none"}
    rr = RunResult(
        run_suffix=f"gb-b{bits}-s{seed}", curve_id=cid, seed=seed,
        parameters={"field_bits": bits, "factor_base_size": m.factor_base_size,
                    "decomposition_length": m.decomposition_length,
                    "solver": "sympy_groebner_grevlex"},
        metrics={"groebner_seconds": round(m.groebner_seconds, 6),
                 "groebner_basis_size": m.groebner_basis_size,
                 "groebner_basis_max_degree_proxy": m.groebner_basis_max_degree,
                 "is_trivial_ideal": m.is_trivial_ideal,
                 "decomposition_found": m.decomposition_found,
                 "rho_baseline_group_operations": baseline.group_operations},
        certificate=cert, stdout=log.getvalue(),
        raw={"target_x": m.target_x, "summand_x": m.summand_x})
    return write_run(EXP_ID, EXP_AREA, rr, status="completed_valid", command=cmd,
                     started=started, finished=finished, out_root=out_root)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", default=EXP_ID)
    ap.add_argument("--bits", default=",".join(map(str, DEFAULT_BITS)))
    ap.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    ap.add_argument("--factor-base", type=int, default=DEFAULT_FACTOR_BASE)
    ap.add_argument("--out", default=None,
                    help="output experiment root (default experiments/<EXP_ID>)")
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
            cmd_r = (f"python -m harness.run --experiment {EXP_ID} "
                     f"--bits {bits} --seeds {seed} --factor-base {args.factor_base}")
            written.append(_rho_run(inst, seed, bits, cmd_r + "  # rho run", args.out))
            written.append(_gb_run(inst, seed, bits, args.factor_base,
                                   cmd_r + "  # gb run", args.out))
    print(f"wrote {len(written)} run records:")
    for r in written:
        print(f"  {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
