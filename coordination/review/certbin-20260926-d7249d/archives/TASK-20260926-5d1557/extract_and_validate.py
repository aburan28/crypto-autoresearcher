#!/usr/bin/env python3
"""TASK-20260926-5d1557 SC-3..SC-5: mechanical, whitelisted blind-input extraction,
validation and protected-digest generation for REVIEW-CERTBIN-20260926-d7249d
(RUN-CERTBIN-a3fc60, EXP-CERTBIN-060020). Run from the repository root.

Written by the Coordinator under DEC-20260926-f6a749 WITHOUT A SHELL; its author
never executed it. The archive task runs it. It may correct a MECHANICAL defect
(a wrong field name, an import path, a syntax slip) without changing any RULE
below (pool, order, codec, validations, protected-set rule, markers, range); every
correction is recorded in the receipt with its unified diff. A change to a rule
is a STOP for the Coordinator.

INDEPENDENCE. Imports nothing from experiments/*/impl/, experiments/*/verifier/,
src/crypto_autoresearcher/ or any review directory. The E_hex codec, the
F_{2^19} arithmetic and the S_3 descent are written here from the frozen text of
experiments/EXP-CERTBIN-060020/specification.yaml (object.field, curve,
factor_base_and_unknowns, summation_polynomial, descended_system, E_layout).
Only the tokeniser and the history helpers of tools/check_review_independence.py
are imported, so that the protected digests are computed exactly as the checker
tokenises commit messages.

MODES
  (default)            extract the blind pool and validate V1-V5; write
                       blind/blind-inputs.json and blind-inputs-key.json; print
                       the sha256 of each. Writes nothing unless V1-V5 pass.
  --hygiene            compute the protected digest set by DEC-20260926-f6a749
                       R-7 (H-1..H-3) and write it into the Coordinator's
                       skeleton blind-phase-hygiene.yaml. Never prints a literal.
  --classify-history   run the blind-history check over LAUNCH..<head>; classify
                       every hit commit by R-7; if every hit is a false positive,
                       remove those items (recorded under `removed`), rewrite the
                       file and re-check; exit 3 on a STOP (nothing rewritten).
"""
import argparse
import gzip
import hashlib
import itertools
import json
import os
import random
import re
import subprocess
import sys
from collections import Counter

import yaml

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_review_independence as cri  # noqa: E402  (tokeniser + history helpers only)

RID = "REVIEW-CERTBIN-20260926-d7249d"
DECISION = "DEC-20260926-f6a749"
OUT = "coordination/review/certbin-20260926-d7249d"
HYG = f"{OUT}/blind-phase-hygiene.yaml"
EXP = "experiments/EXP-CERTBIN-060020"
RUN = f"{EXP}/runs/RUN-CERTBIN-a3fc60"
SPEC = f"{EXP}/specification.yaml"
HYP = "ledger/hypotheses/H-CERTBIN-e3ac93.yaml"
# The executor's git HEAD at launch (manifest_v2.yaml run.code.commit). Every commit
# reachable from it predates every output of RUN-CERTBIN-a3fc60.
LAUNCH = "fe1080a84f640b3503c6cf5da140ff0c29686e89"
V_SEED = 20260926401          # declared seed for the V2 random evaluation points (not a research seed)
MAX_COMMITS = 5000

# ---- frozen object (specification text) -------------------------------------
N, L, NV, NEQ = 19, 10, 20, 19
MOD = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1       # t^19 + t^5 + t^2 + t + 1
A_LIT, B_LIT = 46693, 306147
# E_layout: column j is the j-th monomial of mu_order(2, 20): degree ascending, then
# ascending sorted index tuple (0 = constant, 1..20 = v_0..v_19, 21..210 = pairs i < j).
MONS = [()] + [(i,) for i in range(NV)] + list(itertools.combinations(range(NV), 2))
NCOL = len(MONS)
assert NCOL == 211 and MOD == 524327

# ---- pool rule (review plan blind_rederivation.parameters; fixed before extraction,
#      by arm, role, family/stratum and keep-order index only; no outcome field) ------
GROUPS = [
    # (group, arm, role, field match, count, input kind)
    ("S3-U400", "S3-U400", "unsat", {}, 40, "curve"),
    ("S3-SAT100", "S3-SAT100", "sat", {}, 5, "curve"),
    ("F-RANDX19/TWIST", "F-RANDX19", "unsat", {"stratum": "TWIST"}, 5, "curve"),
    ("F-RANDX19/X2E", "F-RANDX19", "unsat", {"stratum": "X2E"}, 5, "curve"),
    ("F-RANDX19/XE-NOT-2E", "F-RANDX19", "unsat", {"stratum": "XE-NOT-2E"}, 5, "curve"),
    ("N-CONV19", "N-CONV19", "unsat", {}, 10, "explicit"),
    ("N-ELL19", "N-ELL19", "unsat", {}, 10, "explicit"),
    ("N-F219", "N-F219", "unsat", {}, 5, "explicit"),
] + [("N-AFF19/%d" % d, "N-AFF19", "unsat", {"family": d}, 1, "explicit") for d in range(1, 6)]
POOL_SIZE = sum(g[4] for g in GROUPS)
assert POOL_SIZE == 90

BLIND_KEYS = {"schema", "review_id", "field", "m", "l", "V", "variables",
              "monomial_encoding", "curve", "instances"}

# ---- protected-set rule (DEC-20260926-f6a749 R-7) ----------------------------------
# H-1: the verdict vocabulary of N19-DR-1..9, ALL alternatives (the set carries no
#      information about which verdict was recorded).
VERDICT_WORDS = ["PERSISTS", "DECAYS", "PARTIAL", "UNDETERMINED", "EVALUABLE",
                 "DETECTABLE", "CONSISTENT", "LOWER", "HIGHER", "MIXED",
                 "DISTINGUISHED", "TENSOR", "BELOW", "MODULATED", "WEAK", "ABSENT",
                 "SATURATED", "REPLICATES", "HOLDS", "FAILS", "ELIGIBLE"]
# H-2: numeric tokens of the outcome files, minus every token that occurs in the
#      exclusion corpus (frozen design text and code), so design constants are not
#      protected and outcome-exclusive numbers are.
OUTCOME_FILES = [f"{RUN}/decision-rules.json", f"{RUN}/cell-summary.json", f"{RUN}/run-report.md"]
NUMERIC = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
# R-7 false-positive markers (case-insensitive, in a hit commit's message or paths).
MARKERS = ("060020", "a3fc60", "e3ac93", "132822", "certbin-n19", "d7249d", "f6a749",
           "901ea1", "091c56", "n19", "n = 19", "n=19")


# ---- F_{2^19}, S_3, descent ----------------------------------------------------------
def fmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> N:
            a ^= MOD
    return r


def s3(x1, x2, x3, B):
    a = fmul(x1, x2) ^ fmul(x1, x3) ^ fmul(x2, x3)
    return fmul(a, a) ^ fmul(fmul(x1, x2), x3) ^ B


def x12(u):
    """Assignment integer u, bit i = v_i: x_1 = sum_{j<10} v_j t^j, x_2 = sum_{j<10} v_{10+j} t^j."""
    return u & ((1 << L) - 1), (u >> L) & ((1 << L) - 1)


def descend(xR, B):
    """E_S3(x_R) as a 19 x 211 0/1 list, by Moebius inversion on the subsets of each
    column monomial (exact for the multilinear coefficient of that monomial)."""
    cache = {}

    def f(S):
        u = 0
        for i in S:
            u |= 1 << i
        if u not in cache:
            x1, x2 = x12(u)
            cache[u] = s3(x1, x2, xR, B)
        return cache[u]

    E = [[0] * NCOL for _ in range(NEQ)]
    for j, m in enumerate(MONS):
        acc = 0
        for r in range(len(m) + 1):
            for S in itertools.combinations(m, r):
                acc ^= f(S)
        for k in range(NEQ):
            E[k][j] = (acc >> k) & 1
    return E


# ---- codec (E_layout; bit j LSB-first = column j) -----------------------------------
def E_from_hex(hexes):
    assert len(hexes) == NEQ, "E_hex must have 19 rows"
    E = []
    for h in hexes:
        v = int(h, 16)
        assert v >> NCOL == 0, "E_hex row wider than 211 columns"
        E.append([(v >> j) & 1 for j in range(NCOL)])
    return E


def E_to_hex(E):
    return [format(sum(1 << j for j in range(NCOL) if row[j]), "x") for row in E]


def E_sha256(hexes):
    return hashlib.sha256(json.dumps(hexes, separators=(",", ":")).encode()).hexdigest()


def equations(E):
    return [[list(MONS[j]) for j in range(NCOL) if E[k][j]] for k in range(NEQ)]


def eval_row(row, u):
    val = 0
    for j in range(NCOL):
        if row[j] and all((u >> i) & 1 for i in MONS[j]):
            val ^= 1
    return val


# ---- extraction ----------------------------------------------------------------------
def load_instances():
    with gzip.open(f"{RUN}/instances.jsonl.gz", "rt") as fh:
        recs = [json.loads(line) for line in fh if line.strip()]
    keys = [r["key"] for r in recs]
    assert len(keys) == len(set(keys)), "duplicate instance key in instances.jsonl.gz"
    return recs


def select(recs, arm, role, match, k):
    sel = [r for r in recs if r.get("arm") == arm and r.get("role") == role
           and all(str(r.get(f)) == str(v) for f, v in match.items())]
    sel.sort(key=lambda r: int(r["index"]))
    assert len(sel) >= k, ("pool shortfall", arm, role, match, len(sel))
    return sel[:k]


def sha_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def extract():
    with open(SPEC, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)["experiment"]
    lit = spec["inputs"]["literal_parameters"]
    # ---- V4: literal parameters as frozen ----
    assert int(lit["A"]) == A_LIT and int(lit["B"]) == B_LIT, "V4: curve literals differ from the specification"
    assert "524327" in str(lit["modulus"]), "V4: modulus literal differs from the specification"

    recs = load_instances()
    pool = []
    for group, arm, role, match, k, kind in GROUPS:
        for r in select(recs, arm, role, match, k):
            pool.append((group, kind, r))
    order = sorted(pool, key=lambda p: hashlib.sha256((RID + "|" + p[2]["key"]).encode()).hexdigest())

    rng = random.Random(V_SEED)
    instances, key = [], {}
    for i, (group, kind, r) in enumerate(order, 1):
        lab = "BI-%03d" % i
        hexes = [str(h) for h in r["E_hex"]]
        # ---- V3: codec round trip and E_sha256, every pool instance ----
        assert E_sha256(hexes) == r["E_sha256"], ("V3: E_sha256 mismatch", lab)
        E = E_from_hex(hexes)
        assert E_to_hex(E) == hexes, ("V3: codec round trip", lab)
        if kind == "curve":
            xR = int(r["x_R"])
            # ---- V2: x_R range; own descent equals the archived E; random evaluation ----
            assert (1 << L) <= xR < (1 << N), ("V2: x_R outside [2^10, 2^19)", lab)
            assert descend(xR, B_LIT) == E, ("V2: own S_3 descent differs from archived E_hex", lab)
            for _ in range(64):
                u = rng.getrandbits(NV)
                x1, x2 = x12(u)
                t = s3(x1, x2, xR, B_LIT)
                for kk in range(NEQ):
                    assert eval_row(E[kk], u) == (t >> kk) & 1, ("V2: evaluation", lab, kk)
            instances.append({"label": lab, "kind": "curve", "x_R": xR})
        else:
            instances.append({"label": lab, "kind": "explicit", "equations": equations(E)})
        key[lab] = {"key": r["key"], "arm": r["arm"], "role": r["role"],
                    "index": int(r["index"]), "group": group}

    # ---- V1: pool counts, uniqueness, order ----
    cnt = Counter(v["group"] for v in key.values())
    assert cnt == Counter({g[0]: g[4] for g in GROUPS}), ("V1: pool counts", dict(cnt))
    assert len(key) == POOL_SIZE and len({v["key"] for v in key.values()}) == POOL_SIZE
    hs = [hashlib.sha256((RID + "|" + key["BI-%03d" % i]["key"]).encode()).hexdigest()
          for i in range(1, POOL_SIZE + 1)]
    assert hs == sorted(hs), "V1: label order does not follow the sha256 rule"

    blind = {
        "schema": "certbin.n19.blind_inputs.v1",
        "review_id": RID,
        "field": {"n": N, "modulus": "t^19 + t^5 + t^2 + t + 1", "modulus_int": MOD,
                  "encoding": "19-bit integer, bit j = coefficient of t^j"},
        "m": 2,
        "l": L,
        "V": "span{1, t, ..., t^9} (degree < 10)",
        "variables": "v_0..v_19; x_1 = sum_{j<10} v_j t^j, x_2 = sum_{j<10} v_{10+j} t^j",
        "monomial_encoding": "a multilinear monomial is the ascending list of its variable indices; [] is the constant 1",
        "curve": {"A": A_LIT, "B": B_LIT},
        "instances": instances,
    }
    # ---- V5: exact key sets ----
    assert set(blind) == BLIND_KEYS, "V5: blind-inputs keys"
    for inst in instances:
        assert set(inst) in ({"label", "kind", "x_R"}, {"label", "kind", "equations"}), ("V5", inst["label"])
        if inst["kind"] == "explicit":
            assert len(inst["equations"]) == NEQ, ("V5: equation count", inst["label"])

    os.makedirs(f"{OUT}/blind", exist_ok=True)
    written = []
    for path, obj in ((f"{OUT}/blind/blind-inputs.json", blind), (f"{OUT}/blind-inputs-key.json", key)):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, separators=(",", ":"))
            fh.write("\n")
        written.append(path)
    print("V1-V5 PASS; pool", POOL_SIZE, "; V2 seed", V_SEED)
    for path in written:
        print("sha256", sha_file(path), path)
    return 0


# ---- hygiene -------------------------------------------------------------------------
def corpus_files():
    files = [SPEC, f"{EXP}/trial-plan-v1.json", HYP]
    for sub in ("impl", "verifier"):
        for dirpath, _, names in os.walk(f"{EXP}/{sub}"):
            for name in sorted(names):
                if name.endswith((".py", ".md", ".json", ".sh", ".yaml", ".txt")):
                    files.append(os.path.join(dirpath, name))
    return files


def tokens_of(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return set(cri._TOKEN_RE.findall(fh.read()))


def load_hygiene():
    with open(HYG, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    assert isinstance(doc, dict) and isinstance(doc.get("blind_phase_hygiene"), dict), "hygiene skeleton missing"
    return doc


def write_hygiene(doc):
    with open(HYG, "w", encoding="utf-8") as fh:
        fh.write("# Generated by TASK-20260926-5d1557 extract_and_validate.py from the Coordinator's\n"
                 "# skeleton (DEC-20260926-f6a749 R-7). No protected literal is written in any file.\n")
        yaml.safe_dump(doc, fh, sort_keys=False, width=100, allow_unicode=False)


def hygiene():
    excluded = set()
    for path in corpus_files():
        excluded |= tokens_of(path)
    numeric = set()
    for path in OUTCOME_FILES:
        numeric |= {t for t in tokens_of(path) if NUMERIC.fullmatch(t)}
    h2 = numeric - excluded
    items = set(VERDICT_WORDS) | h2
    digests = sorted(hashlib.sha256(t.encode()).hexdigest() for t in items)
    doc = load_hygiene()
    hy = doc["blind_phase_hygiene"]
    hy["protected_sha256"] = {d: "protected RUN-CERTBIN-a3fc60 item p%03d" % i
                              for i, d in enumerate(digests, 1)}
    hy["removed"] = []
    hy["generated"] = {"by": "TASK-20260926-5d1557 extract_and_validate.py --hygiene",
                       "exclusion_corpus_files": len(corpus_files()),
                       "protected_items": len(digests)}
    write_hygiene(doc)
    print("wrote", HYG, "with", len(digests), "protected digest(s); no literal printed")
    return 0


# ---- history classification (R-7) --------------------------------------------------
def git(*args):
    out = subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), out.stderr.strip()[:200]))
    return out.stdout


def classify(head):
    rng = f"{LAUNCH}..{head}"
    doc = load_hygiene()
    hashes = cri.protected_hashes(doc)
    assert hashes, "empty protected set: run --hygiene first"
    hits = {}
    for sha, body in cri.commit_messages(rng, MAX_COMMITS):
        for digest in cri._token_hashes(body):
            if digest in hashes:
                hits.setdefault(digest, set()).add(sha)
    if not hits:
        print(f"PASS: {rng} states none of {len(hashes)} protected value(s)")
        return 0
    stops, false_pos = [], {}
    for digest, shas in sorted(hits.items()):
        for sha in sorted(shas):
            text = (git("log", "-1", "--format=%B", sha) + "\n"
                    + git("diff-tree", "--no-commit-id", "--name-only", "-r", "-m", "--root", sha)).lower()
            if any(marker in text for marker in MARKERS):
                stops.append((hashes[digest], sha[:9]))
            else:
                false_pos.setdefault(digest, []).append(sha[:9])
    if stops:
        for label, sha in stops:
            print(f"STOP: commit {sha} states {label} and is n = 19-related (R-7); nothing rewritten")
        return 3
    hy = doc["blind_phase_hygiene"]
    for digest, shas in sorted(false_pos.items()):
        hy.setdefault("removed", []).append({"label": hashes[digest], "commits": sorted(shas),
                                             "by": f"{DECISION} R-7"})
        del hy["protected_sha256"][digest]
    write_hygiene(doc)
    problems = cri.check_blind_history(rng, cri.protected_hashes(load_hygiene()), MAX_COMMITS)
    if problems:
        print("STOP: re-check after R-7 removal still fails")
        return 3
    print(f"PASS after {len(false_pos)} R-7 removal(s) over {rng}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hygiene", action="store_true")
    ap.add_argument("--classify-history", action="store_true")
    ap.add_argument("--head", default="HEAD")
    args = ap.parse_args()
    if args.hygiene:
        return hygiene()
    if args.classify_history:
        return classify(args.head)
    return extract()


if __name__ == "__main__":
    raise SystemExit(main())
