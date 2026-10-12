"""Implementation smoke checks (TASK-20260928-c7aad3). NOT a scientific run.

L = 8, seed 1 fixture only; every label in the 'smoke|EXP-SDEG-85eefd/v2'
namespace (never the frozen planted/random/rho labels). Reports identity and
backend-agreement results only; computes no beta across sizes.

Usage: python3 smoke.py [--per-deck 16] [--skip-sage | --no-sage] [--out-dir DIR]
Writes DIR/smoke_results.json, DIR/cells/*.json and DIR/opcounts.json (the
canonical per-query op counts used for the cross-host identity check).
--no-sage is the pod path: no fixture reproduction, no Sage elimination; the
B2 split cross-check runs without Sage (b2split.py) on every query.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit  # noqa: E402
import backends  # noqa: E402
import cellrun  # noqa: E402
import decks as decks_mod  # noqa: E402
import fixtures  # noqa: E402
import labels  # noqa: E402
import rho  # noqa: E402
import semaev  # noqa: E402
from verify import O, VCurve  # noqa: E402

OUT = HERE / "smoke"  # overridden by --out-dir
NS = labels.SMOKE_NS


def safe_write(path, text, retries=180, wait=10):
    """The shared repo volume intermittently hits 0 bytes free (other processes);
    retry ENOSPC instead of losing the smoke output."""
    for i in range(retries):
        try:
            Path(path).write_text(text)
            return
        except OSError as e:
            if e.errno != 28 or i == retries - 1:
                raise
            print(f"ENOSPC writing {path}; retry {i + 1}", file=sys.stderr, flush=True)
            time.sleep(wait)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-deck", type=int, default=16)
    ap.add_argument("--skip-sage", action="store_true")
    ap.add_argument("--rho-targets", type=int, default=8)
    ap.add_argument("--fglm-per-deck", type=int, default=1,
                    help="literal Singular GB+FGLM elimination on the first N queries of each |V|>4 deck "
                         "(all queries of |V|<=4 decks); 'split' runs on every query")
    ap.add_argument("--no-sage", action="store_true",
                    help="host without Sage: skip fixture reproduction and Sage B2 entirely")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    global OUT
    if args.out_dir:
        OUT = Path(args.out_dir).resolve()
        smoke_root = (HERE / "smoke").resolve()
        if OUT != smoke_root and smoke_root not in OUT.parents:
            raise SystemExit("--out-dir must be under implementation/smoke/")
    if args.no_sage:
        args.skip_sage = True
    OUT.mkdir(exist_ok=True)
    (OUT / "cells").mkdir(exist_ok=True)
    t0 = time.time()
    import hostinfo
    res = {"namespace": NS, "fixture": "L8-s1", "not_a_scientific_run": True,
           "reports": "identity and agreement only; no beta",
           "host": hostinfo.host_identity(), "no_sage": args.no_sage}

    # 1. fixture reproduction (C-1)
    if args.no_sage:
        res["fixture_reproduction"] = {"byte_identical": None, "note": "not run: host without Sage"}
    elif not args.skip_sage:
        res["fixture_reproduction"] = fixtures.reproduce(OUT / "fixture_reproduction.json")
    else:
        rp = OUT / "fixture_reproduction.json"
        res["fixture_reproduction"] = {
            "reproduced_sha256": hashlib.sha256(rp.read_bytes()).hexdigest() if rp.exists() else None,
            "byte_identical": rp.exists() and rp.read_bytes() == fixtures.FIXTURE_JSON.read_bytes(),
            "note": "from a previous sage run of the frozen generator"}
    print("fixture reproduction:", res["fixture_reproduction"]["byte_identical"], flush=True)

    fx = fixtures.fixture(8, 1)
    terms = semaev.load_terms()
    res["semaev_polys_sha256"] = fixtures.sha256_file(semaev.POLY_FILE)
    sem = semaev.SemaevFp(fx["p"], fx["a"], fx["b"], terms)
    res["semaev_nonzero_coefficients_Fp"] = sem.nonzero

    # 2. identity check (C-3)
    ident = semaev.identity_check(fx, sem, NS, 1000)
    res["identity_check"] = ident
    print("identity:", ident["passed"], ident["zero_nonzero_counts"], flush=True)
    if not ident["passed"]:
        safe_write(OUT / "smoke_results.json", json.dumps(res, indent=1, default=str))
        raise SystemExit("identity check failed")

    # 3. decks + cells
    all_decks = decks_mod.build_all(fx, NS)
    res["decks"] = {k: {"V": d.V, "size": d.size, "notes": d.notes,
                        "construction_ops": d.construction_ops} for k, d in all_decks.items()}
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    res["cells"] = {}
    sage_queries = []
    audit_results = []
    opcounts = []
    n_pl = args.per_deck // 2
    for name, deck in all_decks.items():
        # forward table sanity: every finite u is an S3 root of its witness pair
        tbl = backends.ForwardTable(fx, deck, build_poly=False)
        s3_ok = all(semaev.s3_value(fx["p"], fx["a"], fx["b"], deck.V[i1], deck.V[i2], u) == 0
                    for u, (i1, _, i2, _) in tbl.witness.items() if u != backends.INF_KEY)
        ids = [f"L8-s1-{name}-planted-{j:02d}" for j in range(n_pl)] + \
              [f"L8-s1-{name}-random-{j:02d}" for j in range(args.per_deck - n_pl)]
        cell = cellrun.run_cell(fx, deck, sem, NS, n_pl, args.per_deck - n_pl,
                                audit_ids=frozenset(ids), stop_on_defect=False,
                                log=lambda s: print(" ", s, flush=True), b2_split=True)
        opcounts.extend(cellrun.opcount_rows(cell))
        for qrec in cell["queries"]:
            for be in ("B0", "B1"):
                r = dict(qrec["backends"][be])
                audit_results.append(audit.check_receipt(r))
            R = qrec["R"]
            idx = len([s for s in sage_queries if s["query_id"].startswith(f"L8-s1-{name}-")])
            methods = ["split"] + (["fglm"] if deck.size <= 4 or idx < args.fglm_per_deck else [])
            sage_queries.append({"query_id": qrec["query_id"], "V": deck.V, "methods": methods,
                                 "xR": None if R is None else R[0],
                                 "b2_degree": qrec["backends"]["B2"]["elim_degree"],
                                 "b2_roots_sha256": qrec["backends"]["B2"]["roots_sha256"]})
        for qrec in cell["queries"]:  # op logs were audited in memory above; keep files small
            for be in ("B0", "B1"):
                qrec["backends"][be].pop("op_log", None)
        safe_write(OUT / "cells" / f"L8-s1-{name}.json", json.dumps(cell, default=str))
        q = cell["queries"]
        res["cells"][name] = {
            "V_size": deck.size, "forward_table_size": cell["forward_table"]["size_finite"],
            "forward_table_s3_roots_ok": s3_ok,
            "oracle_enumerated": cell["oracle"]["enumerated_multisets"],
            "oracle_expected": cell["oracle"]["expected"],
            "n_queries": len(q),
            "oracle_members": sum(1 for x in q if x["oracle_member"]),
            "planted_all_members": all(x["oracle_member"] for x in q if x["kind"] == "planted"),
            "decision_agreement_B0_B1_oracle": sum(1 for x in q if x["agreement"]["decision"]),
            "hit_triple_sets_equal": sum(1 for x in q if x["agreement"]["hit_triple_sets_equal"]),
            "witnesses_checked": sum(len(x["backends"][b]["witness_checks"]) for x in q for b in ("B0", "B1")),
            "all_witnesses_verified": all(x["backends"][b]["all_witnesses_verified"] for x in q for b in ("B0", "B1")),
            "b2_split_nosage_checked": len(q), "b2_split_nosage_mismatches": cell["b2_split_mismatches"],
            "defects": cell["defects"], "seconds": round(cell["seconds"], 2)}
        print(name, res["cells"][name], flush=True)
    ob = cellrun.canonical_opcounts_bytes(opcounts)
    safe_write(OUT / "opcounts.json", ob.decode())
    res["opcounts"] = {"file": "opcounts.json", "rows": len(opcounts),
                       "sha256": hashlib.sha256(ob).hexdigest()}
    print("opcounts sha256:", res["opcounts"]["sha256"], flush=True)
    res["accounting_audit"] = {"receipts_checked": len(audit_results),
                               "accepted": sum(1 for a in audit_results if a["accepted"]),
                               "rejected_examples": [a for a in audit_results if not a["accepted"]][:5]}

    # 4. B2 vs Sage elimination
    if not args.skip_sage:
        inp = {"p": fx["p"], "a": fx["a"], "b": fx["b"], "semaev_file": str(semaev.POLY_FILE),
               "queries": sage_queries}
        safe_write(OUT / "b2_sage_input.json", json.dumps(inp))
        ts = time.time()
        pr = subprocess.run([fixtures.SAGE, "-python", str(HERE / "sage_b2_crosscheck.py"),
                             str(OUT / "b2_sage_input.json"), str(OUT / "b2_sage_output.json")],
                            capture_output=True, text=True)
        safe_write(OUT / "b2_sage.stdout", pr.stdout)
        safe_write(OUT / "b2_sage.stderr", pr.stderr)
        cmp = []
        if pr.returncode == 0:
            sres = {r["query_id"]: r for r in json.load(open(OUT / "b2_sage_output.json"))["results"]}
            for sq in sage_queries:
                s = sres[sq["query_id"]]
                for m in sq["methods"]:
                    sm = s.get(m, {})
                    if "roots" not in sm:
                        cmp.append({"query_id": sq["query_id"], "method": m, "b2": sq["b2_degree"],
                                    "error": sm.get("error"), "degree_match": False, "root_set_match": False})
                        continue
                    rh = hashlib.sha256(",".join(map(str, sm["roots"])).encode()).hexdigest()
                    cmp.append({"query_id": sq["query_id"], "method": m, "b2": sq["b2_degree"],
                                "sage_radical_degree": sm["radical_degree"],
                                "sage_eliminant_degree": sm.get("eliminant_degree"),
                                "sage_rational_roots": sm["rational_roots"], "seconds": sm["seconds"],
                                "degree_match": sq["b2_degree"] == sm["radical_degree"],
                                "root_set_match": rh == sq["b2_roots_sha256"]})
        by_m = {}
        for c in cmp:
            e = by_m.setdefault(c["method"], {"n": 0, "degree_matches": 0, "root_set_matches": 0})
            e["n"] += 1
            e["degree_matches"] += int(c["degree_match"])
            e["root_set_matches"] += int(c["root_set_match"])
        res["b2_sage_crosscheck"] = {"returncode": pr.returncode, "seconds": round(time.time() - ts, 1),
                                     "by_method": by_m, "details": cmp}
        print("B2 vs sage:", by_m, flush=True)

    # 5. rho correctness (no ratio reported)
    rr = []
    for t in range(args.rho_targets):
        k = labels.h(labels.cell_lab(NS, "rho", 8, 1, t)) % fx["N"]
        Q = vc.mul(k, tuple(fx["G"]))
        out = rho.solve(fx, Q, t, NS)
        rr.append({"t": t, "solved": out["solved"], "k_matches": out.get("k") == k,
                   "fruitless_cycles": out["fruitless_cycles"], "restarts": out["restarts"]})
    res["rho_correctness"] = {"targets": len(rr), "solved_and_verified": sum(r["solved"] and r["k_matches"] for r in rr),
                              "details": rr}
    print("rho:", res["rho_correctness"]["solved_and_verified"], "/", len(rr), flush=True)
    res["seconds"] = round(time.time() - t0, 1)
    safe_write(OUT / "smoke_results.json", json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
