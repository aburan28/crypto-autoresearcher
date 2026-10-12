#!/usr/bin/env python3
"""TASK-20260926-59169c CP-1: verify archived inputs before comparing.

(1) every file of the two reviewer directories matches the TASK-20260926-9c0134
    receipt path_sha256 (and no unlisted file exists in the archived tree);
(2) each seal.txt matches its sealed files;
(3) blind-inputs.json (and the key file) match the TASK-20260926-58d32c receipt;
(4) the 9c0134 receipt reports no blocking defect.
Checked on the bytes of commit a524be32e (extracted with git archive into
--root) and, separately, on the working tree (--wt), which must be identical.
Own code; imports only the standard library.
"""
import argparse, hashlib, json, os, re, sys

REV = "coordination/review/certbin-20260926-089841"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_root(root):
    out = {"root": root}
    r9 = json.load(open(os.path.join(root, REV, "archives/TASK-20260926-9c0134/snapshot-receipt.json")))
    r58 = json.load(open(os.path.join(root, REV, "archives/TASK-20260926-58d32c/snapshot-receipt.json")))
    # (1)
    mism, ok = [], 0
    for rel, h in r9["path_sha256"].items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            mism.append({"path": rel, "problem": "missing"})
            continue
        hh = sha(p)
        if hh != h:
            mism.append({"path": rel, "problem": "sha256", "got": hh, "want": h})
        elif os.path.getsize(p) != r9["path_size_bytes"][rel]:
            mism.append({"path": rel, "problem": "size"})
        else:
            ok += 1
    unlisted = []
    for t in ("TASK-20260926-83cebf", "TASK-20260926-f0e5a4"):
        d = os.path.join(root, REV, "reviews", t)
        for dp, dn, fn in os.walk(d):
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), root)
                if rel not in r9["path_sha256"]:
                    unlisted.append(rel)
    out["check1_reviewer_dirs_vs_9c0134"] = {"files_matched": ok, "mismatches": mism, "unlisted_files": unlisted,
                                             "pass": not mism and not unlisted}
    # (2) seals
    seals = {}
    s83 = open(os.path.join(root, REV, "reviews/TASK-20260926-83cebf/seal.txt")).read()
    res = []
    for m in re.finditer(r"^sha256 ([0-9a-f]{64})\s+(\S+)\s+\((\d+) bytes", s83, re.M):
        p = os.path.join(root, REV, "reviews/TASK-20260926-83cebf", m.group(2))
        res.append({"file": m.group(2), "sealed": m.group(1), "actual": sha(p),
                    "size_ok": os.path.getsize(p) == int(m.group(3))})
    seals["83cebf"] = {"entries": res, "pass": len(res) == 4 and all(e["sealed"] == e["actual"] and e["size_ok"] for e in res)}
    sf0 = open(os.path.join(root, REV, "reviews/TASK-20260926-f0e5a4/seal.txt")).read()
    m = re.search(r"^sha256: ([0-9a-f]{64})", sf0, re.M)
    fnm = re.search(r"^file: (\S+)", sf0, re.M).group(1)
    act = sha(os.path.join(root, REV, "reviews/TASK-20260926-f0e5a4", fnm))
    seals["f0e5a4"] = {"file": fnm, "sealed": m.group(1), "actual": act, "pass": m.group(1) == act}
    out["check2_seals"] = seals
    # (3) blind inputs
    b = {}
    for rel in (REV + "/blind/blind-inputs.json", REV + "/blind-inputs-key.json"):
        want = r58["path_sha256"].get(rel)
        got = sha(os.path.join(root, rel))
        b[rel] = {"want_58d32c": want, "got": got, "pass": want == got}
    out["check3_blind_inputs_vs_58d32c"] = b
    # (4) blocking defects
    sc1 = r9["SC-1"]
    out["check4_9c0134_blocking"] = {
        "comparator_blocked": sc1.get("comparator_TASK-20260926-59169c_blocked"),
        "defects": sc1.get("defects"),
        "83cebf_import_hits": sc1["import_scan"].get("83cebf_hits"),
        "f0e5a4_import_hits": sc1["import_scan"].get("hits"),
        "83cebf_attestation": sc1["83cebf"]["attestation"],
        "83cebf_blind_from": sc1["83cebf"]["sources_vs_blind_from"],
        "f0e5a4_must_not_read": sc1["f0e5a4"]["sources_vs_must_not_read"],
        "pass": sc1.get("comparator_TASK-20260926-59169c_blocked") is False
                and all("non-blocking" in d for d in sc1.get("defects", [])),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--wt", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {"snapshot_a524be32e": check_root(a.root), "working_tree": check_root(a.wt)}
    json.dump(res, open(a.out, "w"), indent=1)
    allp = all(v["pass"] for r in res.values() for k, v in r.items() if k.startswith("check") and isinstance(v, dict) and "pass" in v)
    allp = allp and all(v["pass"] for r in res.values() for v in r["check2_seals"].values())
    allp = allp and all(v["pass"] for r in res.values() for v in r["check3_blind_inputs_vs_58d32c"].values())
    print("CP-1 ALL PASS" if allp else "CP-1 FAILURE", file=sys.stderr)


if __name__ == "__main__":
    main()
