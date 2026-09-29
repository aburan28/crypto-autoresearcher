"""Generate rho / kangaroo walk data and figures for one ECDLP instance.

    python -m harness.run_walkviz --seed 7 --field-bits 16 --out-dir out/

Writes, per figure requested, a JSON record of the exact states walked and an
SVG drawing of them. Every scalar reported was recovered from public data and
re-verified against Q (docs/claims-and-verification.md); `secret_k_matches`
compares the recovered scalar with the instance's stored k as a self-check on
the harness, not as an input to the solver.

Conclusions drawn from these outputs are scoped to the curve, subgroup order,
walk parameters and budget printed in the manifest.
"""
from __future__ import annotations

import argparse
import json
import os

from . import kangaroo, walk, walkviz
from .toycurve import generate_instance

FIGURES = ("rho", "dp", "kangaroo")


def _write(path: str, text: str) -> str:
    with open(path, "w") as fh:
        fh.write(text)
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--field-bits", type=int, default=16)
    ap.add_argument("--out-dir", default="walkviz-out")
    ap.add_argument("--figures", default="rho,dp,kangaroo",
                    help=f"comma-separated subset of {','.join(FIGURES)}")
    ap.add_argument("--branches", type=int, default=16)
    ap.add_argument("--dp-bits", type=int, default=3)
    ap.add_argument("--walks", type=int, default=32,
                    help="distinguished-point walks to run for the dp figure; "
                         "all of them are run and drawn, the first verified "
                         "collision is the reported solution")
    ap.add_argument("--max-graph-nodes", type=int, default=2048,
                    help="refuse the rho figure above this subgroup order")
    ap.add_argument("--layout-iterations", type=int, default=300)
    ap.add_argument("--layout-seed", type=int, default=0)
    args = ap.parse_args(argv)

    figures = [f.strip() for f in args.figures.split(",") if f.strip()]
    unknown = [f for f in figures if f not in FIGURES]
    if unknown:
        ap.error(f"unknown figure(s): {', '.join(unknown)}")

    os.makedirs(args.out_dir, exist_ok=True)
    inst = generate_instance(seed=args.seed, field_bits=args.field_bits)
    E = inst.curve()
    manifest: dict = {
        "instance": {"p": inst.p, "a": inst.a, "b": inst.b, "n": inst.n,
                     "P": list(inst.P), "Q": list(inst.Q),
                     "field_bits": inst.field_bits, "seed": inst.seed},
        "walk_params": {"branches": args.branches, "dp_bits": args.dp_bits},
        "figures": {},
    }
    out = lambda name: os.path.join(args.out_dir, name)     # noqa: E731

    if "rho" in figures:
        if inst.n > args.max_graph_nodes:
            manifest["figures"]["rho"] = {
                "skipped": f"subgroup order {inst.n} exceeds "
                           f"--max-graph-nodes {args.max_graph_nodes}"}
        else:
            w = walk.AddingWalk(E, inst.P, inst.Q, inst.n, inst.seed,
                                branches=args.branches, tag="rhofig")
            tr = walk.trace_orbit(w)
            walk.dump_json(walk.trace_to_dict(w, tr), out("rho_trace.json"))
            _write(out("rho_trace.svg"),
                   walkviz.render_functional_graph_svg(
                       w, tr, n=inst.n, seed=args.layout_seed,
                       iterations=args.layout_iterations))
            manifest["figures"]["rho"] = {
                "elements": inst.n, "tail_length": tr.tail_length,
                "cycle_length": tr.cycle_length, "closed": tr.closed,
                "group_operations": tr.group_operations,
                "files": ["rho_trace.json", "rho_trace.svg"]}

    if "dp" in figures:
        w = walk.AddingWalk(E, inst.P, inst.Q, inst.n, inst.seed,
                            branches=args.branches, dp_bits=args.dp_bits,
                            tag="rhodp")
        res = walk.solve_dp(inst, dp_bits=args.dp_bits, branches=args.branches,
                            max_walks=args.walks, record_paths=True,
                            stop_on_solution=False, walk=w)
        walk.dump_json(walk.dp_walks_to_dict(w, res.walks, res.collision),
                       out("dp_walks.json"))
        _write(out("dp_walks.svg"),
               walkviz.render_dp_forest_svg(w, res.walks, res.collision,
                                            seed=args.layout_seed,
                                            iterations=args.layout_iterations))
        manifest["figures"]["dp"] = {
            "solved": res.solved, "k": res.k,
            "walks_reaching_dp": sum(1 for w in res.walks if w.hit_dp),
            "secret_k_matches": (res.k == inst.k) if res.solved else None,
            "walks": len(res.walks), "steps": res.steps,
            "distinguished_points": res.distinguished_points,
            "group_operations": res.group_operations,
            "reason": res.reason,
            "files": ["dp_walks.json", "dp_walks.svg"]}

    if "kangaroo" in figures:
        res = kangaroo.solve_interval(inst, record_paths=True,
                                      branches=args.branches,
                                      dp_bits=args.dp_bits)
        walk.dump_json(kangaroo.kangaroos_to_dict(res), out("kangaroo.json"))
        _write(out("kangaroo.svg"),
               walkviz.render_kangaroo_svg(res, seed=args.layout_seed,
                                           iterations=args.layout_iterations))
        manifest["figures"]["kangaroo"] = {
            "solved": res.solved, "k": res.k,
            "secret_k_matches": (res.k == inst.k) if res.solved else None,
            "interval": list(res.interval), "jumps": res.jumps,
            "distinguished_points": res.distinguished_points,
            "group_operations": res.group_operations,
            "reason": res.reason,
            "files": ["kangaroo.json", "kangaroo.svg"]}

    walk.dump_json(manifest, out("manifest.json"))
    print(json.dumps(manifest["figures"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
