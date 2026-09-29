#!/usr/bin/env python3
"""C-PROV for EXP-CERTBIN-3f06d1 (NEW script; phase 0, before any frozen
stream of this contract is drawn and before trial-plan-v1.json is written).

Runs the REPLICATION code (this impl/, generalised V-basis path with the
polynomial basis given explicitly) on the Stage-1 cell: the Stage-1 curve and
V, the 5 archived F-S3 references and the 20 lowest-idx archived F-S3 targets
(x_R read from targets-F-S3.jsonl.gz), and compares with the archived values:
rank, "1 in R_D", the four trace hashes and the replay first-zero indices
against each of the 5 references, at D = 3 and 4. The archived input files are
first checked against the TASK-20260923-c2e57b snapshot receipt.

  python3 experiments/EXP-CERTBIN-3f06d1/impl/cprov.py \
      --stage1-run experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05 \
      --out experiments/EXP-CERTBIN-3f06d1/runs/RUN-CERTBIN-6d92b5/cprov.json

Exit 0 iff C-PROV passes. Draws no random value.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import numpy as np  # noqa: E402

from gf2n import TableField  # noqa: E402
from curve import Curve  # noqa: E402
from macaulay import MacaulayShape, descended_E, affine_basis  # noqa: E402
from oracles import oracle_A, oracle_B  # noqa: E402
from engine import make_ref, scalar_first_zero  # noqa: E402
from elim import eliminate, eval_forms  # noqa: E402
from vspace import VBasis  # noqa: E402

RECEIPT = "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json"
MEM_LIMIT = 4 * 1024 ** 3


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage1-run", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    if os.path.exists(args.out):
        print(f"refusing to overwrite {args.out}", file=sys.stderr)
        return 2
    t0 = time.time()
    started = now()
    s1 = os.path.abspath(args.stage1_run)
    rel = os.path.relpath(s1, REPO)
    receipt = json.load(open(os.path.join(REPO, RECEIPT)))
    inputs = {}
    in_ok = True
    for f in ("curve.json", "references.json", "targets-F-S3.jsonl.gz"):
        key = f"{rel}/{f}"
        got = sha256_file(os.path.join(s1, f))
        want = receipt["path_sha256"].get(key)
        inputs[key] = {"sha256": got, "receipt_sha256": want, "match": got == want}
        in_ok &= got == want

    F = TableField()
    cj = json.load(open(os.path.join(s1, "curve.json")))
    E = Curve(F, cj["A"], cj["B"])
    B = E.B
    V = VBasis([1 << j for j in range(9)], "Stage-1 polynomial V (explicit basis, generalised code path)")
    refs_j = json.load(open(os.path.join(s1, "references.json")))["F-S3"]["references"]
    labels = ["U1", "U2", "U3", "S1", "S2"]
    tg = {}
    with gzip.open(os.path.join(s1, "targets-F-S3.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["idx"] <= 20:
                tg[(r["idx"], r["D"])] = r
    idxs = sorted({i for i, _ in tg})
    assert idxs == list(range(1, 21)), idxs
    E0, Ej = affine_basis(F, B, V.basis)
    planes = [E0] + Ej
    mism = []
    n_cmp = 0
    per_D = {}
    extra = {"oracle_s_matches": 0, "oracle_s_checked": 0, "scalar_forms_path_mismatches": 0}
    for D in (3, 4):
        S = MacaulayShape(D)
        planesM = np.stack([S.build(x) for x in planes])
        live = {}
        for lab in labels:
            rj = refs_j[lab]
            xR = rj["x_R"]
            Em = descended_E(F, B, xR, V.basis)
            sols = oracle_B(Em)
            inst = {"x_R": xR, "sols": sols, "s": len(sols), "selected_as": lab}
            r = make_ref(S, S.build(Em), inst, lab, "F-S3", planesM)
            live[lab] = r
            arch = rj[f"D{D}"]
            got = {"rank": r.res.rank, "one_in_R": r.checks["one_in_R"], "h_rank": r.res.h_rank,
                   "h_set": r.res.h_set, "h_strict": r.res.h_strict, "h_ops": r.res.h_ops}
            for k, v in got.items():
                n_cmp += 1
                if arch[k] != v:
                    mism.append({"D": D, "ref": lab, "field": k, "archived": arch[k], "replication": v})
            extra["oracle_s_checked"] += 1
            extra["oracle_s_matches"] += int(len(sols) == rj["s"] and len(oracle_A(F, B, xR, V)) == rj["s"])
        nt = 0
        for idx in idxs:
            arch = tg[(idx, D)]
            xR = arch["x_R"]
            Em = descended_E(F, B, xR, V.basis)
            res, cpass, _ = eliminate(S.build(Em), S.C, keep_ops=True)
            one = S.const_col in set(res.c)
            got = {"rank": res.rank, "one_in_R": one, "h_rank": res.h_rank, "h_set": res.h_set,
                   "h_strict": res.h_strict, "h_ops": res.h_ops}
            for k, v in got.items():
                n_cmp += 1
                if arch[k] != v:
                    mism.append({"D": D, "idx": idx, "field": k, "archived": arch[k], "replication": v})
            for lab in labels:
                r = live[lab]
                e = eval_forms(r.forms[0], r.forms[1], [xR])[0]
                z = np.flatnonzero(e == 0)
                fz = int(z[0]) if z.size else len(r.p)
                if scalar_first_zero(r.forms[0], r.forms[1], xR) != fz:
                    extra["scalar_forms_path_mismatches"] += 1
                n_cmp += 1
                a = arch["refs"][lab]["replay_first_zero"]
                if a != fz:
                    mism.append({"D": D, "idx": idx, "ref": lab, "field": "replay_first_zero", "archived": a, "replication": fz})
            extra["oracle_s_checked"] += 1
            extra["oracle_s_matches"] += int(len(oracle_B(Em)) == arch["s"])
            nt += 1
        per_D[f"D{D}"] = {"references": len(labels), "targets": nt}
    impl_hashes = {f: sha256_file(os.path.join(HERE, f)) for f in sorted(os.listdir(HERE))
                   if os.path.isfile(os.path.join(HERE, f))}
    passed = in_ok and not mism
    out = {
        "control": "C-PROV", "experiment_id": "EXP-CERTBIN-3f06d1",
        "pass": passed,
        "inputs_match_receipt": in_ok, "receipt": RECEIPT, "inputs": inputs,
        "stage1_cell": {"curve": {k: cj[k] for k in ("A", "B", "order", "h", "q")}, "V": "polynomial {deg < 9}",
                        "references": labels, "targets_idx": idxs},
        "compared_fields": ["rank", "one_in_R", "h_rank", "h_set", "h_strict", "h_ops",
                            "replay_first_zero (target vs each of U1, U2, U3, S1, S2)"],
        "comparisons": n_cmp, "mismatches": mism, "n_mismatches": len(mism), "per_D": per_D,
        "extra_not_part_of_pass": extra,
        "impl_sha256_at_cprov": impl_hashes,
        "process": {"pid": os.getpid(), "argv": sys.argv, "python": sys.version, "numpy": np.__version__},
        "started_at": started, "finished_at": now(), "wall_seconds": time.time() - t0,
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        "draws_any_random_value": False,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1)
    os.replace(tmp, args.out)
    print(json.dumps({"C-PROV_pass": passed, "comparisons": n_cmp, "mismatches": len(mism)}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
