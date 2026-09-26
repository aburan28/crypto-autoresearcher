#!/usr/bin/env python3
"""TASK-20260926-58d32c SC-3..SC-6: mechanical, whitelisted blind-input
extraction, validation and protected-literal hashing for
REVIEW-CERTBIN-20260926-089841 (RUN-CERTBIN-6ebb0e, EXP-CERTBIN-ddfe75).

Run from the repository root, on the merged head, BEFORE the archive commit:

    PYTHONDONTWRITEBYTECODE=1 python3 \
      coordination/review/certbin-20260926-089841/archives/TASK-20260926-58d32c/extract_and_validate.py

Optional, only on a V6 hazard (see below): `--v6-show` prints the matched
tokens to the TERMINAL only, for the non-blind dispatching session applying
DEC-20260926-1adf4e R-5 (b); `--v6-accepted <REF>` records that ruling and
proceeds:

    ... extract_and_validate.py --v6-accepted <DECISION-OR-RECEIPT-REF>

What it does (review plan blind_rederivation.parameters, DEC-20260926-1adf4e R-5):
  * copies instance INPUTS only. blind/ receives the field, curve, the 144-slot
    x_R table of the frozen xr144 order, and 55 pool systems as explicit
    equations with opaque labels. No arm, role, slot, key, s, rank, flag,
    closure value or certificate is written into blind/;
  * writes blind-inputs-key.json (label -> key, arm, role, slot, group) OUTSIDE
    blind/;
  * derives the protected literals from the run's decision-rules.json,
    cell-summary.json and closures.jsonl.gz, drops every token of the frozen
    pre-data texts, and writes ONLY their sha256 into blind-phase-hygiene.yaml
    by replacing the single marker line; it never prints a literal;
  * writes extraction-log.json (validation results, counts and hashes; no
    measured value).

It imports nothing from experiments/*/impl/, experiments/*/verifier/ or src/.
The E layout is decoded from the specification's object.E_layout text with this
file's own code (review plan PD-R6), and the convention is cross-checked by
direct F_{2^17} evaluation of S_3 (V4).

Exit status: 0 = all validations pass and outputs written; 2 = a V1-V5 failure
(AssertionError; NOTHING is written); 3 = V6 hygiene hazard (a protected token
occurs in an opening text; NOTHING is written; the Coordinator decides).
"""
import gzip
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter
from itertools import combinations

RID = "REVIEW-CERTBIN-20260926-089841"
TASK = "TASK-20260926-58d32c"
OUT = "coordination/review/certbin-20260926-089841"
ARCH = f"{OUT}/archives/{TASK}"
EXP = "experiments/EXP-CERTBIN-ddfe75"
RUN = f"{EXP}/runs/RUN-CERTBIN-6ebb0e"
RECEIPT_40B2CA = "coordination/design/certbin-nconv-20260924/archives/TASK-20260924-40b2ca/snapshot-receipt.json"
RC1_SETS = "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"
RC1_SETS_SHA = "64dffd01f693289ac533aec3348319cea6c85ffaaea11c4d63ddcd607cd85a7a"   # spec inputs.files
CURVE = "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json"
CURVE_SHA = "aa3eb4d0f3e9da68d710b8946e2e4c3d13de1b991882f23218d259df9615201d"      # spec inputs.files
HYGIENE = f"{OUT}/blind-phase-hygiene.yaml"
MARKER = "  protected_sha256: {}  # FILLED-AT-ARCHIVE-BY-TASK-20260926-58d32c\n"
V4_SEED = 2026092689199      # declared seed for the V4 random evaluation points
V4_POINTS = 256

FROZEN_TEXTS = [             # pre-data texts; their tokens are never protected
    f"{EXP}/specification.yaml",
    f"{EXP}/trial-plan-v1.json",
    "ledger/hypotheses/H-CERTBIN-be6cbd.yaml",
    "ledger/decisions/DEC-20260924-833c70.yaml",
    "ledger/proposals/IDEA-20260924-8b28ea.yaml",
]
OPENING_TEXTS = [            # Coordinator-written at review opening; V6 scans them
    f"{OUT}/review-plan.yaml",
    HYGIENE,
    f"{ARCH}/extract_and_validate.py",
    "ledger/decisions/DEC-20260926-1adf4e.yaml",
] + [f"ledger/handoffs/TASK-20260926-{t}.yaml" for t in
     ("58d32c", "83cebf", "f0e5a4", "0f8aec", "c58e87", "59169c", "9c0134", "7a06ad")]

FRESH = ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"]
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")  # = tools/check_review_independence.py

# ---------------------------------------------------------------------------
# specification object.E_layout, own code
# ---------------------------------------------------------------------------
NV, NEQ, NCOL = 18, 17, 172
COLS = [()] + [(i,) for i in range(NV)] + list(combinations(range(NV), 2))
assert len(COLS) == NCOL
COLMASK = [sum(1 << i for i in m) for m in COLS]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def decode(E_hex):
    assert isinstance(E_hex, list) and len(E_hex) == NEQ, "E_hex is not a list of 17 rows"
    rows = []
    for h in E_hex:
        assert isinstance(h, str) and re.fullmatch(r"[0-9a-f]+", h), "E_hex row is not lowercase hex"
        r = int(h, 16)
        assert r >> NCOL == 0, "E_hex row wider than 172 bits"
        rows.append(r)
    return rows


def equations(rows):
    return [[list(COLS[j]) for j in range(NCOL) if (r >> j) & 1] for r in rows]


# ---------------------------------------------------------------------------
# F_{2^17} = F_2[t]/(t^17 + t^3 + 1), own code (V4)
# ---------------------------------------------------------------------------
MOD = (1 << 17) | (1 << 3) | 1


def fmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & (1 << 17):
            a ^= MOD
    return r


def s3(x1, x2, x3, B):
    """S_3 = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B (EXP-CERTBIN-4e92d7 object.summation_polynomial)."""
    a = fmul(x1, x2) ^ fmul(x1, x3) ^ fmul(x2, x3)
    return fmul(a, a) ^ fmul(fmul(x1, x2), x3) ^ B


def main(argv):
    v6_accepted = None
    if "--v6-accepted" in argv:
        v6_accepted = argv[argv.index("--v6-accepted") + 1]
    assert os.path.isfile("AGENTS.md") and os.path.isdir(RUN), "run from the repository root"

    # ---- input bindings (content first) --------------------------------------
    receipt = json.load(open(RECEIPT_40B2CA))
    bound = receipt["path_sha256"]
    run_inputs = [f"{RUN}/instances.jsonl.gz", f"{RUN}/decision-rules.json",
                  f"{RUN}/cell-summary.json", f"{RUN}/closures.jsonl.gz",
                  f"{EXP}/trial-plan-v1.json"]
    input_sha = {}
    for p in run_inputs:
        input_sha[p] = sha256_file(p)
        assert input_sha[p] == bound[p], ("input differs from the 40b2ca receipt", p)
    input_sha[RC1_SETS] = sha256_file(RC1_SETS)
    assert input_sha[RC1_SETS] == RC1_SETS_SHA, "RC-1 instance-sets.json differs from the specification binding"
    input_sha[CURVE] = sha256_file(CURVE)
    assert input_sha[CURVE] == CURVE_SHA, "curve.json differs from the specification binding"

    recs = [json.loads(l) for l in gzip.open(f"{RUN}/instances.jsonl.gz", "rt") if l.strip()]
    by_key = {}
    for r in recs:
        assert r["key"] not in by_key, ("duplicate key in instances.jsonl.gz", r["key"])
        by_key[r["key"]] = r
    sets = json.load(open(RC1_SETS))["sets"]
    curve = json.load(open(CURVE))
    A, B = int(curve["A"]), int(curve["B"])

    # ---- slot table: specification instance_sets.xr144 -------------------------
    slots = []
    for sname, n in (("U62", 62), ("S62", 62), ("C20", 20)):
        assert len(sets[sname]) == n, ("archived set size", sname)
        slots += [int(r["archived"]["x_R"]) for r in sets[sname]]
    assert len(slots) == 144
    u62_idx = [r["idx"] for r in sets["U62"]]
    assert u62_idx == sorted(u62_idx), "U62 listed order is not ascending idx (xr144 rule)"
    listed_order_ascending = {s: [r["idx"] for r in sets[s]] == sorted(r["idx"] for r in sets[s])
                              for s in ("S62", "C20")}

    # ---- pool: review plan blind_rederivation.parameters ------------------------
    SA = set(range(10)) | {62, 63, 64, 124, 125, 126}
    first5, first3 = set(range(5)), set(range(3))
    groups = [
        ("P-A", lambda r: r["arm"] == "N-CONV" and r["role"] == "unsat" and r["slot"] in SA, 16),
        ("P-B", lambda r: r["arm"] == "N-CONV" and r["role"] == "sat" and r["slot"] in first5, 5),
        ("P-C", lambda r: r["arm"] in ("S3-U62", "S3-S62", "S3-C20") and r["slot"] in SA, 16),
        ("P-D", lambda r: r["arm"] == "N-CONVL" and r["role"] == "unsat" and r["slot"] in first5, 5),
        ("P-E", lambda r: r["arm"] == "N-CONV17" and r["role"] == "unsat" and r["slot"] in first5, 5),
        ("P-F", lambda r: r["arm"] == "N-ELL144" and r["role"] == "unsat" and r["slot"] in first5, 5),
        ("P-G", lambda r: r["arm"] == "NULL-F262" and r["slot"] in first3, 3),
    ]
    pool = []
    for g, pred, n in groups:
        sel = [r for r in recs if pred(r)]
        assert len(sel) == n, ("pool group size", g, len(sel), n)
        pool += [(g, r) for r in sel]
    assert len(pool) == 55 and len({r["key"] for _, r in pool}) == 55
    assert sorted(r["slot"] for g, r in pool if g == "P-C") == sorted(SA), "P-C does not cover SA"
    assert sorted(r["slot"] for g, r in pool if g == "P-A") == sorted(SA), "P-A does not cover SA"
    assert all(r["role"] == "unsat" for g, r in pool if g == "P-G")

    def order_key(item):
        return hashlib.sha256((RID + "|" + item[1]["key"]).encode()).hexdigest()
    order = sorted(pool, key=order_key)

    systems, keymap, canonical_hex = [], {}, 0
    for i, (g, r) in enumerate(order, 1):
        lab = "BS-%03d" % i
        rows = decode(r["E_hex"])
        canonical_hex += int([format(x, "x") for x in rows] == r["E_hex"])
        systems.append({"label": lab, "equations": equations(rows)})
        keymap[lab] = {"key": r["key"], "arm": r["arm"], "role": r["role"], "slot": r["slot"], "group": g}

    blind = {
        "schema": "certbin.nconv.blind_inputs.v1",
        "review_id": RID,
        "field": {"n": 17, "modulus": "t^17 + t^3 + 1", "encoding": "17-bit integer, bit j = coefficient of t^j"},
        "m": 2,
        "l": 9,
        "V": "span{1, t, ..., t^8} (degree < 9)",
        "variables": "v_0..v_17; x_1 = sum_{j<9} v_j t^j, x_2 = sum_{j<9} v_{9+j} t^j",
        "monomial_encoding": "a multilinear monomial is the ascending list of its variable indices; [] is the constant 1",
        "curve": {"A": A, "B": B},
        "slots_note": "the 144 archived targets x_R in the slot order of EXP-CERTBIN-ddfe75 instance_sets.xr144",
        "slots": [{"slot": i, "x_R": x} for i, x in enumerate(slots)],
        "systems": systems,
    }

    # ---- V1: pool counts, labels, order ------------------------------------------
    cnt = Counter(v["group"] for v in keymap.values())
    assert cnt == Counter({"P-A": 16, "P-B": 5, "P-C": 16, "P-D": 5, "P-E": 5, "P-F": 5, "P-G": 3}), cnt
    assert len(keymap) == 55 and len({v["key"] for v in keymap.values()}) == 55
    hs = [hashlib.sha256((RID + "|" + keymap["BS-%03d" % i]["key"]).encode()).hexdigest() for i in range(1, 56)]
    assert hs == sorted(hs)

    # ---- V2: slot binding and curve ------------------------------------------------
    n_bound = 0
    for r in recs:
        if r["arm"] in ("N-CONV", "N-CONVL", "S3-U62", "S3-S62", "S3-C20"):
            assert isinstance(r["slot"], int) and 0 <= r["slot"] < 144, ("slot", r["key"])
            assert r["x_R"] == slots[r["slot"]], ("x_R does not match the xr144 slot table", r["key"])
            n_bound += 1
        elif r["arm"] in ("N-CONV17", "N-ELL144"):
            assert r["x_R"] is None, ("x_R should be null", r["key"])
    assert all(isinstance(x, int) and 0 <= x < 2 ** 17 for x in slots)
    assert curve["A"] == A and curve["B"] == B

    # ---- V3: record integrity of every pool system ----------------------------------
    for g, r in pool:
        assert hashlib.sha256(json.dumps(r["E_hex"]).encode()).hexdigest() == r["E_sha256"], ("E_sha256", r["key"])

    # ---- V4: decoding convention against direct S_3 evaluation (P-C systems) -------
    t = 2
    for _ in range(17):
        t = fmul(t, t)
    assert t == 2 and fmul(1, 1) == 1, "t^(2^17) != t: modulus arithmetic is wrong"
    rng = random.Random(V4_SEED)
    n_v4 = 0
    for g, r in order:
        if g != "P-C":
            continue
        rows = decode(r["E_hex"])
        xR = r["x_R"]
        for _ in range(V4_POINTS):
            v = rng.getrandbits(18)
            x1, x2 = v & 0x1FF, (v >> 9) & 0x1FF
            target = s3(x1, x2, xR, B)
            for k in range(NEQ):
                val, x = 0, rows[k]
                while x:
                    j = (x & -x).bit_length() - 1
                    if v & COLMASK[j] == COLMASK[j]:
                        val ^= 1
                    x &= x - 1
                assert val == (target >> k) & 1, ("V4 convention mismatch", r["key"], k)
            n_v4 += 1

    # ---- V5: blind-input shape -------------------------------------------------------
    assert set(blind) == {"schema", "review_id", "field", "m", "l", "V", "variables", "monomial_encoding",
                          "curve", "slots_note", "slots", "systems"}
    for s in blind["systems"]:
        assert set(s) == {"label", "equations"} and len(s["equations"]) == NEQ
        for eq in s["equations"]:
            for mon in eq:
                assert mon == sorted(set(mon)) and len(mon) <= 2 and all(0 <= i < NV for i in mon)
    for s in blind["slots"]:
        assert set(s) == {"slot", "x_R"}

    # ---- protected literals (SC-5; never printed) --------------------------------------
    frozen = set()
    for p in FROZEN_TEXTS:
        frozen |= set(TOKEN_RE.findall(open(p, encoding="utf-8").read()))
    cands = set()

    def add_num(o):
        if isinstance(o, bool) or o is None:
            return
        if isinstance(o, int):
            if abs(o) >= 10:
                cands.add(str(o))
        elif isinstance(o, float):
            if o != o or o in (float("inf"), float("-inf")):
                return
            if o.is_integer():
                if abs(o) >= 10:
                    cands.add(str(int(o)))
            else:
                cands.update({repr(o), f"{o:.6f}", f"{o:.4f}", f"{o:.3f}"})
                if 0 < o < 1:
                    cands.update({f"{100 * o:.1f}", f"{100 * o:.2f}"})

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            for tok in re.findall(r"-?\d+\.\d+", o):
                add_num(float(tok))
        else:
            add_num(o)

    walk(json.load(open(f"{RUN}/decision-rules.json")))
    walk(json.load(open(f"{RUN}/cell-summary.json")))
    ext = {}
    for line in gzip.open(f"{RUN}/closures.jsonl.gz", "rt"):
        if not line.strip():
            continue
        c = json.loads(line)
        if c.get("arm") not in FRESH:
            continue
        if c.get("closure") == "M_4":
            fields = ("rank", "P", "fallen")
        elif c.get("closure") == "W_4":
            fields = ("final_dim",)
        else:
            continue
        for f in fields:
            v = c.get(f)
            if isinstance(v, int) and not isinstance(v, bool):
                lo, hi = ext.get((c["arm"], c.get("role"), c["closure"], f), (v, v))
                ext[(c["arm"], c.get("role"), c["closure"], f)] = (min(lo, v), max(hi, v))
    for lo, hi in ext.values():
        add_num(lo)
        add_num(hi)
    kept = sorted(c for c in cands if TOKEN_RE.fullmatch(c) and c not in frozen)
    assert kept, "no protected literal derived"
    kept_set = set(kept)
    digests = sorted(hashlib.sha256(c.encode()).hexdigest() for c in kept)

    # ---- V6: opening texts must state no protected token ---------------------------------
    v6 = {}
    for p in OPENING_TEXTS:
        assert os.path.isfile(p), ("opening text missing", p)
        v6[p] = len(set(TOKEN_RE.findall(open(p, encoding="utf-8").read())) & kept_set)
    v6_total = sum(v6.values())
    if v6_total and "--v6-show" in argv:
        # TERMINAL ONLY, for the non-blind dispatching session applying
        # DEC-20260926-1adf4e R-5 (b). Never redirect this to a file, commit
        # message, PR text or bus message.
        for p in OPENING_TEXTS:
            hits = sorted(set(TOKEN_RE.findall(open(p, encoding="utf-8").read())) & kept_set)
            if hits:
                print("V6-SHOW %s: %s" % (p, hits))
    if v6_total and not v6_accepted:
        print("V6 HYGIENE HAZARD: %d protected token(s) occur in opening texts; per file: %s. "
              "Nothing written. Apply DEC-20260926-1adf4e R-5 (b), then re-run with "
              "--v6-accepted <ref> or stop for the Coordinator."
              % (v6_total, json.dumps({k: n for k, n in v6.items() if n})))
        return 3

    # ---- writes (only after every validation passed) -------------------------------------
    htext = open(HYGIENE, encoding="utf-8").read()
    assert htext.count(MARKER) == 1, "hygiene marker absent or duplicated (already filled? restore from git)"
    block = "  protected_sha256:\n" + "".join(
        "    %s: protected RUN-CERTBIN-6ebb0e item p%03d\n" % (d, i) for i, d in enumerate(digests, 1))
    os.makedirs(f"{OUT}/blind", exist_ok=True)
    outputs = ((f"{OUT}/blind/blind-inputs.json", blind), (f"{OUT}/blind-inputs-key.json", keymap))
    for path, obj in outputs:
        with open(path, "w") as f:
            json.dump(obj, f, separators=(",", ":"))
            f.write("\n")
    with open(HYGIENE, "w", encoding="utf-8") as f:
        f.write(htext.replace(MARKER, block))

    log = {
        "schema": "certbin.nconv.extraction_log.v1",
        "task_id": TASK,
        "review_id": RID,
        "script_sha256": sha256_file(os.path.abspath(__file__)),
        "input_sha256": input_sha,
        "validations": {
            "V1_pool_counts_labels_order": "PASS",
            "V2_slot_binding_and_curve": "PASS (%d slot-bound records checked)" % n_bound,
            "V3_E_sha256_of_pool_records": "PASS",
            "V4_convention_vs_direct_S3": "PASS (%d systems x %d points, seed %d)" % (n_v4, V4_POINTS, V4_SEED),
            "V5_blind_input_shape": "PASS",
            "V6_opening_texts_protected_token_matches": v6,
            "V6_accepted_by": v6_accepted,
        },
        "info": {
            "pool_rows_canonical_hex": "%d of 55" % canonical_hex,
            "rc1_listed_order_ascending_idx": listed_order_ascending,
        },
        "protected_count": len(digests),
        "output_sha256": {p: sha256_file(p) for p in
                          (f"{OUT}/blind/blind-inputs.json", f"{OUT}/blind-inputs-key.json", HYGIENE)},
    }
    with open(f"{ARCH}/extraction-log.json", "w") as f:
        json.dump(log, f, indent=1)
        f.write("\n")
    print("V1-V5 PASS; V6 matches %d%s; wrote blind-inputs.json, blind-inputs-key.json, "
          "hygiene digests (%d), extraction-log.json"
          % (v6_total, " (accepted: %s)" % v6_accepted if v6_accepted else "", len(digests)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except AssertionError as exc:
        print("VALIDATION FAILURE (nothing written): %r" % (exc,))
        sys.exit(2)
