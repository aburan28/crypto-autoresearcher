#!/usr/bin/env python3
"""Comment- and string-aware scan of Lean sources for holes and trusted-base escapes.

Written independently for the SHF-20261016-3caa6f re-audit (B3.2). Reads the files
named on the command line (or a list from stdin with '-'); writes nothing.

Masks nested /- -/ block comments (incl. doc comments), -- line comments and
"..." string literals, keeping line numbers, then reports code-level hits.
Also reports raw (unmasked) mentions so a reader can see what was masked.
"""
import re
import sys
from pathlib import Path

PATTERNS = [
    ("sorry", r"\bsorry\b"),
    ("admit", r"\badmit\b"),
    ("sorryAx", r"\bsorryAx\b"),
    ("axiom_decl", r"(^|\s|\])axiom\s+[^\s:]+"),
    ("native_decide", r"\bnative_decide\b"),
    ("decide_native_opt", r"decide\s*\+\s*native|\bdecide\s*\(\s*config"),
    ("ofReduceBool", r"\bofReduceBool\b|\breduceBool\b"),
    ("trustCompiler", r"\btrustCompiler\b"),
    ("implemented_by", r"\bimplemented_by\b"),
    ("extern", r"@\[\s*extern\b|\bextern\b"),
    ("unsafe", r"\bunsafe\b"),
    ("#exit", r"#exit\b"),
    ("skipKernelTC", r"skipKernelTC"),
    ("debug_option", r"set_option\s+debug\."),
    ("metaprog", r"^\s*(elab|macro|macro_rules|syntax|elab_rules|initialize|builtin_initialize|run_cmd|run_elab|run_meta)\b"),
    ("csimp", r"@\[\s*csimp"),
    ("opaque", r"^\s*(private\s+|noncomputable\s+)*opaque\b"),
]


def mask(text: str) -> str:
    out = list(text)
    i, n, depth = 0, len(text), 0
    while i < n:
        if depth:
            if text.startswith("/-", i):
                out[i] = out[i + 1] = " "; depth += 1; i += 2; continue
            if text.startswith("-/", i):
                out[i] = out[i + 1] = " "; depth -= 1; i += 2; continue
            if text[i] != "\n":
                out[i] = " "
            i += 1; continue
        if text.startswith("/-", i):
            out[i] = out[i + 1] = " "; depth = 1; i += 2; continue
        if text.startswith("--", i):
            while i < n and text[i] != "\n":
                out[i] = " "; i += 1
            continue
        if text[i] == '"':
            # mask string literal (keep the quotes out of the code too)
            out[i] = " "; i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n:
                    out[i] = " "
                    if text[i + 1] != "\n":
                        out[i + 1] = " "
                    i += 2; continue
                if text[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = " "; i += 1
            continue
        i += 1
    return "".join(out)


def scan(path: Path):
    text = path.read_text(encoding="utf-8")
    code = mask(text)
    hits, raw = [], []
    for label, pat in PATTERNS:
        rx = re.compile(pat, re.MULTILINE)
        for m in rx.finditer(code):
            line = code.count("\n", 0, m.start()) + 1
            hits.append((label, line, text.splitlines()[line - 1].strip()[:110]))
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            raw.append((label, line))
    return hits, raw


def main(argv):
    files = argv[1:]
    if files == ["-"]:
        files = [l.strip() for l in sys.stdin if l.strip()]
    total = 0
    for f in files:
        p = Path(f)
        hits, raw = scan(p)
        masked_only = sorted(set(raw) - {(l, n) for l, n, _ in hits})
        status = "CLEAN" if not hits else "HITS"
        print(f"{status}\t{f}\tcode_hits={len(hits)}\tcomment_or_string_mentions={len(masked_only)}")
        for label, line, src in hits:
            total += 1
            print(f"    {label}\tL{line}\t{src}")
        for label, line in masked_only:
            print(f"    (masked) {label}\tL{line}")
    print(f"TOTAL_CODE_HITS={total} FILES={len(files)}")


if __name__ == "__main__":
    main(sys.argv)
