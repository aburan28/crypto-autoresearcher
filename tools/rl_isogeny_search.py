#!/usr/bin/env python3
"""Reinforcement-learning search over an F_p-isogeny class for a cheaper
point-decomposition presentation -- driver for harness.rl_isogeny.

What runs
---------
One environment (a random generic curve of --bits, or --p --a --b), the chosen
agents trained for --episodes episodes each on the same environment and seed,
then --eval-episodes greedy episodes per trained agent.  Every agent is paired
with the random agent under the same episode budget.  With --oracle the whole
isogeny class is enumerated and certified (tools.isogeny_dreg_search) and every
(member, presentation) state is scored with the same meter, giving the true
optimum, the regret of every agent, and the pre-registered reading: whether the
score is constant across the class for each presentation.

Controls (each is a separate invocation so its output is a separate file):
  --permuted    reward is state-independent noise; the agent must not beat random
  --planted     a seeded reachable state carries a bonus; the agent must find it
  --p 1009 --a 0 --b 7   a D_0 = -3 class (j = 0 members present): the known
                structural degeneration, reported as a positive control

Nothing here supports a crypto-scale claim.  Claim tier: toy.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness.rl_isogeny import (  # noqa: E402
    GRIDS,
    GridSpec,
    IsogenyPDPEnv,
    Weights,
    compare,
    evaluate,
    exhaustive_oracle,
    make_agent,
    summarize,
    train,
)
from tools.isogeny_dreg_search import is_singular  # noqa: E402


def random_curve(bits: int, seed: int):
    rng = random.Random(seed)
    while True:
        p = rng.randrange(2 ** (bits - 1), 2 ** bits) | 1
        if p > 3 and all(p % q for q in range(3, math.isqrt(p) + 1, 2)):
            break
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if not is_singular(a, b, p):
            return p, a, b


def environment_record() -> dict:
    rec = {"python": platform.python_version(), "platform": platform.platform()}
    try:
        import torch
        rec["torch"] = torch.__version__
    except Exception:  # pragma: no cover
        rec["torch"] = None
    return rec


def run_one(args, seed: int, log) -> dict:
    if args.bits:
        p, a, b = random_curve(args.bits, seed)
    else:
        p, a, b = args.p, args.a, args.b
        if p is None or a is None or b is None:
            raise SystemExit("give --p --a --b or --bits")
    primes = tuple(int(x) for x in args.primes.split(","))
    weights = Weights(excess=args.w_excess, deficit=args.w_deficit, planted_bonus=args.planted_bonus)
    t0 = time.time()
    env = IsogenyPDPEnv(p, a, b, seed=seed, primes=primes, grid=GRIDS[args.grid],
                        max_steps=args.max_steps, n_null=args.null_curves, null_kind=args.null_kind,
                        weights=weights, permuted=args.permuted, planted=args.planted,
                        plant_depth=args.plant_depth, identity_bits=0 if args.no_identity else 8,
                        exact_trace_limit=args.exact_trace_limit, start_spec=args.start_spec)
    env.reset()
    log(f"env p={p} a={a} b={b} trace={env.trace} N={env.N} active={env.active_primes} "
        f"specs={len(env.specs)} actions={env.n_actions} obs={env.obs_dim} ({time.time() - t0:.1f}s)")

    names = [n.strip() for n in args.agents.split(",") if n.strip()]
    if "random" not in names:
        names.insert(0, "random")
    results = {}
    for name in names:
        try:
            agent = make_agent(name, env, seed=seed + 1000)
        except ImportError as exc:
            results[name] = {"skipped": str(exc)}
            log(f"skip {name}: {exc}")
            continue
        log(f"train {name} for {args.episodes} episodes")
        t1 = time.time()
        recs = train(env, agent, args.episodes, log=log)
        ev = evaluate(env, agent, args.eval_episodes, greedy=True) if args.eval_episodes else []
        evs = evaluate(env, agent, args.eval_episodes, greedy=False) if args.eval_episodes else []
        results[name] = {
            "train": recs, "eval": ev, "eval_stochastic": evs,
            "train_summary": summarize(recs), "eval_summary": summarize(ev) if ev else None,
            "eval_stochastic_summary": summarize(evs) if evs else None,
            "seconds": time.time() - t1,
            "q_states": len(agent.Q) if hasattr(agent, "Q") else None,
            "ppo_updates": getattr(agent, "updates", None),
        }
        # learning curve: best score per decile of training
        dec = max(1, len(recs) // 10)
        results[name]["learning_curve"] = [
            {"episodes": f"{i}-{min(len(recs), i + dec) - 1}",
             "mean_true_return": sum(r["true_return"] for r in recs[i:i + dec]) / len(recs[i:i + dec]),
             "mean_best": sum(r["best_score"] for r in recs[i:i + dec]) / len(recs[i:i + dec]),
             "hit_rate": sum(1 for r in recs[i:i + dec] if r["planted_hit"]) / len(recs[i:i + dec])}
            for i in range(0, len(recs), dec)]

    oracle = None
    if args.oracle:
        log("oracle: enumerating the class")
        oracle = exhaustive_oracle(env, max_members=args.oracle_max_members or None, verbose=args.verbose)
        log(f"oracle: class_size={oracle['class_size']} certified={oracle['certified']} "
            f"best={oracle['best'] and oracle['best']['score']:.3f} constant={oracle['class_constant_per_spec']}")
        for name, res in results.items():
            if "train" in res:
                res["train_summary"] = summarize(res["train"], oracle["best"]["score"])
                if res["eval"]:
                    res["eval_summary"] = summarize(res["eval"], oracle["best"]["score"])
                    res["eval_stochastic_summary"] = summarize(res["eval_stochastic"], oracle["best"]["score"])

    paired = {}
    if "train" in results.get("random", {}):
        for name, res in results.items():
            if name != "random" and "train" in res:
                paired[name] = {"train": compare(res["train"], results["random"]["train"]),
                                "eval": compare(res["eval"], results["random"]["eval"]) if res["eval"] else None,
                                "eval_stochastic": (compare(res["eval_stochastic"], results["random"]["eval_stochastic"])
                                                    if res["eval_stochastic"] else None)}

    report = {
        "instrument": "tools/rl_isogeny_search.py",
        "claim_tier": "toy",
        "seed": seed,
        "config": vars(args),
        "environment": {**env.summary(), "runtime": environment_record()},
        "meter": {"evaluations": env.meter.evaluations, "seconds": env.meter.seconds,
                  "order_checks_passed": env.order_checks, "curves_visited": len(env._curves)},
        "agents": results,
        "paired_vs_random": paired,
        "oracle": oracle,
        "seconds_total": time.time() - t0,
        "reading": {
            "what_a_positive_would_be": "a state with excess_fall > 0 on a certified class of a generic curve, "
                                        "reproduced with independent seeds and null curves",
            "pre_registered": "excess_fall = 0 and deficit_excess = 0 on every state of a generic class; the "
                              "known levers (k, c, m, digit vs direct) move only the shape term",
        },
    }
    return report


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def aggregate(reports, args) -> dict:
    """Across seeds: per-agent eval hit rate, final-optimal rate, best score, paired z."""
    agents = {}
    names = [n for n in reports[0]["agents"]]
    for name in names:
        rows = [r["agents"][name] for r in reports if "train" in r["agents"][name]]
        if not rows:
            agents[name] = {"skipped": reports[0]["agents"][name].get("skipped")}
            continue
        agents[name] = {
            "seeds": len(rows),
            "train_planted_hit_rate": _mean([x["train_summary"]["planted_hit_rate"] for x in rows]),
            "eval_planted_hit_rate": _mean([x["eval_summary"]["planted_hit_rate"] for x in rows if x["eval_summary"]]),
            "eval_planted_hits_by_seed": [x["eval_summary"]["planted_hit_rate"] for x in rows if x["eval_summary"]],
            "eval_stochastic_planted_hit_rate": _mean([x["eval_stochastic_summary"]["planted_hit_rate"]
                                                       for x in rows if x.get("eval_stochastic_summary")]),
            "eval_stochastic_planted_hits_by_seed": [x["eval_stochastic_summary"]["planted_hit_rate"]
                                                     for x in rows if x.get("eval_stochastic_summary")],
            "eval_stochastic_fraction_final_optimal": _mean([x["eval_stochastic_summary"].get("fraction_final_optimal")
                                                             for x in rows if x.get("eval_stochastic_summary")]),
            "train_mean_best_score": _mean([x["train_summary"]["best_score"]["mean"] for x in rows]),
            "eval_mean_best_score": _mean([x["eval_summary"]["best_score"]["mean"] for x in rows if x["eval_summary"]]),
            "eval_mean_final_score": _mean([x["eval_summary"]["final_score"]["mean"] for x in rows if x["eval_summary"]]),
            "train_fraction_best_optimal": _mean([x["train_summary"].get("fraction_best_optimal") for x in rows]),
            "eval_fraction_final_optimal": _mean([x["eval_summary"].get("fraction_final_optimal") for x in rows if x["eval_summary"]]),
            "last_decile_mean_true_return": _mean([x["learning_curve"][-1]["mean_true_return"] for x in rows]),
        }
    paired = {}
    for name in names:
        zs = [r["paired_vs_random"].get(name, {}) for r in reports]
        tr = [z["train"]["mean_diff_best_score"] for z in zs if z.get("train")]
        ev = [z["eval"]["mean_diff_best_score"] for z in zs if z.get("eval")]
        if tr:
            paired[name] = {"train_mean_diff_best_score": _mean(tr), "eval_mean_diff_best_score": _mean(ev),
                            "train_diffs_by_seed": tr}
    oracle = None
    if reports[0].get("oracle"):
        oracle = {"class_sizes": [r["oracle"]["class_size"] for r in reports],
                  "certified": [r["oracle"]["certified"] for r in reports],
                  "states_with_excess": sum(len(r["oracle"]["states_with_excess"]) for r in reports),
                  "excess_constant_per_spec": all(r["oracle"]["excess_constant_per_spec"] for r in reports),
                  "max_shape_spread_bits": max(r["oracle"]["max_shape_spread_bits"] or 0.0 for r in reports)}
    return {
        "instrument": "tools/rl_isogeny_search.py",
        "claim_tier": "toy",
        "config": vars(args),
        "seeds": [r["seed"] for r in reports],
        "environments": [{k: r["environment"][k] for k in ("p", "a", "b", "trace", "order", "start_spec", "planted_target", "permuted")}
                         for r in reports],
        "agents": agents,
        "paired_vs_random": paired,
        "oracle": oracle,
        "per_seed": reports,
        "reading": reports[0]["reading"],
    }


def _state_label(st: dict) -> str:
    curve = st.get("curve") or {}
    return f"{st.get('spec')} @ j={curve.get('j', st.get('j'))}"


def _slim_eval(records: list) -> dict:
    """Evaluation episodes as the summary keeps them: histograms of the final
    and best states, and per-episode (final_score, best_score, planted_hit)."""
    final_hist: dict = {}
    best_hist: dict = {}
    for r in records:
        f = _state_label(r.get("final_state") or {})
        b = _state_label(r.get("best_state") or {})
        final_hist[f] = final_hist.get(f, 0) + 1
        best_hist[b] = best_hist.get(b, 0) + 1
    return {
        "episodes": len(records),
        "final_states": dict(sorted(final_hist.items())),
        "best_states": dict(sorted(best_hist.items())),
        "per_episode": [[round(r["final_score"], 4), round(r["best_score"], 4), int(bool(r["planted_hit"]))]
                        for r in records],
    }


def compact(report: dict, keep_rows: bool = False) -> dict:
    """Per-seed report without per-episode training records or oracle rows
    (summaries, learning curves, slim evaluation episodes and the oracle
    summary stay).  The per-state oracle table and the training episodes are
    regenerable from --seed and are kept out of the repository, as the
    predecessor's per-member tables are (analysis/isogeny-dreg-search)."""
    out = {k: v for k, v in report.items() if k not in ("agents", "oracle")}
    out["agents"] = {}
    for name, res in report["agents"].items():
        if "train" not in res:
            out["agents"][name] = res
            continue
        slim = {k: v for k, v in res.items() if k not in ("train", "eval", "eval_stochastic")}
        slim["eval"] = _slim_eval(res.get("eval", []))
        slim["eval_stochastic"] = _slim_eval(res.get("eval_stochastic", []))
        slim["train_episodes"] = len(res["train"])
        out["agents"][name] = slim
    if report.get("oracle"):
        o = dict(report["oracle"])
        if not keep_rows:
            o.pop("rows", None)
            o["rows_omitted"] = True
        out["oracle"] = o
    return out


def summary_report(full: dict) -> dict:
    """The report written to --out: a single-seed report compacted, or an
    aggregate whose per-seed entries are compacted."""
    if "per_seed" in full:
        out = dict(full)
        out["per_seed"] = [compact(r) for r in full["per_seed"]]
        return out
    return compact(full)


def _sha256_file(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def certify_main(args) -> int:
    from harness.rl_isogeny.leading_forms import DEFAULT_PRIMES, certify_grid
    if args.bits:
        p, a, b = random_curve(args.bits, args.seed)
    else:
        p, a, b = args.p or 7127, args.a or 3, args.b or 5
    env = IsogenyPDPEnv(p, a, b, seed=args.seed, grid=GRIDS[args.grid], max_steps=1, n_null=1)
    primes = tuple(dict.fromkeys((p,) + tuple(DEFAULT_PRIMES)))
    t0 = time.time()
    certs = certify_grid(env.spec_list(), primes=primes, curves_per_prime=3, seed=args.seed)
    report = {
        "instrument": "tools/rl_isogeny_search.py --certify", "claim_tier": "toy (numbers); the lemma is scale-free",
        "primes": list(primes), "grid": args.grid,
        "lemma": ("for every presentation, the top-degree forms of the generators do not depend on the curve, so the "
                  "leading-form syzygy space K_D is class-constant, fall_dim(D) = dim K_D - (full-system syzygies at D), "
                  "and d_ff(real) >= d_ff(generic) for every curve over every prime field; excess_fall > 0 is "
                  "impossible for these presentations at any scale (harness/rl_isogeny/leading_forms.py)"),
        "certificates": {k: c.as_dict() for k, c in certs.items()},
        "all_hold": all(c.holds for c in certs.values()),
        "seconds": time.time() - t0,
    }
    text = json.dumps(report, indent=1, default=str)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    for k, c in certs.items():
        pf = c.per_prime
        print(f"{k:36s} holds={c.holds} predicted_first_fall={[x.predicted_first_fall for x in pf]} "
              f"measured={[x.measured_first_fall for x in pf]}")
    print(f"all_hold={report['all_hold']} primes={primes} ({report['seconds']:.1f}s)")
    return 0


def print_summary(report: dict) -> None:
    if "per_seed" in report:
        print(f"seeds={report['seeds']} envs={[ (e['p'], e['a'], e['b']) for e in report['environments']]}")
        for name, res in report["agents"].items():
            if "seeds" not in res:
                print(f"{name:10s} skipped: {res.get('skipped')}")
                continue
            line = (f"{name:10s} greedy hit {res['eval_planted_hit_rate']:.3f} by seed {res['eval_planted_hits_by_seed']} "
                    f"| stochastic hit {res['eval_stochastic_planted_hit_rate']:.3f} | train hit {res['train_planted_hit_rate']:.2f} "
                    f"| greedy final {res['eval_mean_final_score']:+.3f} | last-decile return {res['last_decile_mean_true_return']:+.3f}")
            if res.get("eval_fraction_final_optimal") is not None:
                line += (f" | final-optimal greedy {res['eval_fraction_final_optimal']:.2f} "
                         f"stochastic {res['eval_stochastic_fraction_final_optimal']:.2f}")
            print(line)
        if report["oracle"]:
            print(f"oracle {report['oracle']}")
        return
    env = report["environment"]
    print(f"p={env['p']} a={env['a']} b={env['b']} trace={env['trace']} start={env['start_spec']} "
          f"evaluations={report['meter']['evaluations']}")
    for name, res in report["agents"].items():
        if "train_summary" in res:
            ts, es = res["train_summary"], res["eval_summary"]
            line = (f"{name:10s} train best {ts['best_score']['mean']:+.3f}+-{ts['best_score']['sd']:.3f} "
                    f"hit {ts['planted_hit_rate']:.2f}")
            if es:
                line += f" | eval best {es['best_score']['mean']:+.3f} final {es['final_score']['mean']:+.3f} hit {es['planted_hit_rate']:.2f}"
            if "fraction_best_optimal" in ts:
                line += f" | best-optimal {ts['fraction_best_optimal']:.2f}"
            if es and "fraction_final_optimal" in es:
                line += (f" | final-optimal greedy {es['fraction_final_optimal']:.2f} "
                         f"stochastic {res['eval_stochastic_summary']['fraction_final_optimal']:.2f}")
            if res.get("eval_stochastic_summary"):
                line += f" | stochastic hit {res['eval_stochastic_summary']['planted_hit_rate']:.2f}"
            print(line)
    oracle = report.get("oracle")
    if oracle:
        print(f"oracle class_size={oracle['class_size']} certified={oracle['certified']} "
              f"best={oracle['best']['score']:+.3f} at {oracle['best']['spec']} j={oracle['best']['j']} "
              f"excess_constant={oracle['excess_constant_per_spec']} shape_spread_bits={oracle['max_shape_spread_bits']:.4f} "
              f"states_with_excess={len(oracle['states_with_excess'])}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--p", type=int)
    ap.add_argument("--a", type=int)
    ap.add_argument("--b", type=int)
    ap.add_argument("--bits", type=int, help="random generic curve at a random prime of this size")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--agents", default="random,tabular_q,ppo",
                    help="comma list from random,tabular_q,ppo (random is always run as the baseline)")
    ap.add_argument("--episodes", type=int, default=100)
    ap.add_argument("--eval-episodes", type=int, default=10)
    ap.add_argument("--max-steps", type=int, default=16)
    ap.add_argument("--grid", default="medium", choices=sorted(GRIDS))
    ap.add_argument("--primes", default="2,3,5,7")
    ap.add_argument("--null-kind", default="other_trace", choices=["other_trace", "curve_scramble"])
    ap.add_argument("--null-curves", type=int, default=2)
    ap.add_argument("--permuted", action="store_true")
    ap.add_argument("--planted", action="store_true")
    ap.add_argument("--plant-depth", type=int, default=3)
    ap.add_argument("--no-identity", action="store_true", help="drop the curve-identity hash bits")
    ap.add_argument("--start-spec", help="presentation every episode starts from: a grid label, 'worst' (the most "
                                         "expensive presentation on the input curve) or 'best'; default: first of the grid")
    ap.add_argument("--seeds", type=int, default=1,
                    help="run this many consecutive seeds (env and agents) and aggregate their summaries")
    ap.add_argument("--oracle", action="store_true", help="enumerate and score the whole class")
    ap.add_argument("--oracle-max-members", type=int, default=0)
    ap.add_argument("--w-excess", type=float, default=4.0)
    ap.add_argument("--w-deficit", type=float, default=0.5)
    ap.add_argument("--planted-bonus", type=float, default=6.0)
    ap.add_argument("--exact-trace-limit", type=int, default=1 << 17)
    ap.add_argument("--full-out", help="also write the FULL report (oracle row table, every training episode, "
                                      "evaluation trajectories) to this path; the summary written to --out records "
                                      "its sha256. The full report is regenerable from --seed and is not committed.")
    ap.add_argument("--summarize-full", help="rebuild the summary at --out from a FULL report written earlier "
                                             "by --full-out (no recomputation) and exit")
    ap.add_argument("--certify", action="store_true",
                    help="write the leading-form certificate for every presentation of the grid at the "
                         "environment's prime plus 32-, 48- and 56-bit primes, and exit (no agents)")
    ap.add_argument("--out")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    if args.certify:
        return certify_main(args)
    if args.summarize_full:
        with open(args.summarize_full) as fh:
            full = json.load(fh)
        report = summary_report(full)
        report["full_report"] = {"path": args.summarize_full, "sha256": _sha256_file(args.summarize_full)}
        text = json.dumps(report, indent=1, default=str)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            with open(args.out, "w") as fh:
                fh.write(text + "\n")
            print_summary(report)
            print(f"written {args.out} from {args.summarize_full}")
        else:
            print(text)
        return 0

    log = (lambda s: print(s, file=sys.stderr)) if args.verbose else (lambda s: None)
    t_all = time.time()
    reports = []
    for seed in range(args.seed, args.seed + max(1, args.seeds)):
        reports.append(run_one(args, seed, log))
    full = reports[0] if len(reports) == 1 else aggregate(reports, args)
    full["seconds_total"] = time.time() - t_all
    if args.full_out:
        Path(args.full_out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.full_out, "w") as fh:
            fh.write(json.dumps(full, indent=1, default=str) + "\n")
    report = summary_report(full)
    if args.full_out:
        report["full_report"] = {"path": args.full_out, "sha256": _sha256_file(args.full_out)}
    text = json.dumps(report, indent=1, default=str)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
        print_summary(report)
        print(f"written {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
