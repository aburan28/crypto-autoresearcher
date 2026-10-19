#!/usr/bin/env python3
"""Independent re-derivation of the frozen EXP-ECDLP-8c41d7 criteria (Validator, check 4).

Written BEFORE opening experiments/EXP-ECDLP-8c41d7/analyze.py.  Reads only
runs/RUN-ECDLP-8c41d7-0{1..4}/raw-result.jsonl.

Source map (AMD-01..03, see validation.md): L=2 <- RUN-01; L=3 <- RUN-02;
L=4 Singular arms <- RUN-03 (p=65551); L=4 msolve arms <- RUN-04 (p=262271).
RUN-03's msolve rows (rc -11) are instrument failures excluded by AMD-03.
This map is written out explicitly (it does NOT use the 'later run wins' rule),
and is cross-checked against the 'later run wins' rule at the end.

Definitions (mine, from the frozen text in specification.yaml):
  non-degenerate instance : results[arm].status != 'degenerate_target'
  completed instance      : status == 'ok'
  jointly completed cell  : both arms of the pair have >= 1 ok instance in that L.
                            (strict variant: all non-degenerate instances ok for both)
  median                  : median wall_s over ok instances of the arm in the cell
  retired at L            : every non-degenerate instance of the cell has status 'timeout'
                            (lenient variant: no instance 'ok')
"""
import json, statistics, sys, glob, os

ROOT = "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-8c41d7/runs"
MS = ("A_elim_ms", "A_drl_ms", "B_ms")
SG = ("A_block_sg", "B_sg")
ARMS = MS + SG
CAP = 600.0


def load(run):
    return [json.loads(l) for l in open(f"{ROOT}/RUN-ECDLP-8c41d7-{run:02d}/raw-result.jsonl")]


def build_map():
    """cells[L][arm] = list of (inst, status, wall_s, p)"""
    src = {(2, a): 1 for a in ARMS}
    src.update({(3, a): 2 for a in ARMS})
    src.update({(4, a): 3 for a in SG})
    src.update({(4, a): 4 for a in MS})
    runs = {r: load(r) for r in (1, 2, 3, 4)}
    cells = {}
    for (L, arm), r in sorted(src.items()):
        rows = [x for x in runs[r] if x["L"] == L]
        assert len(rows) == 6, (L, arm, r, len(rows))
        cells.setdefault(L, {})[arm] = [
            (x["inst"], x["results"][arm]["status"], x["results"][arm].get("wall_s"), x["p"]) for x in rows]
    return cells, runs


def later_run_wins(runs):
    cells = {}
    for r in (1, 2, 3, 4):
        for x in runs[r]:
            for arm, res in x["results"].items():
                cells.setdefault(x["L"], {}).setdefault(arm, {})[x["inst"]] = (r, res["status"], res.get("wall_s"), x["p"])
    return cells


def stats(rows, cap=CAP):
    """rows: list of (inst,status,wall,p).  Treat ok with wall>cap as timeout (what-if cap)."""
    nd = [r for r in rows if r[1] != "degenerate_target"]
    def eff(r):
        return "timeout" if (r[1] == "ok" and r[2] > cap) else r[1]
    ok = [r for r in nd if eff(r) == "ok"]
    return dict(n_nd=len(nd), n_ok=len(ok),
                n_timeout=sum(1 for r in nd if eff(r) == "timeout"),
                n_other=sum(1 for r in nd if eff(r) not in ("ok", "timeout")),
                other=sorted({eff(r) for r in nd if eff(r) not in ("ok", "timeout")}),
                median=(statistics.median([r[2] for r in ok]) if ok else None),
                walls=[r[2] for r in ok])


def verdict(cells, cap=CAP, strict_joint=False, strict_retire=True, quiet=True):
    out = {}
    Ls = sorted(cells)
    def retired_L(arm):
        for L in Ls:
            s = stats(cells[L][arm], cap)
            if s["n_nd"] == 0:
                continue
            if strict_retire:
                if s["n_timeout"] == s["n_nd"]:
                    return L
            else:
                if s["n_ok"] == 0:
                    return L
        return None  # not retired in the grid -> L > max
    def completed_L(arm):
        best = None
        for L in Ls:
            s = stats(cells[L][arm], cap)
            if s["n_ok"] > 0:
                best = L
        return best
    def joint_cells(a, b):
        res = []
        for L in Ls:
            sa, sb = stats(cells[L][a], cap), stats(cells[L][b], cap)
            if strict_joint:
                ok = sa["n_ok"] == sa["n_nd"] and sb["n_ok"] == sb["n_nd"] and sa["n_nd"] > 0
            else:
                ok = sa["n_ok"] > 0 and sb["n_ok"] > 0
            if ok:
                res.append((L, sa["median"], sb["median"]))
        return res
    for name, a, b in (("msolve", "A_elim_ms", "B_ms"), ("singular", "A_block_sg", "B_sg")):
        jc = joint_cells(a, b)
        a_below_all = all(ma < mb for _, ma, mb in jc) if jc else None
        a_ge_all = all(ma >= mb for _, ma, mb in jc) if jc else None
        ra, rb = retired_L(a), retired_L(b)
        INF = 10 ** 9
        ra_n, rb_n = (ra if ra is not None else INF), (rb if rb is not None else INF)
        ca, cb = completed_L(a), completed_L(b)
        succ = bool(a_below_all) and (ca is not None and cb is not None and ca >= cb)
        fals_c1 = bool(a_ge_all)
        fals_c2 = ra_n < rb_n
        out[name] = dict(joint=jc, a_below_all=a_below_all, a_ge_all=a_ge_all, retired_L=(ra, rb),
                         largest_completed_L=(ca, cb), success=succ, falsif_clause1=fals_c1,
                         falsif_clause2=fals_c2, falsification=fals_c1 or fals_c2)
    # dynamic range control: median(A_drl_ms / A_elim_ms) at largest L where both complete
    Lboth = [L for L in Ls if stats(cells[L]["A_drl_ms"], cap)["n_ok"] > 0 and stats(cells[L]["A_elim_ms"], cap)["n_ok"] > 0]
    if Lboth:
        L = max(Lboth)
        drl = {r[0]: r[2] for r in cells[L]["A_drl_ms"] if r[1] == "ok"}
        el = {r[0]: r[2] for r in cells[L]["A_elim_ms"] if r[1] == "ok"}
        common = sorted(set(drl) & set(el))
        ratios = [drl[i] / el[i] for i in common]
        med_of_ratio = statistics.median(ratios)
        ratio_of_med = stats(cells[L]["A_drl_ms"], cap)["median"] / stats(cells[L]["A_elim_ms"], cap)["median"]
        out["dynamic_range"] = dict(L=L, n=len(common), median_of_ratios=med_of_ratio, ratio_of_medians=ratio_of_med,
                                    ratios=[round(x, 3) for x in ratios], pass_ge_2=med_of_ratio >= 2)
    out["A_drl_retired_L"] = (retired_L("A_drl_ms"), retired_L("A_drl_ms"))
    return out


def report(cells):
    print("== per cell / arm (source map) ==")
    for L in sorted(cells):
        for arm in ARMS:
            s = stats(cells[L][arm])
            ps = sorted({r[3] for r in cells[L][arm]})
            print(f"L={L} {arm:11s} p={ps} nd={s['n_nd']} ok={s['n_ok']} timeout={s['n_timeout']} other={s['other']} "
                  f"median_ok={s['median']} walls={s['walls']}")
    print()


def main():
    cells, runs = build_map()
    report(cells)
    print("== ratios A/B of medians per jointly completed cell ==")
    v = verdict(cells)
    for k in ("msolve", "singular"):
        for L, ma, mb in v[k]["joint"]:
            print(f"{k} L={L}: median A={ma} B={mb} ratio A/B={ma/mb:.3f}")
    print()
    print("== verdict @ cap 600 (strict_retire, lenient joint) ==")
    print(json.dumps(v, indent=1, default=str))
    print()
    print("== variants ==")
    for sj in (False, True):
        for sr in (True, False):
            vv = verdict(cells, strict_joint=sj, strict_retire=sr)
            print(f"strict_joint={sj} strict_retire={sr}:",
                  {k: dict(succ=vv[k]["success"], fals=vv[k]["falsification"], c1=vv[k]["falsif_clause1"],
                           c2=vv[k]["falsif_clause2"], retired=vv[k]["retired_L"], completed=vv[k]["largest_completed_L"])
                   for k in ("msolve", "singular")})
    print()
    print("== cap sensitivity (ok rows with wall_s > cap re-labelled timeout; informational what-if) ==")
    for cap in (600, 590, 587, 586, 585, 584, 583, 582, 560, 540, 530, 529, 528, 525, 520, 519, 518, 500):
        vv = verdict(cells, cap=cap)
        print(f"cap={cap:4d}: B_ms retired at L={vv['msolve']['retired_L'][1]} ; A_elim retired L={vv['msolve']['retired_L'][0]} ; "
              f"B_ms largest completed L={vv['msolve']['largest_completed_L'][1]} ; "
              f"fals_clause1={vv['msolve']['falsif_clause1']} fals_clause2={vv['msolve']['falsif_clause2']} "
              f"success={vv['msolve']['success']} ; singular fals={vv['singular']['falsification']} succ={vv['singular']['success']}")
    print()
    print("== cross-check: 'later run wins' rule per (L, arm, inst) ==")
    lw = later_run_wins(runs)
    mism = 0
    for L in sorted(lw):
        for arm in lw[L]:
            for inst, (r, st, wall, p) in sorted(lw[L][arm].items()):
                mine = [x for x in cells[L][arm] if x[0] == inst]
                if not mine:
                    continue
                if (mine[0][1], mine[0][2], mine[0][3]) != (st, wall, p):
                    mism += 1
                    print("MISMATCH", L, arm, inst, r, (st, wall, p), mine[0])
    print("mismatches vs later-run-wins:", mism)
    print()
    print("== instrument failures excluded (RUN-03 msolve rows, L=4, p=65551) ==")
    from collections import Counter
    c = Counter()
    for x in runs[3]:
        for arm in MS:
            c[(arm, x["results"][arm]["status"])] += 1
    print(dict(c))


if __name__ == "__main__":
    main()
