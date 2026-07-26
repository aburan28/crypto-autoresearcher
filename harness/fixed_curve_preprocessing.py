"""Fixed-curve preprocessing probe for S_3 decomposition work.

This experiment measures the practical cost split between:

* one-time factor-base precomputation on a fixed curve, and
* repeated target descents using that factor base.

It mirrors the contract shape used by other harness experiments: each run is a
reproducible immutable record with an explicit command, environment, timing, and
certificate.
"""
from __future__ import annotations

import argparse
import io
import time
from contextlib import redirect_stdout

from . import rho, semaev
from .runner import RunResult, curve_id, write_run
from .toycurve import generate_instance

EXP_ID = "EXP-FCP-001"
EXP_AREA = "FCP"
DEFAULT_BITS = [8, 10, 12]
DEFAULT_SEEDS = [1, 2]
DEFAULT_FACTOR_BASE = 14
DEFAULT_TARGETS_PER_CURVE = 3
GROEBNER_TIMEOUT_S = 120


def _derive_targets(inst, count: int) -> list[tuple[int, tuple[int, int]]]:
    """Return deterministic target points from distinct scalar multipliers."""
    E = inst.curve()
    P = inst.P
    targets: list[tuple[int, tuple[int, int]]] = []
    # Keep a deterministic but nontrivial stride to avoid a degenerate repeated run.
    stride = max(2, inst.seed % max(2, inst.n - 3))
    for idx in range(count):
        k = ((idx + 1) * stride) % (inst.n - 1) + 1
        targets.append((k, E.mul(k, P)))
    return targets


def _run_rho(inst, seed: int, bits: int, command: str, out_root: str | None,
             exp_id: str = EXP_ID):
    log = io.StringIO()
    started = time.time()
    with redirect_stdout(log):
        res = rho.solve(inst)
        print(
            f"rho: solved={res.solved} k={res.k} "
            f"group_ops={res.group_operations} "
            f"total_group_ops={res.total_group_operations} "
            f"iters={res.iterations}"
        )
    finished = time.time()

    if res.solved:
        cert = {
            "kind": "discrete_log",
            "statement": {"curve": {"p": inst.p, "a": inst.a, "b": inst.b},
                          "P": list(inst.P), "Q": list(inst.Q), "k": res.k},
        }
        valid = True
        status = "completed_valid"
        invalid_reason = None
    else:
        cert = {"kind": "none"}
        valid = False
        status = "cancelled_by_budget"
        invalid_reason = res.reason

    rr = RunResult(
        run_suffix=f"rho-b{bits}-s{seed}-t-fixed-{seed}-{len(log.getvalue())}",
        curve_id=curve_id(inst.p, inst.a, inst.b, bits),
        seed=seed,
        parameters={"field_bits": bits, "prime_order_n": inst.n, "solver": "pollard_rho"},
        metrics={
            "group_operations": res.group_operations,
            "total_group_operations": res.total_group_operations,
            "iterations": res.iterations,
            "solved": res.solved,
            "is_fixed_curve_probe": True,
        },
        certificate=cert,
        valid=valid,
        invalid_reason=invalid_reason,
        stdout=log.getvalue(),
        raw={"n": inst.n, "recovered_k": res.k},
    )
    return write_run(
        exp_id, EXP_AREA, rr, status=status, command=command,
        started=started, finished=finished, out_root=out_root
    )


def _run_s3_decomposition(inst, bits: int, seed: int, target_k: int, target_pt, target_idx: int,
                          factor_base, factor_base_size: int, mode: str,
                          precompute_seconds: float, command_suffix: str, out_root: str | None,
                          exp_id: str = EXP_ID):
    log = io.StringIO()
    started = time.time()

    rebuild_seconds = 0.0
    if mode == "naive":
        rebuild_start = time.perf_counter()
        factor_base = semaev.build_factor_base(inst, factor_base_size, seed)
        rebuild_seconds = time.perf_counter() - rebuild_start

    with redirect_stdout(log):
        m = semaev.measure_s3_decomposition(
            inst,
            factor_base_size=factor_base_size,
            target=target_pt,
            factor_base=factor_base,
        )

    finished = time.time()
    metrics = {
        "mode": mode,
        "target_k": target_k,
        "target_index": target_idx,
        "field_bits": bits,
        "groebner_seconds": round(m.groebner_seconds, 6),
        "groebner_basis_size": m.groebner_basis_size,
        "groebner_basis_max_degree_proxy": m.groebner_basis_max_degree,
        "is_trivial_ideal": m.is_trivial_ideal,
        "decomposition_found": m.decomposition_found,
        "factor_base_size": m.factor_base_size,
        "decomposition_length": m.decomposition_length,
        "precompute_seconds": round(precompute_seconds, 6),
        "rebuild_seconds": round(rebuild_seconds, 6),
    }
    rr = RunResult(
        run_suffix=f"{mode}-b{bits}-s{seed}-t{target_idx}",
        curve_id=curve_id(inst.p, inst.a, inst.b, bits),
        seed=seed,
        parameters={"field_bits": bits, "factor_base_size": factor_base_size,
                    "target_index": target_idx},
        metrics=metrics,
        certificate=m.certificate if m.decomposition_found else {"kind": "none"},
        valid=True,
        stdout=log.getvalue(),
        raw={"target": list(target_pt), "target_k": target_k,
             "factor_base": factor_base},
    )
    return write_run(
        exp_id, EXP_AREA, rr, status="completed_valid", command=command_suffix,
        started=started, finished=finished, out_root=out_root
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run fixed-curve S_3 decomposition precompute and reuse experiments."
    )
    ap.add_argument("--bits", default=",".join(map(str, DEFAULT_BITS)))
    ap.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    ap.add_argument("--factor-base", type=int, default=DEFAULT_FACTOR_BASE)
    ap.add_argument("--targets-per-curve", type=int, default=DEFAULT_TARGETS_PER_CURVE)
    ap.add_argument("--out", default=None, help="output experiment root (default experiments/<EXP_ID>)")
    ap.add_argument("--exp-id", default=EXP_ID, help="experiment ID for run manifests")
    args = ap.parse_args()

    bits_list = [int(b) for b in args.bits.split(",") if b]
    seeds = [int(s) for s in args.seeds.split(",") if s]
    written: list[str] = []

    for bits in bits_list:
        for seed in seeds:
            inst = generate_instance(seed=seed, field_bits=bits)
            base_command = (
                f"python -m harness.fixed_curve_preprocessing --bits {bits} "
                f"--seeds {seed} --factor-base {args.factor_base} "
                f"--targets-per-curve {args.targets_per_curve}"
            )
            targets = _derive_targets(inst, args.targets_per_curve)

            # One-time precompute for fixed-curve mode.
            pre_start = time.time()
            factor_base = semaev.build_factor_base(inst, args.factor_base, seed)
            precompute_seconds = time.time() - pre_start
            pre_rr = RunResult(
                run_suffix=f"fixed-precompute-b{bits}-s{seed}-fb{args.factor_base}",
                curve_id=curve_id(inst.p, inst.a, inst.b, bits),
                seed=seed,
                parameters={"field_bits": bits, "factor_base_size": len(factor_base)},
                metrics={
                    "mode": "fixed_precompute",
                    "factor_base_size": len(factor_base),
                    "precompute_seconds": round(precompute_seconds, 6),
                    "precompute_target_count": args.targets_per_curve,
                },
                certificate={"kind": "none"},
                stdout="",
                raw={"factor_base": factor_base},
            )
            written.append(
                write_run(
                    args.exp_id, EXP_AREA, pre_rr, status="completed_valid",
                    command=f"{base_command} # precompute", started=pre_start,
                    finished=pre_start + precompute_seconds, out_root=args.out
                )
            )

            # Per-curve rho baseline on the instantiated target.
            written.append(
                _run_rho(
                    inst=inst,
                    seed=seed,
                    bits=bits,
                    command=f"{base_command} # rho-control",
                    out_root=args.out,
                    exp_id=args.exp_id,
                )
            )

            for target_idx, (target_k, target_pt) in enumerate(targets):
                # Fixed factor-base mode.
                written.append(
                    _run_s3_decomposition(
                        inst=inst,
                        bits=bits,
                        seed=seed,
                        target_k=target_k,
                        target_pt=target_pt,
                        target_idx=target_idx,
                        factor_base=factor_base,
                        factor_base_size=args.factor_base,
                        mode="fixed",
                        precompute_seconds=precompute_seconds,
                        command_suffix=f"{base_command} # fixed target={target_idx}",
                        out_root=args.out,
                        exp_id=args.exp_id,
                    )
                )
                # Fresh factor-base mode (recompute every target).
                written.append(
                    _run_s3_decomposition(
                        inst=inst,
                        bits=bits,
                        seed=seed,
                        target_k=target_k,
                        target_pt=target_pt,
                        target_idx=target_idx,
                        factor_base=[],
                        factor_base_size=args.factor_base,
                        mode="naive",
                        precompute_seconds=0.0,
                        command_suffix=f"{base_command} # naive target={target_idx}",
                        out_root=args.out,
                        exp_id=args.exp_id,
                    )
                )
    print(f"wrote {len(written)} run records:")
    for run_id in written:
        print(f"  {run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
