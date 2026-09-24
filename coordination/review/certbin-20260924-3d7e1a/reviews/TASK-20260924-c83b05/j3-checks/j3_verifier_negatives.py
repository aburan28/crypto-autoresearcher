#!/usr/bin/env python3
"""J3: can C-VERIFIER fail on EVERY certificate kind the run counts?
TASK-20260924-c83b05.

The archived negative controls (negative-controls-verification.json) are 20
corruptions of W_4/U62 certificates only (deviation 6), and 5 of the 10
"one k changed" ones were rejected as "repeated pair" (a format rule), not by
the algebraic sum test. Here, for EVERY (closure, set) kind present in
certificates.jsonl.gz (W_4/U62, W_4/C20, M_5/U62, M_5/N-AFF62, M_5/N-F262),
5 base certificates (file positions 0, 12, 24, 36, 48 within the kind, or
fewer if the kind is smaller, modulo its size) are taken and four corruptions
built from each, each chosen so that it is ALGEBRAICALLY wrong and FORMALLY
valid (no repeated pair, indices in range), so that only the sum test can
reject it:
  (a) pair removed (a pair with mu * f_k != 0);
  (b) k changed to the smallest k' with (mu, k') absent and mu*f_k != mu*f_k';
  (c) mu changed (drop its highest variable, or add v_0 if mu = 1) with the
      new pair absent and the product changed;
  (d) transplant: the unmodified certificate relabelled onto the next
      instance of the same set.
The bases themselves are submitted as positive controls. Ground truth for
every submitted certificate is computed with the validator's own multilinear
arithmetic on the own-decoded systems. The ARCHIVED verifier
(verifier/verify_cert.py, unchanged) is run as a subprocess; its output goes
only to j3-checks/. No archived file is written.
"""
import gzip
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUNREL = "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
RUN = os.path.join(REPO, RUNREL)
sys.path.insert(0, os.path.join(HERE, "..", "j2-constructions"))
import own_algebra as oa  # noqa: E402


def prod(mu, f):
    acc = {}
    for m in f:
        x = mu | m
        acc[x] = acc.get(x, 0) ^ 1
    return frozenset(x for x, p in acc.items() if p)


def own_sum(C, eqs):
    acc = {}
    for mu_l, k in C:
        mu = 0
        for i in mu_l:
            mu |= 1 << i
        for m in eqs[k]:
            x = mu | m
            acc[x] = acc.get(x, 0) ^ 1
    return sorted(x for x, p in acc.items() if p)


def to_mask(l):
    m = 0
    for i in l:
        m |= 1 << i
    return m


def to_list(m):
    return [i for i in range(18) if (m >> i) & 1]


def main():
    inst = json.load(open(os.path.join(RUN, "instance-sets.json")))
    sets = inst["sets"]
    by_key = {x["key"]: x for v in sets.values() for x in v}
    set_of = {x["key"]: s for s, v in sets.items() for x in v}
    eqs = {k: oa.eqs_from_hex(x["E_hex"]) for k, x in by_key.items()}
    certs = [json.loads(line) for line in gzip.open(os.path.join(RUN, "certificates.jsonl.gz"), "rt")]
    kinds = {}
    for c in certs:
        kinds.setdefault(f'{c["closure"]}/{set_of[c["key"]]}', []).append(c)
    out, meta = [], []

    def emit(base, C, label, key=None, kind=None):
        k = key or base["key"]
        x = by_key[k]
        rec = {"key": k, "set": set_of[k], "family": x["family"], "idx": x["idx"],
               "closure": f'{base["closure"]}#{label}', "form": "flat", "C": C}
        out.append(rec)
        truth = own_sum(C, eqs[k]) == [0]
        meta.append({"kind": kind, "label": label, "key": k, "base_key": base["key"], "closure": rec["closure"],
                     "own_ground_truth_sum_is_1": truth})

    for kind, lst in sorted(kinds.items()):
        n = len(lst)
        picks = sorted(set((12 * t) % n for t in range(5)))
        for t, pi in enumerate(picks):
            base = lst[pi]
            C = [list(p) for p in base["C"]]
            E = eqs[base["key"]]
            present = {(to_mask(p[0]), p[1]) for p in C}
            emit(base, C, f"base{t}", kind=kind)
            # (a) pair removed
            for off in range(len(C)):
                pos = (t * 7919 + 13 + off) % len(C)
                mu, k = to_mask(C[pos][0]), C[pos][1]
                if prod(mu, E[k]):
                    Ca = C[:pos] + C[pos + 1:]
                    emit(base, Ca, f"a_removed{t}", kind=kind)
                    break
            # (b) k changed
            done = False
            for off in range(len(C)):
                pos = (t * 104729 + 7 + off) % len(C)
                mu, k = to_mask(C[pos][0]), C[pos][1]
                for k2 in range(17):
                    if k2 != k and (mu, k2) not in present and prod(mu, E[k]) != prod(mu, E[k2]):
                        Cb = [list(p) for p in C]
                        Cb[pos] = [C[pos][0], k2]
                        Cb.sort(key=lambda p: (p[0], p[1]))
                        emit(base, Cb, f"b_kchanged{t}", kind=kind)
                        done = True
                        break
                if done:
                    break
            # (c) mu changed
            done = False
            for off in range(len(C)):
                pos = (t * 15485863 + 3 + off) % len(C)
                mu, k = to_mask(C[pos][0]), C[pos][1]
                mu2 = mu & ~(1 << (mu.bit_length() - 1)) if mu else 1
                if (mu2, k) not in present and prod(mu, E[k]) != prod(mu2, E[k]):
                    Cc = [list(p) for p in C]
                    Cc[pos] = [to_list(mu2), k]
                    Cc.sort(key=lambda p: (p[0], p[1]))
                    emit(base, Cc, f"c_muchanged{t}", kind=kind)
                    done = True
                    break
            # (d) transplant onto the next instance of the same set
            same = [x["key"] for x in sets[set_of[base["key"]]]]
            other = same[(same.index(base["key"]) + 1) % len(same)]
            emit(base, C, f"d_transplant{t}", key=other, kind=kind)
    cp = os.path.join(HERE, "neg-extended-certificates.jsonl.gz")
    with gzip.open(cp, "wt") as f:
        for c in out:
            f.write(json.dumps(c, separators=(",", ":")) + "\n")
    vout = os.path.join(HERE, "neg-extended-verification.json")
    cmd = [sys.executable, os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/verifier/verify_cert.py"),
           "--certs", os.path.relpath(cp, REPO), "--source-run", "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05",
           "--out", os.path.relpath(vout, REPO), "--instances", RUNREL + "/instance-sets.json"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    ver = json.load(open(vout))
    vres = {(x["key"], x["closure"]): x for x in ver["certificates"]}
    table = {}
    wrong = []
    for m in meta:
        v = vres[(m["key"], m["closure"])]
        m["verifier_verified"] = v["verified"]
        m["verifier_reason"] = v["reason"]
        typ = m["label"].rstrip("0123456789")
        cell = table.setdefault(m["kind"], {}).setdefault(typ, {"n": 0, "verifier_accepts": 0, "ground_truth_valid": 0,
                                                                   "rejected_by_sum_test": 0, "rejected_other_reason": 0})
        cell["n"] += 1
        cell["verifier_accepts"] += bool(v["verified"])
        cell["ground_truth_valid"] += bool(m["own_ground_truth_sum_is_1"])
        if not v["verified"]:
            if v["reason"].startswith("sum is not 1"):
                cell["rejected_by_sum_test"] += 1
            else:
                cell["rejected_other_reason"] += 1
        if bool(v["verified"]) != bool(m["own_ground_truth_sum_is_1"]):
            wrong.append(m)
    res = {"task_id": "TASK-20260924-c83b05", "joint": "J3", "check": "C-VERIFIER extended negative controls",
           "command": cmd, "returncode": r.returncode, "stdout": r.stdout, "stderr": r.stderr[-2000:],
           "verifier_sha256": ver["verifier_sha256"], "submitted": ver["submitted"],
           "per_kind_and_type": table, "verifier_vs_ground_truth_disagreements": wrong,
           "all_bases_accepted": all(c["verifier_accepts"] == c["n"] for k in table.values() for t, c in k.items() if t == "base"),
           "all_corruptions_rejected_by_sum_test": all(c["rejected_by_sum_test"] == c["n"] for k in table.values() for t, c in k.items() if t != "base"),
           "construction_checked": ver["construction_checked"], "construction_disagreements": ver["construction_disagreements"],
           "details": meta}
    json.dump(res, open(os.path.join(HERE, "neg_extended_results.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("details", "stderr")}, indent=1))


if __name__ == "__main__":
    main()
