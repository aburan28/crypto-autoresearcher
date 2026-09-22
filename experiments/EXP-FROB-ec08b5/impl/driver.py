#!/usr/bin/env python3
"""EXP-FROB-ec08b5 driver: the Frobenius-stable factor-base design space.

Runs under `sage -python`.  Five phases, each checkpointed to
<run-dir>/checkpoint/<phase>.json so an interrupted run resumes instead of
restarting; --resume picks up whatever is already complete.

Output is BOUNDED BY CONSTRUCTION.  Nothing per-element, per-tuple or per-point
is streamed; every phase emits aggregate counters plus a fixed number of witness
records.  (The predecessor lane EXP-FROB-d8aa37 streamed one JSON record per
signed tuple, which is why its stage0 produced a 2.44 GB partial artifact and
never reached a checker in nineteen launches.)

No claim here is an attack, a solved discrete log, or a relation: every phase is
an exact structural census.  Timeouts and interrupts are recorded as
infrastructure status, never as mathematical evidence.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))

EXPERIMENT = "EXP-FROB-ec08b5"
SOURCES = ("lattice.py", "orbits.py", "analysis.py", "verify_field.py",
           "curve_panel.py", "driver.py")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


class Checkpoints:
    def __init__(self, run_dir, resume):
        self.dir = Path(run_dir) / "checkpoint"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.resume = resume

    def get(self, phase):
        p = self.dir / f"{phase}.json"
        if self.resume and p.exists():
            return json.loads(p.read_text())
        return None

    def put(self, phase, payload):
        p = self.dir / f"{phase}.json"
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(canonical(payload))
        tmp.replace(p)


# ---------------------------------------------------------------- phase 1 ----
def phase_self_test():
    """Fixed fixtures with hand-checkable answers. No panel data."""
    from lattice import attainable_dimensions, num_stable_subspaces, cyclotomic_cosets
    from orbits import orbit_census, orbit_census_burnside, all_stable_subspaces
    checks = []

    def ck(name, got, want):
        checks.append(dict(name=name, got=got, want=want, pass_=got == want))

    # T^7-1 over F_2 = (T-1)(T^3+T+1)(T^3+T^2+1): dims {0,1,3,4,6,7}, 8 divisors
    ck("dims(2,7)", attainable_dimensions(2, 7), [0, 1, 3, 4, 6, 7])
    ck("count(2,7)", num_stable_subspaces(2, 7), 8)
    # 2 is a primitive root mod 131 -> Phi_131 irreducible
    ck("dims(2,131)", attainable_dimensions(2, 131), [0, 1, 130, 131])
    ck("count(2,131)", num_stable_subspaces(2, 131), 4)
    # T^4-1 = (T-1)^4 over F_2: divisors 1,(T-1),...,(T-1)^4 -> 5 stable subspaces
    ck("count(2,4)", num_stable_subspaces(2, 4), 5)
    ck("dims(2,4)", attainable_dimensions(2, 4), [0, 1, 2, 3, 4])
    # 2-cyclotomic cosets mod 7
    ck("cosets(2,7)", cyclotomic_cosets(2, 7), [(0,), (1, 2, 4), (3, 5, 6)])
    # the unique stable line over F_2 at n=7 is fixed pointwise
    line = [s for s in all_stable_subspaces(2, 7) if sum(len(c) for c in s) == 1]
    ck("unique stable line at (2,7)", len(line), 1)
    ck("stable line is fixed pointwise", orbit_census(2, 7, line[0])["max_orbit_size"], 1)
    # the two derivations agree on a fixed fixture
    full = tuple(cyclotomic_cosets(2, 7))
    ck("totient == burnside on F_128",
       orbit_census(2, 7, full), orbit_census_burnside(2, 7, full))
    return dict(checks=checks, all_pass=all(c["pass_"] for c in checks))


# ---------------------------------------------------------------- phase 2 ----
def phase_lattice_crosscheck(cells, exhaustive_max):
    """Methods A (divisors) / B (closure) / C (exhaustive) / O (direct orbits)."""
    from math import gcd
    from collections import Counter
    from verify_field import setup, method_B_closure, method_C_exhaustive, method_O_orbits
    from lattice import attainable_dimensions, num_stable_subspaces
    from orbits import all_stable_subspaces, orbit_census

    rows = []
    for q, n in cells:
        t0 = time.perf_counter()
        e = setup(q, n)
        B = method_B_closure(e, n)
        row = dict(q=q, n=n, field_size=q ** n,
                   A_count=num_stable_subspaces(q, n),
                   A_dims=attainable_dimensions(q, n),
                   B_count=len(B), B_dims=sorted(set(B.values())),
                   C_count=None, C_agrees=None,
                   orbit_census_agrees=None, gcd_qn=gcd(q, n))
        row["AB_agrees"] = (row["A_count"] == row["B_count"] and row["A_dims"] == row["B_dims"])
        if q ** n <= exhaustive_max:
            C = method_C_exhaustive(e, n)
            row["C_count"] = len(C)
            row["C_agrees"] = set(C) == set(B)
        if gcd(q, n) == 1:
            analytic = Counter(tuple(sorted(orbit_census(q, n, s)["elements_by_orbit_size"].items()))
                               for s in all_stable_subspaces(q, n))
            direct = Counter(tuple(sorted(method_O_orbits(e, k).items())) for k in B)
            row["orbit_census_agrees"] = analytic == direct
        row["wall_seconds"] = round(time.perf_counter() - t0, 3)
        row["cell_agrees"] = all(v for v in (row["AB_agrees"], row["C_agrees"],
                                             row["orbit_census_agrees"]) if v is not None)
        rows.append(row)
    return dict(cells=rows, all_agree=all(r["cell_agrees"] for r in rows))


# ---------------------------------------------------------------- phase 3 ----
def phase_census_crosscheck(cells):
    """Totient derivation vs Burnside derivation, every stable subspace."""
    from orbits import all_stable_subspaces, orbit_census, orbit_census_burnside
    rows, total, bad = [], 0, 0
    for q, n in cells:
        subs = all_stable_subspaces(q, n)
        mism = 0
        for s in subs:
            if orbit_census(q, n, s) != orbit_census_burnside(q, n, s):
                mism += 1
        rows.append(dict(q=q, n=n, subspaces=len(subs), mismatches=mism))
        total += len(subs)
        bad += mism
    return dict(cells=rows, subspaces_compared=total, mismatches=bad, all_agree=bad == 0)


# ---------------------------------------------------------------- phase 4 ----
def phase_curve_panel(cells, seed):
    """Real curves, real factor bases, measured pi-orbits, with two controls."""
    from collections import Counter
    from curve_panel import (env, ordinary_subfield_curves, non_subfield_curve,
                             stable_subspace, random_unstable_subspace,
                             factor_base, pi_orbits)
    rows = []
    for (q, n, dim) in cells:
        e = env(q, n)
        k, K = e["k"], e["K"]
        S = stable_subspace(e, dim)
        if S is None:
            rows.append(dict(q=q, n=n, dim=dim, skipped="dimension not attainable"))
            continue
        U = random_unstable_subspace(e, dim, seed=seed)
        for ci, E in enumerate(ordinary_subfield_curves(k, limit=2)):
            EK = E.base_extend(K)
            Fb = factor_base(EK, e, S)
            orbs, stable = pi_orbits(EK, Fb, q)
            # exact point-level prediction for n an odd prime:
            #   fixed points are exactly the affine points of E(F_q) inside F_V,
            #   every other orbit has length exactly n
            fixed = [P for P in Fb if P[0] in k and P[1] in k]
            predicted_orbits = (len(fixed) + (len(Fb) - len(fixed)) // n
                                if (len(Fb) - len(fixed)) % n == 0 else None)
            row = dict(q=q, n=n, dim=dim, curve_index=ci,
                       curve=[str(a) for a in E.a_invariants()],
                       j_invariant=str(E.j_invariant()),
                       group_order=int(EK.order()),
                       factor_base_size=len(Fb),
                       pi_stable=stable,
                       fixed_points=len(fixed),
                       measured_orbits=(len(orbs) if orbs is not None else None),
                       predicted_orbits=predicted_orbits,
                       prediction_exact=(orbs is not None and predicted_orbits == len(orbs)),
                       orbit_size_histogram=(dict(sorted(Counter(orbs).items()))
                                             if orbs is not None else None),
                       measured_reduction=(len(Fb) / len(orbs) if orbs else None))
            # control 1: a random NON-stable V of the same dimension
            if U is not None:
                FbU = factor_base(EK, e, U)
                _, stU = pi_orbits(EK, FbU, q)
                row["control_unstable_V"] = dict(factor_base_size=len(FbU), pi_stable=stU,
                                                 control_passes=(stU is False))
            # control 2: the NULL OBJECT -- a curve over F_{q^n} and over no subfield
            try:
                En = non_subfield_curve(K, k, seed=seed)
                FbN = factor_base(En, e, S)
                _, stN = pi_orbits(En, FbN, q)
                row["control_null_curve"] = dict(j_in_subfield=False,
                                                 factor_base_size=len(FbN),
                                                 pi_stable=stN,
                                                 control_passes=(stN is False))
            except Exception as exc:
                row["control_null_curve"] = dict(error=str(exc)[:200])
            rows.append(row)
    scored = [r for r in rows if "skipped" not in r]
    return dict(cells=rows,
                cells_measured=len(scored),
                prediction_exact_on_all=all(r["prediction_exact"] for r in scored),
                stable_V_always_pi_stable=all(r["pi_stable"] for r in scored),
                unstable_control_always_fails=all(
                    r.get("control_unstable_V", {}).get("control_passes", True) for r in scored),
                null_curve_control_always_fails=all(
                    r.get("control_null_curve", {}).get("control_passes", True) for r in scored))


# ---------------------------------------------------------------- phase 5 ----
def phase_target_table(targets, m_values, m_cap):
    """Attainability and net-win verdict at real and toy extension degrees."""
    from analysis import spectrum, verdict, min_faithful_dimension, max_usable_m, _ord
    rows = []
    for q, n, note in targets:
        sp = spectrum(q, n)
        d = _ord(q, n)
        rows.append(dict(
            q=q, n=n, note=note, ord_n_q=d, irreducible_factors_of_phi_n=(n - 1) // d,
            stable_subspace_count=2 ** (1 + (n - 1) // d),
            attainable_dimensions=(sp and sorted(sp)),
            min_faithful_dimension=min_faithful_dimension(q, n, sp),
            max_m_with_net_win=max_usable_m(q, n, sp, m_cap=m_cap),
            m_cap_used=m_cap,
            verdicts=[verdict(q, n, m, sp) for m in m_values]))
    return dict(targets=rows)


# --------------------------------------------------------------------------- #
PHASES = ("self_test", "lattice_crosscheck", "census_crosscheck",
          "curve_panel", "target_table")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--plan", required=True, help="frozen trial plan JSON")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(Path(args.plan).read_text())
    panel = plan["panel"]
    cp = Checkpoints(run_dir, args.resume)

    here = Path(__file__).resolve().parent
    receipt = dict(
        experiment=EXPERIMENT, run_id=plan["run_id"], trial_plan=str(args.plan),
        trial_plan_sha256=sha(args.plan), started_at=stamp(),
        source_sha256={s: sha(here / s) for s in SOURCES},
        python=sys.version, platform=platform.platform(),
        sage=os.environ.get("SAGE_VERSION", "sage -python"),
        seed=panel["seed"], phases={}, status="running")

    results, failed = {}, None
    for name in PHASES:
        done = cp.get(name)
        if done is not None:
            results[name] = done["result"]
            receipt["phases"][name] = dict(done["meta"], resumed=True)
            continue
        t0 = time.perf_counter()
        try:
            if name == "self_test":
                r = phase_self_test()
            elif name == "lattice_crosscheck":
                r = phase_lattice_crosscheck([tuple(c) for c in panel["lattice_cells"]],
                                             panel["exhaustive_max_field_size"])
            elif name == "census_crosscheck":
                r = phase_census_crosscheck([tuple(c) for c in panel["census_cells"]])
            elif name == "curve_panel":
                r = phase_curve_panel([tuple(c) for c in panel["curve_cells"]], panel["seed"])
            elif name == "target_table":
                r = phase_target_table([tuple(t) for t in panel["targets"]],
                                       panel["m_values"], panel["m_cap"])
        except Exception:
            failed = dict(phase=name, traceback=traceback.format_exc()[-4000:])
            receipt["phases"][name] = dict(status="error",
                                           wall_seconds=round(time.perf_counter() - t0, 3))
            break
        meta = dict(status="ok", wall_seconds=round(time.perf_counter() - t0, 3),
                    completed_at=stamp(), resumed=False)
        cp.put(name, dict(result=r, meta=meta))
        results[name] = r
        receipt["phases"][name] = meta

    receipt["finished_at"] = stamp()
    receipt["status"] = "error" if failed else "completed"
    if failed:
        receipt["failure"] = failed
        receipt["infrastructure_note"] = (
            "A phase failed. Per AGENTS.md this is an execution status, NOT negative "
            "mathematical evidence about any hypothesis.")
    (run_dir / "raw-result.json").write_text(json.dumps(results, indent=1, sort_keys=True))
    receipt["raw_result_sha256"] = sha(run_dir / "raw-result.json")
    (run_dir / "execution-receipt.json").write_text(json.dumps(receipt, indent=1, sort_keys=True))
    print(json.dumps({k: (v.get("all_agree", v.get("all_pass", "see raw-result")))
                      for k, v in results.items() if isinstance(v, dict)}, indent=1))
    print("status:", receipt["status"])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
