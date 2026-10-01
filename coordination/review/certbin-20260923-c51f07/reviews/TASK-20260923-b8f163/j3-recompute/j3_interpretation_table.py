#!/usr/bin/env python3
"""TASK-20260923-b8f163 J3 deliverable: the per-interpretation table.

For I-4, I-5, I-11, I-12, I-14, I-15 and I-24 (plus two points the plan named:
the M3 ratio-rule bullet overlap and the median convention): the reading as run,
the alternative reading, and the affected verdicts under each. Uses the
validator's own numbers (j3_recompute.json) and recomputes the M2 variants with
the validator's own affine forms. No producer code. Zero trials; no RUN-id.
Writes j3_interpretation_table.json and j3_interpretation_table.txt.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import j3_recompute as R  # noqa: E402  (validator's own module)


def dr2(rf, p2, m3kind, mode):
    """DR-2 per spec text. m3kind: 'zero' (bullet 1) or 'not_estimable' (bullet 3).
    mode 'as_run' = trial-plan I-24; 'strict' = any unevaluable clause -> not evaluable."""
    fal = [rf >= 0.5, p2["median"] < 0.2, False if m3kind == "zero" else None]
    con = [rf <= 0.01, p2["frac_in_band"] >= 0.9, False if m3kind == "zero" else True]
    if any(c is True for c in fal):
        return "E1 FALSIFIED"
    if mode == "strict" and any(c is None for c in fal + con):
        return "not evaluable"
    if all(c is True for c in con):
        return "E1 CONSISTENT"
    return "between"


def dr4(p2):
    if p2["n"] == 0:
        return "not evaluable"
    if p2["median"] < 0.2:
        return "H1 FALSIFIED"
    if p2["frac_in_band"] >= 0.9:
        return "H1 SUPPORTED at this cell"
    return "not supported, not falsified"


def main():
    J3 = json.load(open(os.path.join(HERE, "j3_recompute.json")))
    recs, refs = R.load()
    curve = json.load(open(os.path.join(R.RUN, "curve.json")))
    import gzip
    oplogs = {}
    with gzip.open(os.path.join(R.RUN, "F-S3-reference-oplogs-D4.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            oplogs.setdefault(r["ref"], []).append(r)
    for lab in oplogs:
        lst = sorted(oplogs[lab], key=lambda r: r["k"])
        oplogs[lab] = [(r["p"], r["c"], r["X"]) for r in lst]
    labels5 = ["U1", "U2", "U3", "S1", "S2"]
    forms, _ = R.forms_for_refs(curve["B"], oplogs, labels5)
    tg = sorted([r for r in recs["F-S3"] if r["D"] == 4], key=lambda r: r["idx"])
    E = {lab: {r["idx"]: R.eval_e(*forms[lab], r["x_R"]) for r in tg} for lab in labels5}

    def p2(filter_, basis):
        hs, window = [], []
        for lab in labels5:
            a0, a = forms[lab]
            K = len(a)
            ev = [E[lab][r["idx"]] for r in tg if filter_(r)]
            S, Z, _ = R.hazards(ev, K)
            if basis == "all":
                dep = [len({e[k] for e in ev}) == 2 for k in range(K)]
            elif basis == "survivors":
                dep = [0 < Z[k] < S[k] for k in range(K)]
            else:  # rank-increasing
                bas, dep = {}, []
                for k in range(K):
                    v, inc = a[k], False
                    while v:
                        hb = v.bit_length() - 1
                        if hb in bas:
                            v ^= bas[hb]
                        else:
                            bas[hb] = v
                            inc = True
                            break
                    dep.append(inc)
            for k in range(K):
                if dep[k] and S[k] >= 200:
                    hs.append(Z[k] / S[k])
                if dep[k] and 193 <= S[k] < 200:
                    window.append({"ref": lab, "k": k, "S_k": S[k]})
        n = len(hs)
        return {"n": n, "median": R.median(hs), "frac_in_band": (sum(1 for h in hs if 0.4 <= h <= 0.6) / n) if n else None,
                "n_zero": sum(1 for h in hs if h == 0), "in_band_h": sorted(h for h in hs if 0.4 <= h <= 0.6),
                "dependent_pivots_with_S_k_in_[193,199]": window}

    nd = lambda r: not r["degenerate"]  # noqa: E731
    P = {
        "as_run: dependence over all non-degenerate targets, arms pooled (spec text)": p2(nd, "all"),
        "alt: dependence over replay survivors (contradicts 'over the family's non-degenerate targets'; the spec reserves this basis for F-NULLF2)": p2(nd, "survivors"),
        "alt: S_k over the unsat arm only (contradicts 'both arms pooled')": p2(lambda r: nd(r) and r["s"] == 0, "all"),
        "READING owned by J4, not a rule: rank-increasing pivots only": p2(nd, "rank"),
    }
    rf = J3["retention_family"]["F-S3/D4/strict"]["value"]
    combos = {}
    for pname, st in P.items():
        combos[pname] = {"P2": {k: v for k, v in st.items() if k != "in_band_h"}, "DR-4": dr4(st),
                         "DR-2": {f"M3 {m} / I-24 {mode}": dr2(rf, st, m, mode)
                                  for m in ("zero", "not_estimable") for mode in ("as_run", "strict")}}
    asrun = P[list(P)[0]]
    edge = min(min(abs(h - 0.4), abs(h - 0.6)) for h in asrun["in_band_h"])

    V = J3["DR_validator"]["verdicts"]
    S = J3["sensitivity"]
    table = [
        {"id": "I-4", "as_run": "Degenerate targets (x_R in V; 7 of 1000 in F-S3) are kept as their own stratum and excluded from arms, entropy and M2.",
         "alternative": "(A) include degenerate targets in the arms, entropy and M2 pools; (B) replace degenerate draws by further S_test draws so that 1000 targets are non-degenerate.",
         "recomputed": {"A_retention_unsat_D4_strict": S["I-4"]["alt_A_retention_unsat_D4_strict"],
                        "A_P2": {k: S["I-4"]["alt_A_P2"][k] for k in ("n", "median", "frac_in_band")},
                        "A_H_T_strict_D4": S["I-4"]["alt_A_M4_F-S3_D4_strict"],
                        "B_bound_max_retention_family": S["I-4"]["alt_B_max_retention_family"],
                        "B_P2_membership": "at most 7 added targets; no P2 pair has S_k within 7 of 200, and the dependent pivots with S_k in [193, 199] that could enter are listed in the as-run P2 row; the 11 exact-zero hazards cannot rise above 7/207 = 0.034, so the in-band fraction cannot reach 0.9",
                        "B_in_band_min_distance_to_edge": edge},
         "verdicts_as_run": {k: V[k] for k in ("DR-1", "DR-2", "DR-3", "DR-4")},
         "verdicts_alternative": {"A": {k: S["I-4"]["alt_A_verdicts"][k] for k in ("DR-1", "DR-2", "DR-3", "DR-4")},
                                  "B": "DR-1 FALSIFIED (retention <= 0.018 < 0.5); DR-3 E2 FALSIFIED; DR-2 between; DR-4 not supported, not falsified (bounded, not computed; zero-trial task)"},
         "flip": False},
        {"id": "I-5", "as_run": S["I-5"]["as_run"], "alternative": S["I-5"]["alternative"],
         "recomputed": S["I-5"]["fact"], "flip": False},
        {"id": "I-11", "as_run": S["I-11"]["as_run"],
         "alternative": "any other tied reference (U2, U3, modal) as maximizing; or the sat references S1, S2",
         "recomputed": S["I-11"]["verdicts_by_ref"], "flip": False,
         "note": "All four M1 counts are 0, so the tie-break selects the reference. DR-3 E2 FALSIFIED, DR-6 FAILS/FAILS and DR-7 not closed/not closed under every choice. Pruned dense bytes 1,266,915-1,267,864; saving_strict 33.59-35.66; saving_set 1.6578-1.6603."},
        {"id": "I-12", "as_run": S["I-12"]["as_run"], "alternative": S["I-12"]["alternative"],
         "recomputed": "not triggered: the F-S3 numerator count is 0, so the lower-bound case does not arise", "flip": False},
        {"id": "I-14", "as_run": "Modal hazards use targets 101..N. r-dependence is taken over the scored non-degenerate targets. Only the 5 F-S3 references enter P2.",
         "alternative": "(a) modal hazards over all targets; (b) P2-set variants listed under M2_variants",
         "recomputed": {"(a)": "the modal is not in the P2 set, so no DR moves (first-3 modal hazards over all targets are recorded in j3_recompute.json)",
                        "M2_variants": combos},
         "flip": "No DR flips under any reading consistent with the spec text. DR-4 reads 'H1 SUPPORTED at this cell' under the three text-incompatible P2 definitions. Combined with bullet-3 M3, those definitions also turn DR-2 into 'E1 CONSISTENT'. See finding F-J3-2."},
        {"id": "I-15", "as_run": S["I-15"]["as_run"], "alternative": "CP 99.9% interval of the observed proportion containing 2^-K_rank; exact two-sided p-value",
         "recomputed": S["I-15"]["alternatives"], "flip": False, "note": S["I-15"]["note"]},
        {"id": "I-24", "as_run": "DR-2: a clause that cannot be evaluated makes the verdict 'not evaluable' only if no evaluable clause decides it; the M3 consistency clause accepts 'not estimable'. DR-3: a not-estimable M3 leaves the M3 clauses unknown.",
         "alternative": "strict handling: any unevaluable clause makes DR-2 'not evaluable'",
         "recomputed": {k: v for k, v in combos[list(P)[0]]["DR-2"].items()},
         "flip": "DR-2 changes label from 'between' to 'not evaluable' only under strict handling combined with the bullet-3 M3 reading the run used. Neither label falsifies or supports E1. DR-3 is decided by retention_family < 0.5 under every reading."},
        {"id": "M3-bullet-overlap (not in I-1..I-25)", "as_run": "producer: bullet 3 'both 0: not estimable' takes precedence (analysis.py:274-278)",
         "alternative": "bullet 1 'numerator count 0: ratio is 0' takes precedence",
         "recomputed": "observed counts: numerator 0/386; denominators 0/115, 0/126, 0/127",
         "flip": "At the as-run P2 set, no flip under either precedence (DR-2 between, DR-3 E2 FALSIFIED, DR-5 not applicable). The precedence decides DR-2 only jointly with a text-incompatible P2 definition."},
        {"id": "median convention (not an I-item)", "as_run": "average of the two middle values (0.4817)", "alternative": "lower median (0.4739)",
         "flip": False},
    ]
    out = {"table": table, "as_run_P2": {k: v for k, v in asrun.items() if k != "in_band_h"},
           "in_band_h_values": asrun["in_band_h"], "in_band_min_distance_to_edge": edge}
    json.dump(out, open(os.path.join(HERE, "j3_interpretation_table.json"), "w"), indent=1)
    with open(os.path.join(HERE, "j3_interpretation_table.txt"), "w") as fh:
        for row in table:
            fh.write(f"== {row['id']}\n  as run: {row['as_run']}\n  alternative: {row['alternative']}\n  flip: {row['flip']}\n")
        fh.write("\n== I-14 / I-24 matrix (DR-4; DR-2 by M3 reading x I-24 handling)\n")
        for pname, c in combos.items():
            fh.write(f"  {pname}\n    P2 n={c['P2']['n']} median={c['P2']['median']} frac_in_band={c['P2']['frac_in_band']} zeros={c['P2']['n_zero']}\n")
            fh.write(f"    DR-4: {c['DR-4']}\n")
            for k, v in c["DR-2"].items():
                fh.write(f"    DR-2 [{k}]: {v}\n")
    print(open(os.path.join(HERE, "j3_interpretation_table.txt")).read())
    print("as-run P2 window candidates:", asrun["dependent_pivots_with_S_k_in_[193,199]"], "edge distance:", edge)


if __name__ == "__main__":
    main()
