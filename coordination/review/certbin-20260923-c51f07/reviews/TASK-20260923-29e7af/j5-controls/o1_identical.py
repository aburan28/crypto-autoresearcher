#!/usr/bin/env python3
"""J5 / proves-too-much object O1 (TASK-20260923-29e7af, red team).
IDENTICAL INSTANCES, where "the trace is unstable" is KNOWN FALSE.

Runs the ARCHIVED pipeline function engine.process_family UNCHANGED (imported
from experiments/EXP-CERTBIN-4e92d7/impl/, not edited, not copied) on:
  O1(a) each of the five F-S3 references scored against an identical copy of
        itself (targets = the 5 reference instances, idx 1..5);
  O1(b) the archived pair F-S3 target 1 and F-RANDX target 786 (same x_R =
        88878), in both directions.
at D = 4 and D = 3. Instance inputs come from the archived phase-1 checkpoint.
Verification computation under DEC-20260923-4d7a19; NOT a trial, no RUN id,
not evidence about H-CERTBIN-a73f1c. Writes only o1-results.json here.

Declared failure signature (review plan proves_too_much): the pipeline must
report a match at all four granularities and survival of the whole replay
with every e_k = 1. Anything else means the instability readings are
manufactured by the instrument.
"""
import copy
import gzip
import json
import os
import sys
import time

REPO = "/home/user/crypto-autoresearcher"
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/impl")
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IMPL)

import numpy as np  # noqa: E402
from gf2n import TableField  # noqa: E402
from macaulay import MacaulayShape, affine_basis, descended_E  # noqa: E402
from engine import process_family  # noqa: E402


def log(msg):
    print(msg, flush=True)


def main():
    t0 = time.time()
    P1 = json.load(gzip.open(os.path.join(RUN, "checkpoint/p1-instances.json.gz"), "rt"))
    F = TableField()
    B = P1["curve"]["B"]
    E0, Ej = affine_basis(F, B)
    planes = [E0] + Ej
    ctx = {"F": F, "shapes": {4: MacaulayShape(4), 3: MacaulayShape(3)}}
    build = lambda inst: descended_E(F, B, inst["x_R"])  # noqa: E731  (same as driver.build_curve)
    refs_arch = json.load(open(os.path.join(RUN, "references.json")))["F-S3"]["references"]
    out = {"O1a": {}, "O1b": {}, "archived_cross_record_F-RANDX_786": {}}
    for D in (4, 3):
        # ---- O1(a)
        refs = [copy.deepcopy(r) for r in P1["F-S3"]["refs"]]
        tg = []
        for i, r in enumerate(refs):
            t = copy.deepcopy(r)
            t.pop("selected_as", None)
            t.update({"idx": i + 1, "degenerate": False, "self_of": r["selected_as"]})
            tg.append(t)
        res, live, _ = process_family(ctx, "O1a-F-S3-self", D, ref_insts=refs, targets=tg, build_E=build,
                                      reverse=False, planes_E=planes, cross_groups={}, log=log,
                                      affine_route=True)
        rows = []
        for rec, t in zip(res["records"], tg):
            lab = t["self_of"]
            m = rec["refs"][lab]
            K = next(len(r.p) for r in live["own"] if r.label == lab)
            rows.append({"ref": lab, "match": m["match"], "f_div": m["f_div"], "kdiv": m["kdiv"],
                         "replay_first_zero": m["replay_first_zero"], "K": K,
                         "full_replay_survival": m["replay_first_zero"] == K,
                         "all_four_match": all(m["match"].values())})
        rebuilt = {r["label"]: {k: r[k] == refs_arch[r["label"]][f"D{D}"][k]
                                for k in ("h_rank", "h_set", "h_strict", "h_ops")}
                   for r in res["refs"] if r["label"] in refs_arch}
        out["O1a"][f"D{D}"] = {"rows": rows, "rebuilt_refs_equal_archived_hashes": rebuilt,
                               "hash_anomalies": res["hash_anomalies"],
                               "signature_met": all(r["all_four_match"] and r["full_replay_survival"] for r in rows)}
        # ---- O1(b): F-S3 target 1 <-> F-RANDX target 786
        fs3_t1 = copy.deepcopy(next(t for t in P1["F-S3"]["targets"] if t["idx"] == 1))
        rx_786 = copy.deepcopy(next(t for t in P1["F-RANDX"]["targets"] if t["idx"] == 786))
        assert fs3_t1["x_R"] == rx_786["x_R"] == 88878
        pairs = {}
        for name, ref_i, tgt_i in (("ref=F-S3 t1, target=F-RANDX t786", fs3_t1, rx_786),
                                   ("ref=F-RANDX t786, target=F-S3 t1", rx_786, fs3_t1)):
            ri = copy.deepcopy(ref_i)
            ri["selected_as"] = "R"
            ti = copy.deepcopy(tgt_i)
            ti["idx"] = 1
            r2, live2, _ = process_family(ctx, "O1b-shared-xR", D, ref_insts=[ri], targets=[ti], build_E=build,
                                          reverse=False, planes_E=planes, cross_groups={}, log=log,
                                          affine_route=True)
            m = r2["records"][0]["refs"]["R"]
            K = len(live2["own"][0].p)
            pairs[name] = {"match": m["match"], "f_div": m["f_div"], "replay_first_zero": m["replay_first_zero"],
                           "K": K, "all_four_match": all(m["match"].values()),
                           "full_replay_survival": m["replay_first_zero"] == K}
        out["O1b"][f"D{D}"] = {"pairs": pairs,
                               "signature_met": all(p["all_four_match"] and p["full_replay_survival"]
                                                    for p in pairs.values())}
        # archived secondary cross-record of F-RANDX target 786 against F-S3:modal
        with gzip.open(os.path.join(RUN, "targets-F-RANDX.jsonl.gz"), "rt") as f:
            for line in f:
                d = json.loads(line)
                if d["idx"] == 786 and d["D"] == D:
                    mm = d["refs"].get("F-S3:modal")
                    out["archived_cross_record_F-RANDX_786"][f"D{D}"] = {
                        "match": mm["match"] if mm else None,
                        "replay_first_zero": mm.get("replay_first_zero") if mm else None,
                        "F-S3_modal_len_strict": refs_arch["modal"][f"D{D}"]["len_strict"]}
    out["wall_seconds"] = round(time.time() - t0, 1)
    out["numpy"] = np.__version__
    json.dump(out, open(os.path.join(HERE, "o1-results.json"), "w"), indent=1)
    print(json.dumps({k: (v if k != "O1a" else {D: {"signature_met": x["signature_met"],
                                                    "rebuilt": x["rebuilt_refs_equal_archived_hashes"]}
                                                for D, x in v.items()}) for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
