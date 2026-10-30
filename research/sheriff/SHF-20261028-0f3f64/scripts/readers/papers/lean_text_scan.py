#!/usr/bin/env python3
"""Text-level B3 scan (no Lean toolchain; nothing executed from crypto) of the
three Lean projects the prior findings L3, L5, L6, L-N1, L-N2, L-N7 concern.

For each .lean file at a pinned commit: strip comments (line `--`, nested
block `/- -/`) and string literals, then report trusted-base escapes and
holes, the theorem/lemma/def names declared, and which declared theorems the
project's AxiomAudit.lean audits. Also reads crypto:tools/lean/trusted-native.txt.

Usage: python3 -I lean_text_scan.py /home/user/crypto <rev>
"""
import re
import subprocess
import sys

repo, rev = sys.argv[1], sys.argv[2]
PROJECTS = {
    "TreeSplit": "research/ic_tree_split_structured_v_20261011/lean/",
    "conductor_gap": "research/conductor_gap_cm_pairs_20261010/lean/",
    "S3Roots": "papers/rootfinding-decomposition/lean/",
}
TOKENS = ["sorry", "admit", "native_decide", "ofReduceBool", "trustCompiler",
          "implemented_by", "extern", "unsafe", "#exit", "skipKernelTC", "decide",
          "run_cmd", "elab", "macro", "syntax", "initialize"]


def git(*args):
    return subprocess.run(["git", "-C", repo, "-c", "gc.auto=0", *args],
                          capture_output=True, check=True).stdout.decode()


def strip(src):
    out, i, n, depth = [], 0, len(src), 0
    while i < n:
        if depth == 0 and src.startswith("--", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if src.startswith("/-", i):
            depth += 1
            i += 2
            continue
        if depth and src.startswith("-/", i):
            depth -= 1
            i += 2
            continue
        if depth:
            out.append("\n" if src[i] == "\n" else " ")
            i += 1
            continue
        if src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append('""')
            i = j + 1
            continue
        out.append(src[i])
        i += 1
    return "".join(out)


files = [l for l in git("ls-tree", "-r", "--name-only", rev).splitlines()
         if l.endswith(".lean") and any(l.startswith(p) for p in PROJECTS.values())]
print(f"commit {rev}")
for name, prefix in PROJECTS.items():
    pf = [f for f in files if f.startswith(prefix)]
    print(f"\n== project {name} ({prefix}): {len(pf)} .lean files")
    declared, audited = [], set()
    for f in sorted(pf):
        src = git("show", f"{rev}:{f}")
        code = strip(src)
        ns_stack = []
        hits = []
        for ln, line in enumerate(code.splitlines(), 1):
            m = re.match(r"\s*namespace\s+(\S+)", line)
            if m:
                ns_stack.append(m.group(1))
            m = re.match(r"\s*end\s+(\S+)", line)
            if m and ns_stack and ns_stack[-1] == m.group(1):
                ns_stack.pop()
            for t in TOKENS:
                pat = r"(?<![\w.`])" + re.escape(t) + r"(?![\w])"
                if re.search(pat, line):
                    hits.append((ln, t, line.strip()[:110]))
            if re.match(r"\s*(private\s+|protected\s+)?axiom\s", line):
                hits.append((ln, "axiom-decl", line.strip()[:110]))
            m = re.match(r"\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma|def|instance)\s+([^\s:({\[]+)", line)
            if m:
                full = ".".join(ns_stack + [m.group(2)])
                declared.append((m.group(1), full, f, ln))
        if f.endswith("AxiomAudit.lean"):
            audited |= set(re.findall(r"`([A-Za-z_][\w.]*)", code))
            audited |= set(re.findall(r"#print\s+axioms\s+([\w.]+)", code))
        print(f"  {f}: {len(src.splitlines())} lines; flagged tokens (comment/string-stripped):")
        for ln, t, s in hits:
            print(f"    L{ln} [{t}] {s}")
        if not hits:
            print("    none")
    thms = [d for d in declared if d[0] in ("theorem", "lemma")]
    print(f"  theorems/lemmas declared: {len(thms)}")
    for kind, full, f, ln in thms:
        mark = "audited" if full in audited else "NOT in AxiomAudit"
        print(f"    {full}  ({f.rsplit('/', 1)[1]}:{ln})  {mark}")
    defs_audited = [a for a in sorted(audited) if a not in {t[1] for t in thms} and "." in a]
    print(f"  AxiomAudit names that are not theorems/lemmas here: {defs_audited}")

print("\n== crypto:tools/lean/trusted-native.txt (non-comment entries)")
for line in git("show", f"{rev}:tools/lean/trusted-native.txt").splitlines():
    if line.strip() and not line.lstrip().startswith("#"):
        print("  " + line)
