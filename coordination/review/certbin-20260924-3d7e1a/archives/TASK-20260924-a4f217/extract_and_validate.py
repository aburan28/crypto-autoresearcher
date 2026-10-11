#!/usr/bin/env python3
"""TASK-20260924-a4f217 SC-3/SC-4: mechanical, whitelisted blind-input extraction
and validation for REVIEW-CERTBIN-20260924-3d7e1a. Run from the repository root.

Copies instance inputs only. Writes no set/family/idx/key/stratum/rank/flag or
closure value into blind/. Any failed validation raises and nothing is written
by the caller's commit step.
"""
import gzip, hashlib, json, os, random, sys

ROOT = os.getcwd()
IMPL = os.path.join(ROOT, "experiments/EXP-CERTBIN-e94b27/impl")
sys.path.insert(0, IMPL)
from macaulay import EQ_MONS          # noqa: E402
from instances import E_from_hex, E_to_hex   # noqa: E402
import gf2n                            # noqa: E402

RID = "REVIEW-CERTBIN-20260924-3d7e1a"
OUT = "coordination/review/certbin-20260924-3d7e1a"
RUN = "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
S1 = "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
V4_SEED = 20260924417   # declared seed for the V4 random points

sets = json.load(open(f"{RUN}/instance-sets.json"))["sets"]
curve = json.load(open(f"{S1}/curve.json"))


def lowest(name, k):
    return sorted(sets[name], key=lambda r: r["idx"])[:k]


pool = [(r, "U62") for r in sets["U62"]] + [(r, "S62") for r in lowest("S62", 10)] \
     + [(r, "C20") for r in lowest("C20", 5)] + [(r, "N-AFF62") for r in lowest("N-AFF62", 10)] \
     + [(r, "N-F262") for r in lowest("N-F262", 10)]
order = sorted(pool, key=lambda p: hashlib.sha256((RID + "|" + p[0]["key"]).encode()).hexdigest())


def monos(E_row):
    return [list(EQ_MONS[j]) for j in range(len(EQ_MONS)) if E_row[j]]


def equations(hx):
    E = E_from_hex(hx)
    return [monos(E[k]) for k in range(E.shape[0])]


instances, key = [], {}
for i, (r, s) in enumerate(order, 1):
    lab = "BI-%03d" % i
    if s in ("U62", "S62", "C20"):
        instances.append({"label": lab, "kind": "curve", "x_R": int(r["archived"]["x_R"])})
    else:
        instances.append({"label": lab, "kind": "explicit", "equations": equations(r["E_hex"])})
    key[lab] = {"key": r["key"], "set": s, "family": r["family"], "idx": r["idx"]}

blind = {
    "schema": "certbin.rc1.blind_inputs.v1",
    "review_id": RID,
    "field": {"n": 17, "modulus": "t^17 + t^3 + 1", "encoding": "17-bit integer, bit j = coefficient of t^j"},
    "m": 2, "l": 9,
    "V": "span{1, t, ..., t^8} (degree < 9)",
    "variables": "v_0..v_17; x_1 = sum_{j<9} v_j t^j, x_2 = sum_{j<9} v_{9+j} t^j",
    "monomial_encoding": "a multilinear monomial is the ascending list of its variable indices; [] is the constant 1",
    "curve": {"A": int(curve["A"]), "B": int(curve["B"])},
    "instances": instances,
}
nulls = {"convention": "equation k is row k of instances.E_from_hex(E_hex) (EXP-CERTBIN-e94b27 impl/instances.py); "
                       "column j is monomial macaulay.EQ_MONS[j] = mu_order(2) (degree-ascending, lexicographic tuples); "
                       "each monomial written as its ascending variable-index list"}
for s in ("N-AFF62", "N-F262"):
    for r in sets[s]:
        nulls[r["key"]] = {"set": s, "family": r["family"], "idx": r["idx"], "equations": equations(r["E_hex"])}

# ---- V1 ----
from collections import Counter
cnt = Counter(key[l]["set"] for l in key)
assert cnt == Counter({"U62": 62, "S62": 10, "C20": 5, "N-AFF62": 10, "N-F262": 10}), cnt
assert len(set(key)) == 97 and len({v["key"] for v in key.values()}) == 97
hs = [hashlib.sha256((RID + "|" + key["BI-%03d" % i]["key"]).encode()).hexdigest() for i in range(1, 98)]
assert hs == sorted(hs)
# ---- V2 ----
tg = {}
for line in gzip.open(f"{S1}/targets-F-S3.jsonl.gz", "rt"):
    rec = json.loads(line); tg.setdefault(rec["idx"], rec["x_R"])
for inst in instances:
    if inst["kind"] == "curve":
        m = key[inst["label"]]
        assert inst["x_R"] == tg[m["idx"]], inst["label"]
        assert isinstance(inst["x_R"], int) and 0 <= inst["x_R"] < 2 ** 17
assert blind["curve"] == {"A": curve["A"], "B": curve["B"]}
# ---- V3 ----
# V3 source deviation (recorded in the receipt): targets-F-NULLF2.jsonl.gz carries no E_hex;
# the archived F-NULLF2 systems are in the Stage-1 checkpoint p1-instances.json.gz (hash-bound
# by the TASK-20260923-c2e57b receipt), which is the file RC-1 itself read.
p1 = json.load(gzip.open(f"{S1}/checkpoint/p1-instances.json.gz", "rt"))
nf2 = {t["idx"]: t["E_hex"] for t in p1["F-NULLF2"]["targets"]}
n_nf2 = 0
for s in ("N-AFF62", "N-F262"):
    for r in sets[s]:
        E = E_from_hex(r["E_hex"])
        assert E_to_hex(E) == r["E_hex"], r["key"]
        if s == "N-F262":
            assert r["idx"] in nf2, ("no archived F-NULLF2 E_hex for idx", r["idx"])
            assert nf2[r["idx"]] == r["E_hex"], r["key"]; n_nf2 += 1
assert n_nf2 == 62
# ---- V4 ----
F = gf2n.TableField()
B = int(curve["B"])
def s3(x1, x2, x3):
    a = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.sqr(a) ^ F.mul(F.mul(x1, x2), x3) ^ B
rng = random.Random(V4_SEED)
for r in lowest("U62", 5):
    E = E_from_hex(r["E_hex"]); xR = int(r["archived"]["x_R"])
    for _ in range(256):
        v = [rng.getrandbits(1) for _ in range(18)]
        x1 = sum(v[j] << j for j in range(9)); x2 = sum(v[9 + j] << j for j in range(9))
        target = s3(x1, x2, xR)
        for k in range(17):
            val = 0
            for j in range(len(EQ_MONS)):
                if E[k, j] and all(v[i] for i in EQ_MONS[j]): val ^= 1
            assert val == (target >> k) & 1, (r["key"], k)
# ---- V5 ----
assert set(blind) == {"schema", "review_id", "field", "m", "l", "V", "variables", "monomial_encoding", "curve", "instances"}
for inst in instances:
    assert set(inst) in ({"label", "kind", "x_R"}, {"label", "kind", "equations"})

os.makedirs(f"{OUT}/blind", exist_ok=True); os.makedirs(f"{OUT}/systems", exist_ok=True)
for path, obj in ((f"{OUT}/blind/blind-inputs.json", blind), (f"{OUT}/blind-inputs-key.json", key),
                  (f"{OUT}/systems/null-systems.json", nulls)):
    with open(path, "w") as f: json.dump(obj, f, separators=(",", ":")); f.write("\n")
print("V1-V5 PASS; wrote 3 files; V4 seed", V4_SEED)
