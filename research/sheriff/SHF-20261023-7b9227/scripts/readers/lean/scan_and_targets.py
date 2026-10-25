#!/usr/bin/env python3
"""Comment/string-aware scan of the in-scope Lean files for holes and
trusted-base escapes; namespace coverage; target-yaml binding; imports map.
Usage: python3 -I scan_and_targets.py <repo-root> <modules.txt-out>
"""
import hashlib, json, re, sys, glob, os
ROOT, MODOUT = sys.argv[1], sys.argv[2]
FILES = """Binstd/Factorization Binstd/YieldCeiling Endosweep/DkExactBatch4
FrobTrace/CharacteristicFive FrobTrace/FactorKernel FrobTrace/FiniteFieldTrace
FrobTrace/NullCurveOrder FrobTrace/OrderFive FrobTrace/QuotientMatrices
FrobTrace/QuotientMatrixKernels NCP/AffineNormalForm NCP/CommutatorIdeal
NCP/Reachability Semaev/BooleanParityDegreeThreeRankCertificate
Semaev/BooleanParityFiltrationCertificate Semaev/BooleanParityFiniteCertificate
Semaev/BooleanParitySemanticRankCertificate Semaev/Certificate
Semaev/FiniteEquationSemantics""".split()
paths = [f"{ROOT}/formal/CryptoResearch/{f}.lean" for f in FILES]
paths.append(f"{ROOT}/docs/reports/2026-10-22-semaev-first-fall-replay/evidence/finite-equation-lean-eval.lean")

def strip(src):
    out = []; i = 0; n = len(src); depth = 0
    while i < n:
        if depth == 0 and src.startswith("--", i):
            j = src.find("\n", i); i = n if j < 0 else j; continue
        if src.startswith("/-", i):
            depth += 1; i += 2; continue
        if depth and src.startswith("-/", i):
            depth -= 1; i += 2; continue
        if depth:
            if src[i] == "\n": out.append("\n")
            i += 1; continue
        if src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append('""'); i = j + 1; continue
        out.append(src[i]); i += 1
    return "".join(out)

PAT = {
    "sorry": r"\bsorry\b", "admit": r"\badmit\b", "axiom": r"(^|\s)axiom\s",
    "native_decide": r"native_decide", "ofReduceBool": r"ofReduceBool|trustCompiler",
    "implemented_by": r"implemented_by", "extern": r"@\[\s*extern", "unsafe": r"\bunsafe\b",
    "#exit": r"#exit", "skipKernelTC": r"skipKernelTC", "decide_true_trick": r"decide\s*:=\s*true",
    "opaque": r"(^|\s)opaque\s", "csimp": r"csimp", "macro/elab/syntax": r"(^|\s)(macro|macro_rules|elab|elab_rules|syntax|initialize|builtin_initialize|run_cmd|run_elab|run_meta)\b",
    "Lean.Elab/Meta usage": r"\bLean\.(Elab|Meta)\b|open Lean\b", "#eval": r"#eval", "attribute": r"attribute\s*\[",
    "Classical instance": r"open\s+Classical|propDecidable",
}
res = {}
mods = []
for p in paths:
    raw = open(p).read(); s = strip(raw)
    rel = os.path.relpath(p, ROOT)
    hits = {k: [ln + 1 for ln, line in enumerate(s.split("\n")) if re.search(v, line)] for k, v in PAT.items()}
    hits = {k: v for k, v in hits.items() if v}
    setopts = [line.strip() for line in s.split("\n") if line.strip().startswith("set_option")]
    imports = [l.split()[1] for l in s.split("\n") if l.startswith("import ")]
    nss = re.findall(r"^namespace\s+(\S+)", s, re.M)
    decls = re.findall(r"^(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma|def|abbrev|instance|structure|inductive)\s+(\S+)", s, re.M)
    toplevel_outside_ns = []
    depthns = []
    for line in s.split("\n"):
        m = re.match(r"^namespace\s+(\S+)", line)
        if m: depthns.append(m.group(1)); continue
        m = re.match(r"^end\s+(\S+)", line)
        if m and depthns and depthns[-1] == m.group(1): depthns.pop(); continue
        m = re.match(r"^(?:private\s+|noncomputable\s+)*(theorem|lemma|def|abbrev|structure|inductive)\s+(\S+)", line)
        if m and not depthns: toplevel_outside_ns.append(m.group(2))
    res[rel] = dict(sha256=hashlib.sha256(raw.encode()).hexdigest(), bytes=len(raw), hits=hits,
                    set_option=setopts, imports=imports, namespaces=nss,
                    n_theorems=sum(1 for k, _ in decls if k in ("theorem", "lemma")),
                    decls_outside_namespace=toplevel_outside_ns,
                    all_namespaces_under_CryptoResearch=all(n.startswith("CryptoResearch") or not n[0].isupper() for n in nss))
    if rel.startswith("formal/CryptoResearch/"):
        mod = rel[len("formal/"):-len(".lean")].replace("/", ".")
        mods.append(f"{mod}\t{','.join(imports)}")

# targets
tg = {}
for t in sorted(glob.glob(f"{ROOT}/formal/targets/*.yaml")):
    txt = open(t).read()
    tn = re.search(r"^theorem_name:\s*(\S+)", txt, re.M)
    tf = re.search(r"^theorem_file:\s*(\S+)", txt, re.M)
    if not tn or not tf: continue
    tfp = f"{ROOT}/formal/{tf.group(1)}"
    rel = os.path.relpath(tfp, ROOT)
    if rel not in res: continue
    full = tn.group(1)
    s = strip(open(tfp).read())
    # resolve fully-qualified names declared in file
    stack = []; found = set()
    for line in s.split("\n"):
        m = re.match(r"^namespace\s+(\S+)", line)
        if m: stack.append(m.group(1)); continue
        m = re.match(r"^end\s+(\S+)", line)
        if m and stack and stack[-1] == m.group(1): stack.pop(); continue
        m = re.match(r"^(?:private\s+|protected\s+)*(theorem|lemma)\s+(\S+)", line)
        if m: found.add(".".join(stack + [m.group(2)]))
    tg[os.path.basename(t)] = dict(theorem_name=full, theorem_file=tf.group(1), file_exists=os.path.exists(tfp),
                                   theorem_declared=full in found, private=bool(re.search(r"private\s+theorem\s+" + re.escape(full.split('.')[-1]) + r"\b", s)))
covered_files = {v["theorem_file"] for v in tg.values()}
uncovered = [r for r in res if r.startswith("formal/") and r[len("formal/"):] not in covered_files]
open(MODOUT, "w").write("\n".join(mods) + "\n")
print(json.dumps(dict(scan=res, targets=tg, modules_without_target=uncovered), indent=1))
