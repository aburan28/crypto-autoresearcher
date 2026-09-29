"""Archived-instance loading and the deterministic set-selection rules of
EXP-CERTBIN-e94b27 (spec instance_sets). Zero sampling: every set is a rule
on archived records of RUN-CERTBIN-3b7e05; no seed, no draw.
"""
import gzip
import hashlib
import json
import os

import numpy as np

from macaulay import descended_E, affine_basis, affine_combine, EQ_MONS, NEQ, mono_mask

EXPECTED = {"U62": 62, "S62": 62, "C20": 20, "N-AFF62": 62, "N-F262": 62}
SET_FAMILY = {"U62": "F-S3", "S62": "F-S3", "C20": "F-S3", "N-AFF62": "F-AFF-1", "N-F262": "F-NULLF2"}
SET_ORDER = ["U62", "S62", "C20", "N-AFF62", "N-F262"]
EQ_MASKS = [mono_mask(m) for m in EQ_MONS]


class ContractDefect(Exception):
    pass


def read_targets(src, fam):
    recs = [json.loads(line) for line in gzip.open(os.path.join(src, f"targets-{fam}.jsonl.gz"), "rt")]
    by = {}
    for r in recs:
        by.setdefault(r["idx"], {})[r["D"]] = r
    return by


def load_source(src):
    curve = json.load(open(os.path.join(src, "curve.json")))
    p1 = json.load(gzip.open(os.path.join(src, "checkpoint", "p1-instances.json.gz"), "rt"))
    tg = {fam: read_targets(src, fam) for fam in ("F-S3", "F-AFF-1", "F-NULLF2")}
    return curve, p1, tg


def _arch(r3, r4):
    return {"s": r4["s"], "stratum": r4["stratum"], "degenerate": r4["degenerate"],
            "x_R": r4["x_R"], "rank_4": r4["rank"], "one_in_R_4": r4["one_in_R"],
            "rank_3": r3["rank"], "one_in_R_3": r3["one_in_R"],
            "stratum_D3": r3["stratum"], "s_D3": r3["s"]}


def select_sets(tg):
    """Returns {set: [instance dict]} by the frozen rules, ascending idx."""
    s3 = tg["F-S3"]
    idxs = sorted(s3)
    sets = {}
    sets["U62"] = [i for i in idxs if s3[i][4]["stratum"] == "unsat" and s3[i][4]["one_in_R"] is False]
    sets["S62"] = [i for i in idxs if s3[i][4]["stratum"] == "sat"][:62]
    sets["C20"] = [i for i in idxs if s3[i][4]["stratum"] == "unsat" and s3[i][4]["one_in_R"] is True][:20]
    aff = tg["F-AFF-1"]
    sets["N-AFF62"] = [i for i in sorted(aff) if aff[i][4]["stratum"] == "unsat" and not aff[i][4]["degenerate"]][:62]
    nf = tg["F-NULLF2"]
    sets["N-F262"] = [i for i in sorted(nf) if nf[i][4]["stratum"] == "unsat"][:62]
    out = {}
    for name in SET_ORDER:
        fam = SET_FAMILY[name]
        out[name] = [{"set": name, "family": fam, "idx": i, "key": f"{name}:{fam}:{i}",
                      "archived": _arch(tg[fam][i][3], tg[fam][i][4])} for i in sets[name]]
    counts = {k: len(v) for k, v in out.items()}
    if counts != EXPECTED:
        raise ContractDefect(f"set sizes {counts} != expected {EXPECTED}")
    return out


def E_from_hex(hx):
    E = np.zeros((NEQ, len(EQ_MONS)), dtype=np.uint8)
    for k, h in enumerate(hx):
        v = int(h, 16)
        for j in range(len(EQ_MONS)):
            E[k, j] = (v >> j) & 1
    return E


def E_to_hex(E):
    out = []
    for row in E:
        v = 0
        for j in np.flatnonzero(row):
            v |= 1 << int(j)
        out.append(format(v, "x"))
    return out


def eqs_of(E):
    return [[EQ_MASKS[j] for j in np.flatnonzero(E[k])] for k in range(NEQ)]


def build_instances(F, curve, p1, sets):
    """Attach E (17 x 172) to every instance and run the C-NULLS structural
    identities. Returns (structural check dict)."""
    B = curve["B"]
    E0, Ej = affine_basis(F, B)
    U = E0.astype(bool).copy()
    for x in Ej:
        U |= x.astype(bool)
    aff = p1["F-AFF-1"]
    A0 = E_from_hex(aff["A0_hex"])
    Aj = [E_from_hex(h) for h in aff["Aj_hex"]]
    nf_by_idx = {t["idx"]: t for t in p1["F-NULLF2"]["targets"]}
    aff_by_idx = {t["idx"]: t for t in aff["targets"]}
    s3_by_idx = {t["idx"]: t for t in p1["F-S3"]["targets"]}
    checks = {"F-AFF-1_two_way_identity_fail": [], "F-NULLF2_support_outside_U": [],
              "union_support_size_per_eq_recomputed": [int(x) for x in U.sum(axis=1)],
              "union_support_size_per_eq_archived": p1["F-NULLF2"]["union_support_size_per_eq"],
              "p1_vs_targets_mismatch": []}
    checks["union_support_matches_archive"] = (checks["union_support_size_per_eq_recomputed"]
                                               == checks["union_support_size_per_eq_archived"])
    for name, lst in sets.items():
        for inst in lst:
            a = inst["archived"]
            if inst["family"] == "F-S3":
                xR = a["x_R"]
                if s3_by_idx[inst["idx"]]["x_R"] != xR or s3_by_idx[inst["idx"]]["s"] != a["s"]:
                    checks["p1_vs_targets_mismatch"].append(inst["key"])
                E = descended_E(F, B, xR)
            elif inst["family"] == "F-AFF-1":
                t = aff_by_idx[inst["idx"]]
                r = a["x_R"]
                if t["x_R"] != r or t["s"] != a["s"]:
                    checks["p1_vs_targets_mismatch"].append(inst["key"])
                E = affine_combine(A0, Aj, r)
                rb = np.array([(r >> j) & 1 for j in range(NEQ)], dtype=np.int64)
                alt = ((A0.astype(np.int64) + np.tensordot(rb, np.stack(Aj).astype(np.int64), axes=1)) % 2).astype(np.uint8)
                if not np.array_equal(E, alt):
                    checks["F-AFF-1_two_way_identity_fail"].append(inst["key"])
            else:
                t = nf_by_idx[inst["idx"]]
                if t["s"] != a["s"]:
                    checks["p1_vs_targets_mismatch"].append(inst["key"])
                E = E_from_hex(t["E_hex"])
                if np.any(E.astype(bool) & ~U):
                    checks["F-NULLF2_support_outside_U"].append(inst["key"])
            inst["E"] = E
            inst["E_hex"] = E_to_hex(E)
            inst["E_sha256"] = hashlib.sha256(json.dumps(inst["E_hex"]).encode()).hexdigest()
    checks["pass"] = (not checks["F-AFF-1_two_way_identity_fail"] and not checks["F-NULLF2_support_outside_U"]
                      and checks["union_support_matches_archive"] and not checks["p1_vs_targets_mismatch"])
    return checks
