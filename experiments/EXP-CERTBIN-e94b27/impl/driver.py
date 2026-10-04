#!/usr/bin/env python3
"""Driver for EXP-CERTBIN-e94b27 (RC-1). Phase 0 is selftest.py.

  main invocation      : phases 1-4 (checkpoint per closure per set), then
                         assembles closures.jsonl.gz and certificates.jsonl.gz;
                         runs phase 7 only if phases 5 and 6 are complete.
  --phase determinism  : phase 5 (C-DET) in a SEPARATE process.
  (verifier)           : phase 6 is verifier/verify_cert.py, a separate process.
  --resume             : continue from the last complete checkpoint; after
                         phase 6: C-VERIFIER negative controls (the verifier is
                         invoked again as a separate process on 20 corrupted
                         certificates) and phase 7 (aggregation, decision
                         rules, run report).
"""
import argparse
import gzip
import json
import os
import resource
import subprocess
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import yaml  # noqa: E402

from common import (REPO, SPEC, MEM_LIMIT, W5_WATCHDOG, c_src, dump_json, dump_json_gz, load_json_gz,  # noqa: E402
                    now, sha256_file)
from gf2n import TableField  # noqa: E402
from macaulay import MacaulayShape  # noqa: E402
from elim import column_pass  # noqa: E402
from closure import Closure, WatchdogExpired, eval_cert, cert_to_json  # noqa: E402
from instances import load_source, select_sets, build_instances, eqs_of, SET_ORDER, ContractDefect  # noqa: E402
from oracles_rc1 import oracle_A, oracle_B  # noqa: E402

CLOSURE_MODULE = os.path.join(HERE, "closure.py")
W4_SETS = ["U62", "S62", "C20", "N-AFF62", "N-F262"]
M5_SETS = ["U62", "S62", "N-AFF62", "N-F262"]
W5_SETS = ["U62", "S62", "N-AFF62", "N-F262"]


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def git_state():
    try:
        head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--untracked-files=all"],
                            capture_output=True, text=True).stdout.splitlines()
        return {"commit": head, "dirty": bool(st), "status_porcelain": st}
    except Exception as e:  # noqa: BLE001
        return {"commit": None, "error": repr(e)}


class Run:
    def __init__(self, a):
        self.a = a
        self.out = os.path.abspath(a.out)
        self.ck = os.path.join(self.out, "checkpoint")
        os.makedirs(self.ck, exist_ok=True)
        self.F = TableField()

    def log(self, msg):
        print(f"[{now()}] {msg}", flush=True)

    def ckp(self, name):
        return os.path.join(self.ck, name)

    def done(self, name):
        return os.path.exists(self.ckp(name))

    # ------------------------------------------------------------------
    def load_instances(self):
        curve, p1, tg = load_source(os.path.join(REPO, self.a.source_run))
        sets = select_sets(tg)
        if self.a.dev_limit:
            sets = {k: v[:self.a.dev_limit] for k, v in sets.items()}
        nulls = build_instances(self.F, curve, p1, sets)
        return curve, sets, nulls

    # ------------------------------------------------------------------
    def phase1(self, curve, sets, nulls):
        name = "p1-sets-oracles-base.json.gz"
        if self.done(name):
            self.log("phase 1: checkpoint present, skipped")
            return load_json_gz(self.ckp(name))
        t0 = time.time()
        B = curve["B"]
        sh4, sh3 = MacaulayShape(4), MacaulayShape(3)
        recs = {}
        for sname in SET_ORDER:
            for inst in sets[sname]:
                E = inst["E"]
                eqs = eqs_of(E)
                a = inst["archived"]
                solsB = oracle_B(eqs)
                r = {"key": inst["key"], "set": sname, "family": inst["family"], "idx": inst["idx"],
                     "x_R": a["x_R"], "s_B": len(solsB), "stratum_B": "sat" if solsB else "unsat"}
                if inst["family"] == "F-S3":
                    solsA = oracle_A(self.F, B, a["x_R"])
                    r["s_A"] = len(solsA)
                    r["oracle_A_equals_B"] = solsA == solsB
                    # the linear consequence ell of EV-CERTBIN-6c3e0a O-11
                    xr2inv = self.F.inv(self.F.mul(a["x_R"], a["x_R"]))
                    trc = self.F.trace(self.F.mul(B, xr2inv))
                    comb = {}
                    for k in range(17):
                        if self.F.trace(self.F.mul(1 << k, xr2inv)):
                            for m in eqs[k]:
                                comb[m] = comb.get(m, 0) ^ 1
                    comb = sorted(m for m, p in comb.items() if p)
                    ell = sorted([1 << 0, 1 << 9] + ([0] if trc else []))
                    r["ell"] = ell
                    r["ell_identity_holds"] = comb == ell
                ok = (r["s_B"] == a["s"] and r["stratum_B"] == a["stratum"])
                if inst["family"] == "F-S3":
                    ok = ok and r["oracle_A_equals_B"] and r["s_A"] == a["s"]
                r["oracle_agree_archive"] = bool(ok)
                base = {}
                for D, sh in ((4, sh4), (3, sh3)):
                    M = sh.build(E)
                    ps, cs, _ = column_pass(M, sh.C, keep_ops=False)
                    base[D] = {"rank": len(ps), "one": bool(sh.C - 1 in cs)}
                r["M_4"] = base[4]
                r["M_3"] = base[3]
                r["base_agree_archive"] = (base[4]["rank"] == a["rank_4"] and base[4]["one"] == a["one_in_R_4"]
                                           and base[3]["rank"] == a["rank_3"] and base[3]["one"] == a["one_in_R_3"])
                recs[inst["key"]] = r
            self.log(f"phase 1: {sname} done ({time.time() - t0:.1f}s)")
        res = {"records": recs, "c_nulls_structure": nulls, "wall_seconds": time.time() - t0,
               "peak_rss_bytes": rss(), "finished_at": now()}
        dump_json_gz(self.ckp(name), res)
        return res

    # ------------------------------------------------------------------
    def closure_set(self, cname, sname, insts, fn):
        name = f"p-{cname}-{sname}.json.gz"
        if self.done(name):
            self.log(f"{cname} {sname}: checkpoint present, skipped")
            return load_json_gz(self.ckp(name))
        t0 = time.time()
        recs, certs = {}, []
        for inst in insts:
            ti = time.time()
            rec, cert = fn(inst)
            rec["wall_seconds"] = time.time() - ti
            recs[inst["key"]] = rec
            if cert is not None:
                cj = cert_to_json(cert)
                certs.append({"key": inst["key"], "set": sname, "family": inst["family"], "idx": inst["idx"],
                              "closure": cname, "form": "flat", "C": cj, "size": len(cj),
                              "max_deg_mu": max(len(p[0]) for p in cj)})
                rec["certificate"] = "emitted"
            elif rec.get("one"):
                rec["certificate"] = "UNCERTIFIED"
        res = {"closure": cname, "set": sname, "records": recs, "certificates": certs,
               "closure_module_sha256": sha256_file(CLOSURE_MODULE),
               "wall_seconds": time.time() - t0, "peak_rss_bytes": rss(), "finished_at": now()}
        dump_json_gz(self.ckp(name), res)
        self.log(f"{cname} {sname}: {len(insts)} instances, {sum(1 for r in recs.values() if r.get('one'))} "
                 f"refuted, {len(certs)} certificates ({time.time() - t0:.1f}s)")
        return res

    def fn_w(self, D, deadline=None):
        cl = Closure(18, D, 17)

        def fn(inst):
            eqs = eqs_of(inst["E"])
            try:
                rec, cert = cl.w_closure(eqs, want_cert=True, deadline_s=deadline)
            except WatchdogExpired:
                return {"label": "UNDETERMINED(budget)", "one": None, "watchdog_seconds": deadline}, None
            rec["label"] = "refuted" if rec["one"] else "not_refuted"
            if inst["family"] == "F-S3" and D == 4:
                ell = inst["ell"]
                rec["ell_in_W4_le1"] = bool(cl.member(ell))
            if cert is not None:
                rec["engine_self_check_sum_is_1"] = eval_cert(cert, eqs) == [0]
            return rec, cert
        return fn

    def fn_m(self, D):
        cl = Closure(18, D, 17)

        def fn(inst):
            eqs = eqs_of(inst["E"])
            rec, cert = cl.macaulay_closure(eqs, want_cert=True)
            rec["label"] = "refuted" if rec["one"] else "not_refuted"
            if cert is not None:
                rec["engine_self_check_sum_is_1"] = eval_cert(cert, eqs) == [0]
            return rec, cert
        return fn

    # ------------------------------------------------------------------
    def main_phases(self):
        a = self.a
        src = c_src()
        dump_json(self.ckp("c-src-driver.json"), src)
        if not src["pass"]:
            self.log("C-SRC FAILED: STOP (SR-2, INV-2)")
            return 2
        st = os.path.join(self.out, "selftest.json")
        if not os.path.exists(st) or not json.load(open(st)).get("pass"):
            self.log("selftest.json missing or failing: STOP (SR-2, INV-1)")
            return 2
        plan = os.path.join(REPO, a.plan)
        if not os.path.exists(plan):
            self.log("trial plan missing: STOP")
            return 2
        pl = json.load(open(plan))
        if pl["specification"]["sha256"] != sha256_file(os.path.join(REPO, SPEC)):
            self.log("specification differs from the trial plan's: STOP")
            return 2
        tp = time.time()
        try:
            curve, sets, nulls = self.load_instances()
        except ContractDefect as e:
            self.log(f"CONTRACT DEFECT: {e}: STOP")
            dump_json(self.ckp("contract-defect.json"), {"defect": str(e), "at": now()})
            return 3
        p1 = self.phase1(curve, sets, nulls)
        for sname in SET_ORDER:
            for inst in sets[sname]:
                if inst["family"] == "F-S3":
                    inst["ell"] = p1["records"][inst["key"]]["ell"]
        # instance-sets.json (written once)
        isp = os.path.join(self.out, "instance-sets.json")
        if not os.path.exists(isp):
            dump_json(isp, {"experiment_id": "EXP-CERTBIN-e94b27", "run_id": a.run_id,
                            "rules": "spec instance_sets (frozen v1); zero sampling",
                            "sizes": {k: len(v) for k, v in sets.items()},
                            "sets": {k: [{"key": i["key"], "family": i["family"], "idx": i["idx"],
                                          "archived": i["archived"], "E_hex": i["E_hex"],
                                          "E_sha256": i["E_sha256"]} for i in v] for k, v in sets.items()}})
        timings = {"phase1": p1["wall_seconds"]}
        # phase 2: W_4
        t = time.time()
        w4 = {s: self.closure_set("W_4", s, sets[s], self.fn_w(4)) for s in W4_SETS}
        timings["phase2_W_4"] = time.time() - t
        # phase 3: M_5
        t = time.time()
        m5 = {s: self.closure_set("M_5", s, sets[s], self.fn_m(5)) for s in M5_SETS}
        timings["phase3_M_5"] = time.time() - t
        # phase 4: W_5 on the residual
        sel = {}
        for s in W5_SETS:
            if s == "S62":
                sel[s] = sets[s][:10]
            else:
                res = [i for i in sets[s] if not w4[s]["records"][i["key"]].get("one")
                       and not m5[s]["records"][i["key"]].get("one")]
                sel[s] = res if s == "U62" else res[:10]
        t = time.time()
        w5 = {s: self.closure_set("W_5", s, sel[s], self.fn_w(5, deadline=W5_WATCHDOG)) for s in W5_SETS}
        timings["phase4_W_5"] = time.time() - t
        dump_json(self.ckp("w5-selection.json"), {s: [i["key"] for i in v] for s, v in sel.items()})
        # assemble closures.jsonl.gz and certificates.jsonl.gz (once)
        cp = os.path.join(self.out, "closures.jsonl.gz")
        cep = os.path.join(self.out, "certificates.jsonl.gz")
        if not os.path.exists(cp):
            with gzip.open(cp + ".tmp", "wt") as f:
                for s in SET_ORDER:
                    for inst in sets[s]:
                        k = inst["key"]
                        r1 = p1["records"][k]
                        for D in (3, 4):
                            b = r1[f"M_{D}"]
                            f.write(json.dumps({"key": k, "set": s, "idx": inst["idx"], "closure": f"M_{D}",
                                                "rank": b["rank"], "one": b["one"],
                                                "label": "refuted" if b["one"] else "not_refuted",
                                                "role": "C-BASE baseline"}) + "\n")
                        for cname, dct in (("W_4", w4), ("M_5", m5), ("W_5", w5)):
                            if s in dct and k in dct[s]["records"]:
                                rec = dict(dct[s]["records"][k])
                                rec.update({"key": k, "set": s, "idx": inst["idx"], "closure": cname})
                                f.write(json.dumps(rec) + "\n")
            os.replace(cp + ".tmp", cp)
        if not os.path.exists(cep):
            with gzip.open(cep + ".tmp", "wt") as f:
                for cname, dct, sl in (("W_4", w4, W4_SETS), ("M_5", m5, M5_SETS), ("W_5", w5, W5_SETS)):
                    for s in sl:
                        for c in dct[s]["certificates"]:
                            f.write(json.dumps(c, separators=(",", ":")) + "\n")
            os.replace(cep + ".tmp", cep)
        tim_p = self.ckp("timings-phases-1-4.json")
        if not os.path.exists(tim_p):
            dump_json(tim_p, {"timings_seconds": timings, "this_invocation_wall": time.time() - tp,
                              "peak_rss_bytes": rss(), "at": now()})
        self.log("phases 1-4 complete")
        det_ok = self.done("p5-determinism.json.gz")
        ver = os.path.join(self.out, "certificate-verification.json")
        if not det_ok or not os.path.exists(ver):
            self.log("pending: phase 5 (--phase determinism) and/or phase 6 (verify_command); then --resume")
            return 0
        return self.after_verification(sets)

    # ------------------------------------------------------------------
    def determinism(self):
        """Phase 5 (C-DET): separate process; recompute M_5 and W_4 on the 10
        lowest-idx U62 and the 5 lowest-idx S62 instances."""
        name = "p5-determinism.json.gz"
        if self.done(name):
            self.log("phase 5: checkpoint present, skipped")
            return 0
        need = ["p-W_4-U62.json.gz", "p-W_4-S62.json.gz", "p-M_5-U62.json.gz", "p-M_5-S62.json.gz"]
        if not all(self.done(n) for n in need):
            self.log("phase 5 needs phases 2-3 checkpoints: STOP")
            return 2
        t0 = time.time()
        curve, sets, _ = self.load_instances()
        insts = sets["U62"][:10] + sets["S62"][:5]
        cl4, cl5 = Closure(18, 4, 17), Closure(18, 5, 17)
        rows, mism = [], []
        for inst in insts:
            s = inst["set"]
            eqs = eqs_of(inst["E"])
            w, _ = cl4.w_closure(eqs, want_cert=False)
            m, _ = cl5.macaulay_closure(eqs, want_cert=False)
            rows.append({"key": inst["key"], "W_4": {"final_dim": w["final_dim"],
                                                     "iterations_to_fixpoint": w["iterations_to_fixpoint"],
                                                     "one": w["one"]},
                         "M_5": {"rank": m["rank"], "one": m["one"]}})
        ref = {}
        for s in ("U62", "S62"):
            ref[("W_4", s)] = load_json_gz(self.ckp(f"p-W_4-{s}.json.gz"))["records"]
            ref[("M_5", s)] = load_json_gz(self.ckp(f"p-M_5-{s}.json.gz"))["records"]
        for r, inst in zip(rows, insts):
            s = inst["set"]
            ow = ref[("W_4", s)][inst["key"]]
            om = ref[("M_5", s)][inst["key"]]
            same = (ow["final_dim"] == r["W_4"]["final_dim"]
                    and ow["iterations_to_fixpoint"] == r["W_4"]["iterations_to_fixpoint"]
                    and ow["one"] == r["W_4"]["one"] and om["rank"] == r["M_5"]["rank"] and om["one"] == r["M_5"]["one"])
            r["identical_to_main_process"] = bool(same)
            if not same:
                mism.append(inst["key"])
        res = {"control": "C-DET", "pid": os.getpid(), "separate_process": True, "instances": rows,
               "mismatches": mism, "pass": not mism, "wall_seconds": time.time() - t0,
               "peak_rss_bytes": rss(), "finished_at": now()}
        dump_json_gz(self.ckp(name), res)
        dump_json(os.path.join(self.out, "determinism.json"), res)
        self.log(f"phase 5: C-DET pass={not mism} ({time.time() - t0:.1f}s)")
        return 0

    # ------------------------------------------------------------------
    def negative_controls(self):
        """C-VERIFIER part 2: 20 corrupted certificates built from verified ones,
        checked by the verifier in a separate process."""
        outp = os.path.join(self.out, "negative-controls-verification.json")
        meta = self.ckp("negative-controls-meta.json")
        if os.path.exists(outp) and os.path.exists(meta):
            res = json.load(open(outp))
            res.update(json.load(open(meta)))
            return res
        ver = json.load(open(os.path.join(self.out, "certificate-verification.json")))
        okkeys = [(r["key"], r["closure"]) for r in ver["certificates"] if r["verified"]]
        certs = {}
        with gzip.open(os.path.join(self.out, "certificates.jsonl.gz"), "rt") as f:
            for line in f:
                c = json.loads(line)
                certs[(c["key"], c["closure"])] = c
        corrupted = []
        if okkeys:
            for i in range(20):
                base = certs[okkeys[i % len(okkeys)]]
                C = [list(p) for p in base["C"]]
                pos = (i * 7919) % len(C)
                if i % 2 == 0:
                    kind = "one pair removed"
                    removed = C.pop(pos)
                    detail = {"removed": removed}
                else:
                    kind = "one k changed"
                    old = C[pos][1]
                    C[pos] = [C[pos][0], (old + 1) % 17]
                    detail = {"position": pos, "k_from": old, "k_to": (old + 1) % 17}
                corrupted.append({"key": base["key"], "set": base["set"], "family": base["family"],
                                  "idx": base["idx"], "closure": base["closure"] + f"#corrupt{i:02d}",
                                  "form": "flat", "C": C, "corruption": kind, "detail": detail})
        cp = os.path.join(self.out, "negative-controls-certificates.jsonl.gz")
        with gzip.open(cp, "wt") as f:
            for c in corrupted:
                f.write(json.dumps(c, separators=(",", ":")) + "\n")
        cmd = [sys.executable, os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/verifier/verify_cert.py"),
               "--certs", os.path.relpath(cp, REPO), "--source-run", self.a.source_run,
               "--out", os.path.relpath(outp, REPO)]
        self.log("C-VERIFIER negative controls: " + " ".join(cmd))
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        res = json.load(open(outp))
        m = {"_built": len(corrupted), "_command": cmd, "_returncode": r.returncode,
             "_corruptions": [{"key": c["key"], "closure": c["closure"], "corruption": c["corruption"],
                               "detail": c["detail"]} for c in corrupted]}
        dump_json(meta, m)
        res.update(m)
        return res

    def after_verification(self, sets):
        neg = self.negative_controls()
        from analysis import aggregate
        return aggregate(self, sets, neg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--source-run", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--phase", choices=["determinism"], default=None)
    ap.add_argument("--dev-limit", type=int, default=0,
                    help="DEVELOPMENT ONLY: first N instances per set; refused for an output inside the repository")
    a = ap.parse_args()
    if a.dev_limit and os.path.abspath(a.out).startswith(REPO + os.sep):
        print("--dev-limit is refused for an output directory inside the repository", file=sys.stderr)
        return 4
    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    spec = yaml.safe_load(open(os.path.join(REPO, a.spec)))["experiment"]
    if not (spec["status"] == "approved" and spec.get("approved_by") and spec["id"] == "EXP-CERTBIN-e94b27"
            and spec["run_id"] == a.run_id):
        print("specification_error: not an approved contract for this run id", file=sys.stderr)
        return 4
    run = Run(a)
    with open(run.ckp("invocations.jsonl"), "a") as f:
        f.write(json.dumps({"argv": sys.argv, "at": now(), "pid": os.getpid(), "git": git_state()}) + "\n")
    if a.phase == "determinism":
        return run.determinism()
    return run.main_phases()


if __name__ == "__main__":
    sys.exit(main())
