#!/usr/bin/env python3
"""The sheriff's deterministic half: sweep, canary and case check.

The `sheriff` skill (`.claude/skills/sheriff/SKILL.md`, manual
`docs/sheriff.md`) audits whether a result is what it says it is. Reading
is the skill's job. This tool does the part that must not depend on a reader:

    python3 tools/sheriff.py sweep --target all [--deep] [--out DIR]
    python3 tools/sheriff.py canary [--json]
    python3 tools/sheriff.py check-case research/sheriff/SHF-...

`sweep` looks at crypto-autoresearcher and its sibling checkouts (`../crypto`,
`../cryptanalysis`, or `--repo NAME=PATH`). It scans Lean sources for holes and
trusted-base escapes, finds zk/STARK verifiers that throw away the values they
were meant to check, and catches dev-mode receipts and execution-proof language.
It traces paper numbers to artifacts, flags strong claim words, and runs every
existing checker it can, recording `not_covered` for each one it cannot. It
writes a new, write-once case directory and prints its path.

`canary` is the instrument's positive control. It plants each defect the sweep
claims to detect in a scratch repository, along with look-alikes that must not
be flagged. It exits non-zero if any plant is missed or any look-alike is
flagged. A sweep records its own canary result, and a case whose canary did not
pass cannot uphold anything (`check-case`).

`check-case` validates the `findings.yaml` the session composes after the reader
pass. It uses a closed verdict vocabulary. An upheld claim needs evidence that
exists on disk. A failed beat or a linked blocker forbids upholding. A
`not_covered` beat is never a pass.

The sweep never edits an audited file. Every checker runs read-only, and the
sweep records `git status` before and after so a checker that wrote anything
is itself a finding. Nothing here changes research state.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable

import yaml

REPO = Path(__file__).resolve().parents[1]
HOME = "crypto-autoresearcher"
SIBLINGS = ("crypto", "cryptanalysis")
CASE_ROOT = "research/sheriff"
SCHEMA = "sheriff.sweep/v1"
CASE_SCHEMA = "sheriff.case/v1"

BEATS = {
    "B2": "execution proofs, STARKs and zk",
    "B3": "Lean and formal proofs",
    "B4": "certificates and verified answers",
    "B5": "cost accounting and comparisons",
    "B6": "statistics, controls and preregistration",
    "B7": "provenance, integrity and reproducibility",
    "B8": "prose, papers and numbers",
}
SEVERITIES = ("blocker", "major", "minor", "info")
VERDICTS = ("upheld", "upheld_scoped", "overclaimed", "unsupported", "broken", "not_covered")
BEAT_STATES = ("pass", "fail", "not_covered", "n/a")
MAX_TEXT_BYTES = 2_000_000
LIST_CAP = 200

# Files that define the vocabulary rather than use it, and corpora that quote
# other people's claims. A proof-language hit there is not a claim of ours.
CONTRACT_PATHS = (
    "AGENTS.md", "CLAUDE.md", "docs/execution-proof-chain.md", "docs/runbook-execution.md",
    "docs/sheriff.md", "docs/cairn-integration-plan.md", "docs/evidence-and-reproducibility.md",
    "tools/sheriff.py", "tools/runbook.py",
)
EXCLUDED_DIRS = (".claude", ".agents", ".codex", "knowledge/literature", "inputs",
                 "third_party", "tests", "node_modules", "vendor", CASE_ROOT,
                 "crypto_source_snapshot")
FIXTURE_PATH = re.compile(
    r"(^|/)(selftest|fixtures?|canary|negative[-_]controls?)(/|$)|(^|/)neg_[^/]*\.lean$")


def finding(beat: str, rule: str, severity: str, message: str, *, repo: str = "",
            path: str = "", line: int | None = None, kind: str = "finding",
            excerpt: str = "") -> dict[str, Any]:
    return {"beat": beat, "rule": rule, "severity": severity, "kind": kind,
            "repo": repo, "path": path, "line": line, "message": message,
            "excerpt": excerpt.strip()[:240]}


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------

def git(repo: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, errors="replace", check=check)


def discover(overrides: list[str], siblings: bool = True) -> dict[str, Path]:
    repos = {HOME: REPO}
    if siblings:
        for name in SIBLINGS:
            path = REPO.parent / name
            if (path / ".git").exists():
                repos[name] = path
    for item in overrides:
        name, _, path = item.partition("=")
        if not name or not path:
            raise SystemExit(f"--repo takes NAME=PATH, got {item!r}")
        repos[name] = Path(path).resolve()
    return repos


def snapshot(name: str, path: Path) -> dict[str, Any]:
    head = git(path, "rev-parse", "HEAD").stdout.strip()
    main = git(path, "rev-parse", "--verify", "-q", "origin/main").stdout.strip() or None
    status = git(path, "status", "--porcelain").stdout
    diff = git(path, "diff", "HEAD").stdout
    return {"path": str(path), "head": head,
            "branch": git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(),
            "origin_main": main, "at_origin_main": bool(main) and main == head,
            "dirty_paths": len(status.splitlines()),
            "tree_digest": hashlib.sha256((status + "\0" + diff).encode()).hexdigest()}


def tracked(repo: Path, pathspecs: Iterable[str] = ()) -> list[str]:
    out = git(repo, "ls-files", "-z", "--", *pathspecs).stdout
    return [p for p in out.split("\0") if p]


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def specs_for(scope: list[str], exts: Iterable[str], repo: Path) -> list[str]:
    """Pathspecs for files with these extensions under each scope entry. A
    non-magic git pathspec's `*` also matches `/`, so `dir/*.md` reaches
    every depth."""
    out: list[str] = []
    for s in scope or [""]:
        if s and (repo / s).is_file():
            out.append(s)
        else:
            out += [f"{s.rstrip('/')}/*{e}" if s else f"*{e}" for e in exts]
    return out


def excluded(rel: str) -> bool:
    return rel in CONTRACT_PATHS or any(rel == d or rel.startswith(d + "/") for d in EXCLUDED_DIRS)


def grep_lines(repo: Path, terms: Iterable[str], pathspecs: Iterable[str]) -> list[tuple[str, int, str]]:
    """Case-insensitive fixed-string prefilter; callers apply the real regex."""
    args = ["grep", "-n", "-I", "-i", "-F", "--no-color"]
    for term in terms:
        args += ["-e", term]
    proc = git(repo, *args, "--", *pathspecs)
    rows = []
    for raw in proc.stdout.splitlines():
        rel, _, rest = raw.partition(":")
        num, _, text = rest.partition(":")
        if num.isdigit() and not excluded(rel):
            rows.append((rel, int(num), text))
    return rows


# ---------------------------------------------------------------------------
# B3: Lean
# ---------------------------------------------------------------------------

LEAN_CHAR = re.compile(r"'(?:\\.|[^\\'\n])'")
LEAN_NAME_LITERAL = re.compile(r"`+[A-Za-z_\u00c0-\uffff][\w.'\u00c0-\uffff]*")


def strip_lean(src: str) -> str:
    """Blank out comments (nested block, line, doc), string and char literals
    and name literals (``Lean.ofReduceBool names a constant, it does not use
    one), keeping every offset so line numbers survive."""
    return LEAN_NAME_LITERAL.sub(lambda m: " " * len(m.group(0)), _strip_lean(src))


def _strip_lean(src: str) -> str:
    out: list[str] = []
    i, n, depth = 0, len(src), 0
    blank = lambda s: "".join("\n" if ch == "\n" else " " for ch in s)  # noqa: E731
    while i < n:
        if depth:
            if src.startswith("/-", i):
                depth, i = depth + 1, i + 2
                out.append("  ")
            elif src.startswith("-/", i):
                depth, i = depth - 1, i + 2
                out.append("  ")
            else:
                out.append(blank(src[i]))
                i += 1
            continue
        if src.startswith("/-", i):
            depth, i = 1, i + 2
            out.append("  ")
        elif src.startswith("--", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append(blank(src[i:j + 1]))
            i = j + 1
        elif src[i] == "'" and (i == 0 or not (src[i - 1].isalnum() or src[i - 1] in "_'.")) \
                and (m := LEAN_CHAR.match(src, i)):
            out.append(" " * len(m.group(0)))
            i = m.end()
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


LEAN_RULES = (
    ("lean.sorry", re.compile(r"\bsorry\b"), "blocker",
     "`sorry`: the statement is assumed, not proved"),
    ("lean.admit", re.compile(r"\badmit\b"), "blocker",
     "`admit`: the goal is closed by `sorry`"),
    ("lean.axiom", re.compile(
        r"(?m)^[ \t]*(?:@\[[^\]\n]*\][ \t]*)?(?:(?:private|protected|noncomputable|unsafe|partial)[ \t]+)*axiom[ \t]+\S"),
     "blocker", "custom `axiom`: everything downstream is conditional on an unchecked assumption"),
    ("lean.skip_kernel", re.compile(r"\bskipKernelTC\b"), "blocker",
     "kernel type checking switched off"),
    ("lean.native_decide", re.compile(r"\bnative_decide\b|\bofReduce(?:Bool|Nat)\b|\btrustCompiler\b"),
     "major", "compiler-trusted evaluation: the kernel did not check this; the compiler and every "
     "`implemented_by` it reaches are in the trusted base"),
    ("lean.implemented_by", re.compile(r"\bimplemented_by\b|@\[\s*extern\b"), "major",
     "`implemented_by`/`extern`: the code that runs is not the definition the kernel sees"),
    ("lean.unsafe", re.compile(r"\bunsafe\b"), "major", "`unsafe` declaration"),
    ("lean.exit", re.compile(r"(?m)^[ \t]*#exit\b"), "major",
     "`#exit`: nothing after it is elaborated, so theorems below it do not exist"),
)
LEAN_META = re.compile(r"(?m)^[ \t]*(?:elab|macro|macro_rules|syntax|run_cmd|run_elab|run_meta|"
                       r"initialize|builtin_initialize)\b")
LEAN_DECL = re.compile(r"\b(?:theorem|lemma)\s+([^\s:(\[{]+)")
LEAN_AUDIT = re.compile(r"collectAxioms|#print\s+axioms|#audit_project")


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def lean_project(repo: Path, rel: str) -> tuple[str | None, str]:
    """(root, kind): nearest lake project, else nearest toolchain pin."""
    parts = Path(rel).parent.parts
    for k in range(len(parts), -1, -1):
        d = Path(*parts[:k]) if k else Path(".")
        if (repo / d / "lakefile.toml").is_file() or (repo / d / "lakefile.lean").is_file():
            return d.as_posix(), "lake"
    for k in range(len(parts), -1, -1):
        d = Path(*parts[:k]) if k else Path(".")
        if (repo / d / "lean-toolchain").is_file():
            return d.as_posix(), "standalone"
    return None, "unpinned"


def scan_lean(name: str, repo: Path, files: list[str], workflows: str) -> tuple[list[dict], dict]:
    found: list[dict] = []
    projects: dict[tuple[str | None, str], dict[str, Any]] = {}
    theorems = 0
    for rel in files:
        raw = read_text(repo / rel)
        if raw is None:
            continue
        code = strip_lean(raw)
        fixture = bool(FIXTURE_PATH.search(rel))
        lines = raw.splitlines()
        for rule, rx, severity, message in LEAN_RULES:
            for m in rx.finditer(code):
                ln = line_of(code, m.start())
                sev, msg = severity, message
                if fixture:
                    sev, msg = "info", message + " (deliberate fixture by path; confirm it is never imported)"
                found.append(finding("B3", rule, sev, msg, repo=name, path=rel, line=ln,
                                     excerpt=lines[ln - 1] if ln <= len(lines) else ""))
        for m in LEAN_META.finditer(code):
            ln = line_of(code, m.start())
            found.append(finding("B3", "lean.metaprogram", "info",
                                 "metaprogramming in a proof file: a reader confirms it adds or alters no declaration",
                                 repo=name, path=rel, line=ln, kind="lead", excerpt=lines[ln - 1]))
        for m in LEAN_DECL.finditer(code):
            theorems += 1
            end = code.find(":=", m.end())
            stmt = code[m.end(): end if end > 0 else m.end() + 400]
            if re.search(r":\s*True\s*$", stmt.strip()):
                ln = line_of(code, m.start())
                found.append(finding("B3", "lean.vacuous", "minor",
                                     f"`{m.group(1)}` concludes `True`: it can say nothing about the claim",
                                     repo=name, path=rel, line=ln, kind="lead", excerpt=lines[ln - 1]))
        root, kind = lean_project(repo, rel)
        proj = projects.setdefault((root, kind), {"files": [], "audit": False})
        proj["files"].append(rel)
        proj["audit"] = proj["audit"] or bool(LEAN_AUDIT.search(code))
    summary = {"files": len(files), "theorem_declarations": theorems, "projects": []}
    for (root, kind), proj in sorted(projects.items(), key=lambda kv: str(kv[0])):
        if all(FIXTURE_PATH.search(f) for f in proj["files"]):
            continue
        label = root or "(repository root, no pin)"
        ci = bool(root) and root != "." and re.search(
            rf"(?<![\w/.-]){re.escape(root)}(?![\w-])", workflows) is not None
        summary["projects"].append({"root": label, "kind": kind, "files": len(proj["files"]),
                                    "axiom_audit": proj["audit"], "ci": ci})
        where = proj["files"][0] if kind == "unpinned" else label
        if kind == "unpinned":
            found.append(finding("B3", "lean.unpinned", "major",
                                 f"{len(proj['files'])} Lean file(s) with no lean-toolchain pin: the build cannot be reproduced",
                                 repo=name, path=where, kind="lead"))
        if not proj["audit"]:
            found.append(finding("B3", "lean.no_axiom_audit", "major",
                                 f"{kind} Lean project with no axiom audit (`collectAxioms`/`#print axioms`): "
                                 "a `sorryAx` or custom axiom reached indirectly would go unseen",
                                 repo=name, path=where, kind="lead"))
        if not ci:
            found.append(finding("B3", "lean.no_ci", "minor",
                                 f"{kind} Lean project not named by any CI workflow: nothing rebuilds it "
                                 "after a toolchain, Mathlib or source change", repo=name, path=where,
                                 kind="lead"))
    return found, summary


# ---------------------------------------------------------------------------
# B2: zk/STARK verifiers, receipts and execution-proof language
# ---------------------------------------------------------------------------

ZK_PATH = re.compile(r"(?i)(^|/)(zk|stark|fri|snark|plonk|groth|bulletproof|verifier)[^/]*(/|\.rs$)")
RUST_VERIFY = re.compile(r"\bfn\s+(verify\w*)\s*(?:<[^>{]*>)?\s*\(")
RUST_DISCARD = re.compile(r"\blet\s+_\s*=\s*([^;]+);")
BARE_NAMES = re.compile(r"^\(?\s*&?[A-Za-z_][\w.]*(\s*,\s*&?[A-Za-z_][\w.]*)*\s*,?\s*\)?$")
TRUST_COMMENT = re.compile(r"(?i)(we trust|trust the|not (?:yet )?(?:checked|verified)|skip(?:ped|s)? "
                           r"(?:the )?check|\bTODO\b|\bFIXME\b|for now|minimal[- ]soundness|we'd compute)")
RUST_TEST = re.compile(r"#\[test\]\s*(?:#\[[^\]]*\]\s*)*fn\s+(\w+)")
NEGATIVE_TEST = re.compile(r"(?i)(tamper|reject|invalid|forg|bad|wrong|corrupt|fail|malicious|sound|mutat|fake)")


def strip_rust(src: str) -> str:
    out: list[str] = []
    i, n = 0, len(src)
    blank = lambda s: "".join("\n" if ch == "\n" else " " for ch in s)  # noqa: E731
    while i < n:
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(blank(src[i:j]))
            i = j
        elif src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append(blank(src[i:j + 1]))
            i = j + 1
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def rust_body(code: str, start: int) -> tuple[int, int] | None:
    """Body span of the fn whose parameter list opens just before `start`;
    None for a bodiless declaration (`fn verify(&self) -> bool;`)."""
    depth, j, brace = 1, start, -1
    while j < len(code) and depth:
        depth += {"(": 1, ")": -1}.get(code[j], 0)
        j += 1
    nest = 0
    while j < len(code):
        ch = code[j]
        if ch in "([<":
            nest += 1
        elif ch in ")]>" and nest:
            nest -= 1
        elif ch == ";" and not nest:
            return None
        elif ch == "{":
            brace = j
            break
        j += 1
    if brace < 0:
        return None
    depth = 0
    for j in range(brace, len(code)):
        if code[j] == "{":
            depth += 1
        elif code[j] == "}":
            depth -= 1
            if depth == 0:
                return brace, j
    return None


def scan_zk(name: str, repo: Path, files: list[str]) -> list[dict]:
    found = []
    for rel in files:
        if not rel.endswith(".rs") or not ZK_PATH.search(rel):
            continue
        raw = read_text(repo / rel)
        if raw is None:
            continue
        code = strip_rust(raw)
        lines = raw.splitlines()
        verifiers = 0
        for m in RUST_VERIFY.finditer(code):
            span = rust_body(code, m.end())
            if not span:
                continue
            verifiers += 1
            body = code[span[0]:span[1]]
            for d in RUST_DISCARD.finditer(body):
                if BARE_NAMES.match(d.group(1).strip()):
                    ln = line_of(code, span[0] + d.start())
                    found.append(finding(
                        "B2", "zk.discarded_value", "major",
                        f"`{m.group(1)}` discards `{d.group(1).strip()}`: a value the verifier reads and "
                        "never checks is a constraint it does not enforce", repo=name, path=rel, line=ln,
                        kind="lead", excerpt=lines[ln - 1]))
            for k, text in enumerate(raw[span[0]:span[1]].splitlines()):
                comment = text.partition("//")[2]
                if comment and TRUST_COMMENT.search(comment):
                    ln = line_of(raw, span[0]) + k
                    found.append(finding("B2", "zk.trust_comment", "minor",
                                         f"`{m.group(1)}` says it trusts or skips a check", repo=name,
                                         path=rel, line=ln, kind="lead", excerpt=text))
        if verifiers:
            tests = RUST_TEST.findall(code)
            if not any(NEGATIVE_TEST.search(t) for t in tests):
                found.append(finding(
                    "B2", "zk.no_negative_test", "major",
                    f"{verifiers} verifier function(s) and {len(tests)} test(s) in this file, none of which "
                    "shows a forged or tampered proof being rejected", repo=name, path=rel, kind="lead"))
    return found


# Claims that one of OUR computations is proved. Zero-knowledge proofs as a
# research topic (FAEST, Picnic, signature schemes) are not such claims.
PROOF_CLAIM = re.compile(
    r"(?i)\b(execution[- ]verified|verified execution|execution[- ]proofs? (?:verified|passed|checked|attached)"
    r"|stark[- ](?:proven|proved|verified|receipts?)|stark proofs? (?:of|for) (?:the|our|this|each|every)"
    r"|zk[- ]?verified|(?:zk|zero[- ]knowledge|succinct) proofs? (?:of|for) (?:the|our|this|each|every) "
    r"(?:run|computation|result|execution|count|search|walk|trial)s?"
    r"|proven computation|verifiabl[ey] (?:computed|executed)|risc ?(?:zero|0) receipts?|sp1 proofs?"
    r"|cryptographically (?:proven|proved|verified))\b")
PROOF_TERMS = ("execution verified", "execution-verified", "verified execution", "execution proof",
               "stark", "zk", "zero-knowledge", "zero knowledge", "succinct proof", "proven computation",
               "verifiabl", "risc zero", "risc0", "sp1 proof", "cryptographically")
DEV_MODE = re.compile(r'"dev_mode"\s*:\s*true|\bdev_mode:\s*true\b|RISC0_DEV_MODE\s*[=:]\s*"?1')
TEXT_SPECS = ("*.md", "*.tex", "*.txt", "*.yaml", "*.yml", "*.rst", "*.typ")


def scan_proof_claims(name: str, repo: Path, scope: list[str]) -> list[dict]:
    specs = specs_for(scope, [g[1:] for g in TEXT_SPECS], repo)
    found = []
    for rel, ln, text in grep_lines(repo, PROOF_TERMS, specs):
        m = PROOF_CLAIM.search(text)
        if m:
            found.append(finding("B2", "zk.proof_language", "minor",
                                 f"says `{m.group(0)}`: needs a pinned-verifier receipt that binds this exact "
                                 "result (docs/execution-proof-chain.md), or the wording is an overclaim",
                                 repo=name, path=rel, line=ln, kind="lead", excerpt=text))
    return found


def scan_dev_mode(name: str, repo: Path, scope: list[str]) -> list[dict]:
    specs = specs_for(scope, (".json", ".jsonl", ".yaml", ".yml", ".env", ".toml"), repo)
    found = []
    for rel, ln, text in grep_lines(repo, ("dev_mode", "RISC0_DEV_MODE"), specs):
        if DEV_MODE.search(text):
            found.append(finding("B2", "zk.dev_mode_receipt", "blocker",
                                 "a dev-mode receipt or RISC0_DEV_MODE setting: dev-mode proofs are fake by design",
                                 repo=name, path=rel, line=ln, excerpt=text))
    return found


# ---------------------------------------------------------------------------
# B8: prose and papers
# ---------------------------------------------------------------------------

STRONG = re.compile(
    r"(?i)\b(breakthrough|beats? (?:pollard[- ])?rho|faster than (?:pollard[- ])?rho|outperform\w*"
    r"|break(?:s|ing)? (?:the )?(?:curve|ecdlp|ecc|discrete log)|prove[sdn]?\b|proof that|verified\b"
    r"|\bsecure\b|orders? of magnitude|massive\w*|sub-?exponential|polynomial[- ]time|weak curve"
    r"|speed-?ups?)")
STRONG_TERMS = ("breakthrough", "rho", "outperform", "break", "prove", "proof that", "verified",
                "secure", "order of magnitude", "orders of magnitude", "massive", "exponential",
                "polynomial", "weak curve", "speedup", "speed-up")
CLAIM_SURFACES = ("papers", "claims", "benchmarks/README.md", "README.md", "PUBLICATION-CANDIDATES.md")


def scan_language(name: str, repo: Path, scope: list[str]) -> tuple[list[dict], dict[str, int]]:
    roots = scope or [s for s in CLAIM_SURFACES if (repo / s).exists()]
    if not roots:
        return [], {}
    specs = specs_for(roots, (".md", ".tex", ".json", ".txt"), repo)
    found, counts = [], {}
    for rel, ln, text in grep_lines(repo, STRONG_TERMS, specs):
        for m in STRONG.finditer(text):
            counts[rel] = counts.get(rel, 0) + 1
            found.append(finding("B8", "prose.strong_claim", "info",
                                 f"`{m.group(0)}`: a reader attaches the artifact that earns this word, "
                                 "or records the overclaim", repo=name, path=rel, line=ln, kind="lead",
                                 excerpt=text))
    return found, counts


TEX_DROP = re.compile(r"\\(?:cite\w*|ref|eqref|cref|Cref|label|url|href|includegraphics|input|include|"
                      r"usepackage|documentclass|bibliography\w*|setlength|vspace|hspace|resizebox)"
                      r"(?:\[[^\]]*\])?\{[^}]*\}")
# A comma joins thousands groups only when the run does not continue a list:
# `{19,37,79,109}` is four numbers, not 79109; plain numbers may follow a comma.
TEX_NUMBER = re.compile(r"(?:(?<![\w.,\\])(\d{1,3}(?:(?:\{,\}|\\,|,)\d{3})+(?![\d,])(?:\.\d+)?)"
                        r"|(?<![\w.\\])(\d+\.\d+|\d{3,}))"
                        r"(?!\s*(?:pt|cm|mm|em|ex|in|bp)\b|\s*\\(?:textwidth|linewidth|columnwidth))")


def tex_numbers(src: str) -> list[tuple[str, int]]:
    out = []
    for k, line in enumerate(src.splitlines(), 1):
        if re.search(r"\\begin\{thebibliography\}|\\bibliography\{|\\printbibliography", line):
            break  # volumes, pages and years of references are not results
        line = re.sub(r"(?<!\\)%.*$", "", line)
        line = TEX_DROP.sub(" ", line)
        for m in TEX_NUMBER.finditer(line):
            raw = m.group(1) or m.group(2)
            plain = re.sub(r"\{,\}|\\,|,", "", raw)
            if re.fullmatch(r"(19|20)\d\d", plain):
                continue
            digits = plain.replace(".", "").lstrip("0")
            if "." in plain and len(digits) < 3 and len(plain.split(".")[1]) < 3:
                continue  # 0.5, 1.25: too short to trace meaningfully
            out.append((plain, k))
    return out


PATH_REF = re.compile(r"(?:(?P<repo>crypto-autoresearcher|cryptanalysis|crypto):)?"
                      r"(?P<path>(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]*)")


def cited_paths(text: str, home: str, repos: dict[str, Path], base: str = "") -> set[tuple[str, str]]:
    """(repo, path) pairs a paper names that exist on disk, read as
    repository-relative or relative to the paper directory `base`. Bare
    top-level directories are dropped: citing `research/` is not citing an
    artifact."""
    text = re.sub(r"\\(?:allowbreak|slash|-)|\{\}", "", text.replace("\\_", "_"))
    out = set()
    for m in PATH_REF.finditer(text):
        path = m.group("path").rstrip(".").rstrip("/")
        path = path[2:] if path.startswith("./") else path
        if path.count("/") < 1 and "." not in path.rsplit("/", 1)[-1]:
            continue
        names = [m.group("repo")] if m.group("repo") else [home, *[n for n in repos if n != home]]
        forms = [path]
        if base and not m.group("repo"):
            local = os.path.normpath(os.path.join(base, path))
            if not local.startswith(".."):
                forms.insert(0, local)
        stripped = re.sub(r"^(?:\.\./)+", "", path)
        if stripped != path:
            forms.append(stripped)
        hit = next(((n, f) for f in forms for n in names
                    if n in repos and f and f != "." and (repos[n] / f).exists()), None)
        if hit:
            out.add(hit)
    return out


NUM_TOKEN = re.compile(r"(?<![\w.])-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.])-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
TRACE_FILE_BYTES = 25_000_000
TRACE_PAPER_BYTES = 400_000_000


def artifact_numbers(repos: dict[str, Path], roots: dict[str, list[str]]) -> tuple[set[str], list[float], dict]:
    """Numeric tokens in the cited artifacts, size-capped. Returns the exact
    strings, their float values, and what was skipped."""
    exact: set[str] = set()
    values: list[float] = []
    skipped = {"large_files": 0, "binary_files": 0, "over_budget_files": 0}
    budget = TRACE_PAPER_BYTES
    for n, paths in roots.items():
        for rel in tracked(repos[n], paths):
            if rel.endswith((".pdf", ".tex", ".bib", ".png", ".jpg", ".gz", ".zip", ".npy", ".bin")):
                continue
            path = repos[n] / rel
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > TRACE_FILE_BYTES:
                skipped["large_files"] += 1
                continue
            if size > budget:
                skipped["over_budget_files"] += 1
                continue
            budget -= size
            data = path.read_bytes()
            if b"\0" in data[:8192]:
                skipped["binary_files"] += 1
                continue
            for tok in NUM_TOKEN.findall(data.decode("utf-8", "replace")):
                tok = tok.replace(",", "")
                if tok not in exact:
                    exact.add(tok)
                    try:
                        values.append(float(tok))
                    except ValueError:
                        pass
    return exact, values, skipped


def rounding_index(exact: set[str], values: list[float], places: set[int]) -> dict[int, set[str]]:
    """For each decimal-place count a paper uses, every artifact value rounded
    or truncated to that many places."""
    rounded: dict[int, set[str]] = {}
    for k in places:
        rounded[k] = {f"{x:.{k}f}" for x in values if abs(x) < 1e15}
        rounded[k] |= {t[: t.index(".") + 1 + k] for t in exact
                       if "." in t and "e" not in t.lower() and len(t.split(".")[1]) >= k}
    return rounded


def is_traced(value: str, exact: set[str], rounded: dict[int, set[str]]) -> bool:
    """Exact, truncated or rounded presence. Truncation and rounding are how
    papers quote measurements; anything looser would trace everything."""
    if value in exact:
        return True
    if "." in value:
        k = len(value.split(".")[1])
        return value in rounded.get(k, set())
    return False


def trace_numbers(name: str, repo: Path, repos: dict[str, Path], scope: list[str]) -> tuple[list[dict], list[dict]]:
    """Every number in a paper should appear in an artifact the paper cites
    (AGENTS.md, "Papers"). Searching the cited artifacts, not whole
    repositories, keeps a coincidental match elsewhere from counting."""
    papers = sorted({"/".join(p.split("/")[:2]) for p in tracked(repo, ["papers/*.tex"]) if p.count("/") >= 2})
    if scope:
        papers = [p for p in papers if any(p == s or p.startswith(s.rstrip("/") + "/") or s.startswith(p) for s in scope)]
    found, summary = [], []
    for paper in papers:
        numbers: dict[str, list[tuple[str, int]]] = {}
        cited: set[tuple[str, str]] = set()
        for rel in tracked(repo, [f"{paper}/*.tex", f"{paper}/*.md", f"{paper}/*.bib"]):
            src = read_text(repo / rel) or ""
            cited |= cited_paths(src, name, repos, base=str(Path(rel).parent))
            if rel.endswith(".tex"):
                for value, ln in tex_numbers(src):
                    numbers.setdefault(value, []).append((rel, ln))
        if not numbers:
            continue
        roots: dict[str, list[str]] = {name: [paper]}
        for n, path in sorted(cited):
            roots.setdefault(n, []).append(path)
        exact, values, skipped = artifact_numbers(repos, roots)
        rounded = rounding_index(exact, values, {len(v.split(".")[1]) for v in numbers if "." in v})
        untraced = [v for v in numbers if not is_traced(v, exact, rounded)]
        summary.append({"repo": name, "paper": paper, "numbers": len(numbers), "cited_paths": len(cited),
                        "traced": len(numbers) - len(untraced), "untraced": len(untraced),
                        "skipped": skipped})
        if not cited:
            found.append(finding("B8", "paper.no_cited_artifacts", "major",
                                 f"{len(numbers)} numbers and no committed artifact path cited: none can be traced",
                                 repo=name, path=paper))
        if any(skipped.values()):
            found.append(finding("B8", "paper.trace_incomplete", "info",
                                 f"tracing skipped cited files: {skipped}", repo=name, path=paper,
                                 kind="not_covered"))
        for value in untraced:
            rel, ln = numbers[value][0]
            found.append(finding("B8", "paper.untraced_number", "minor",
                                 f"`{value}` appears in none of the {len(cited)} artifact path(s) the paper cites, "
                                 "exactly, truncated or rounded: a reader traces it or records it as unsupported",
                                 repo=name, path=rel, line=ln, kind="lead", excerpt=value))
    return found, summary


# ---------------------------------------------------------------------------
# Existing checkers
# ---------------------------------------------------------------------------

def _pending_audits(proc: subprocess.CompletedProcess) -> tuple[str, str]:
    try:
        rows = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return "error", "unparseable output"
    return ("fail", f"{len(rows)} finished runbook session(s) with no audit of their journal tip") \
        if rows else ("pass", "every finished runbook session has an audit")


ECBENCH = "./target/release/ecbench"
CHECKERS: list[dict[str, Any]] = [
    {"id": "progress-fidelity", "repo": HOME, "beat": "B5", "tier": "quick",
     "argv": [sys.executable, "-m", "tools.progress_fidelity", "portfolio", "claims/"]},
    {"id": "runbook-pending-audits", "repo": HOME, "beat": "B7", "tier": "quick",
     "argv": [sys.executable, "tools/runbook.py", "pending-audits", "--json"], "parse": _pending_audits},
    {"id": "claim-class", "repo": HOME, "beat": "B8", "tier": "quick",
     "argv": [sys.executable, "tools/claim_class_audit.py"]},
    {"id": "run-source-provenance", "repo": HOME, "beat": "B7", "tier": "deep", "advisory": True,
     "argv": [sys.executable, "tools/check_run_source_provenance.py"]},
    {"id": "ledger", "repo": HOME, "beat": "B7", "tier": "deep", "timeout": 1200,
     "argv": [sys.executable, "tools/validate_ledger.py"]},
    {"id": "merge-hygiene", "repo": HOME, "beat": "B7", "tier": "deep", "timeout": 1200,
     "argv": [sys.executable, "tools/check_merge_hygiene.py", "--absolute"]},
    {"id": "formal-build-and-axioms", "repo": HOME, "beat": "B3", "tier": "deep", "timeout": 3600,
     "needs_bin": ["lake"], "argv": ["bash", "-c", "cd formal && lake build && lake env lean AxiomAudit.lean"],
     "enable": "./formal/setup.sh (elan + network), then python3 tools/rebuild_formal_root.py --workspace formal"},
    {"id": "formal-targets", "repo": HOME, "beat": "B3", "tier": "deep", "timeout": 3600,
     "needs_bin": ["lake"], "argv": [sys.executable, "tools/verify_formal_targets.py", "--artifact-dir",
                                     "{scratch}/formal-receipts"]},
    {"id": "curve-names", "repo": "crypto", "beat": "B4", "tier": "quick",
     "argv": [sys.executable, "scripts/check_curve_names.py"]},
    {"id": "ecbench-bounds", "repo": "crypto", "beat": "B5", "tier": "deep", "needs": [ECBENCH],
     "argv": ["bash", "-c", f"{ECBENCH} bound check --root . --record docs/bounds/records/*.json"],
     "enable": "cargo build --release --bin ecbench"},
    {"id": "ecbench-challenges", "repo": "crypto", "beat": "B5", "tier": "deep", "needs": [ECBENCH],
     "argv": ["bash", "-c", f"for f in docs/bounds/challenges/*.json; do {ECBENCH} challenge check --file \"$f\" "
              "|| exit 1; done"], "enable": "cargo build --release --bin ecbench"},
    # Every committed ecbench session, not only the globs crypto's CI audits:
    # integrity checks apply to interrupted sessions too (--allow-interrupted,
    # as CI does); sessions outside CI's globs are listed so the gap is seen.
    {"id": "ecbench-sessions-integrity", "repo": "crypto", "beat": "B7", "tier": "deep", "timeout": 3600,
     "needs": [ECBENCH], "enable": "cargo build --release --bin ecbench",
     "argv": ["bash", "-c", "rc=0; n=0; for f in $(git grep -l -E '\"schema\": ?\"ecbench.session/v1\"' -- "
              "'*/session.json'); do d=$(dirname \"$f\"); n=$((n+1)); "
              "case \"$d/\" in research/ecbench_*/sessions/*/|research/ghs_curve_comparison_20261009/sessions/*/|"
              "research/notes/ecc2k130/*_compact_orbit_ic_20261003/sessions/*/) ;; *) echo \"OUTSIDE-CI-GLOBS $d\";; esac; "
              f"{ECBENCH} verify --dir \"$d\" --replay 0 --allow-interrupted --exit-code --out {{scratch}}/v.json "
              ">/dev/null 2>&1 || { echo \"FAIL $d\"; rc=1; }; done; echo \"$n sessions\"; exit $rc"]},
    {"id": "zk-stark-tests", "repo": "crypto", "beat": "B2", "tier": "deep", "timeout": 3600,
     "needs_bin": ["cargo"], "argv": ["cargo", "test", "--release", "--lib", "zk::stark"]},
    {"id": "fb-archive", "repo": "cryptanalysis", "beat": "B7", "tier": "quick",
     "argv": [sys.executable, "experiments/fb-archive/fbarchive.py", "verify"]},
    {"id": "fb-refs", "repo": "cryptanalysis", "beat": "B7", "tier": "quick",
     "argv": [sys.executable, "experiments/fb-archive/refs.py", "check"]},
    {"id": "lean-gate-selftest", "repo": "cryptanalysis", "beat": "B3", "tier": "deep", "timeout": 3600,
     "needs_bin": ["lake"], "argv": ["bash", "tools/lean/selftest/run.sh"]},
    {"id": "lean-proof-gate", "repo": "cryptanalysis", "beat": "B3", "tier": "deep", "timeout": 3600,
     "needs_bin": ["lake"], "argv": ["bash", "tools/lean/proof-gate.sh"]},
]


def run_checker(spec: dict[str, Any], repo: Path | None, deep: bool, scratch: Path) -> dict[str, Any]:
    row = {"id": spec["id"], "repo": spec["repo"], "beat": spec["beat"], "tier": spec["tier"],
           "command": " ".join(spec["argv"]).replace("{scratch}", "<scratch>")}
    if repo is None:
        return {**row, "status": "not_covered", "reason": f"repository {spec['repo']} is not checked out"}
    if spec["tier"] == "deep" and not deep:
        return {**row, "status": "not_covered", "reason": "deep tier not requested (--deep)"}
    missing = [b for b in spec.get("needs_bin", []) if not shutil.which(b)]
    missing += [p for p in spec.get("needs", []) if not (repo / p).exists()]
    if missing:
        return {**row, "status": "not_covered", "reason": f"missing: {', '.join(missing)}",
                "enable": spec.get("enable", "")}
    argv = [a.replace("{scratch}", str(scratch)) for a in spec["argv"]]
    start = time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True, errors="replace",
                              timeout=spec.get("timeout", 600))
    except subprocess.TimeoutExpired:
        return {**row, "status": "error", "reason": f"timed out after {spec.get('timeout', 600)} s",
                "seconds": round(time.monotonic() - start, 1)}
    tail = (proc.stdout + ("\n" + proc.stderr if proc.stderr.strip() else "")).strip()[-4000:]
    status, note = ("pass" if proc.returncode == 0 else "fail"), ""
    if status == "fail" and git(repo, "config", "--bool", "core.sparseCheckout").stdout.strip() == "true":
        note = "sparse checkout: a missing file can fail this checker; confirm on a full checkout"
    if "parse" in spec and proc.returncode == 0:
        status, note = spec["parse"](proc)
    if status == "fail" and spec.get("advisory"):
        status = "advisory"
    return {**row, "status": status, "exit_code": proc.returncode, "note": note,
            "seconds": round(time.monotonic() - start, 1), "tail": tail}


# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------

def resolve_target(target: str, repos: dict[str, Path]) -> dict[str, list[str]]:
    """repo name -> scope paths (empty list: whole repository)."""
    if target == "all":
        return {name: [] for name in repos}
    name, sep, rest = target.partition(":")
    if sep and name in repos:
        rest = rest.strip("/")
        return {name: [] if rest in ("", ".") else [rest]}
    if re.fullmatch(r"(EXP|RUN)-[\w-]+", target):
        hits = sorted({p.split(f"/{target}/")[0] + f"/{target}"
                       for p in tracked(REPO, [f"**/{target}/**"])})
        if not hits:
            raise SystemExit(f"no tracked path names {target}")
        return {HOME: hits}
    path = Path(target)
    for repo_name, root in repos.items():
        try:
            rel = (path if path.is_absolute() else (Path.cwd() / path)).resolve().relative_to(root)
        except ValueError:
            continue
        if (root / rel).exists():
            return {repo_name: [rel.as_posix()]}
    raise SystemExit(f"cannot resolve target {target!r} (use all, EXP-*, RUN-*, a path, or repo:path)")


def mint_case(root: Path) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
    for _ in range(20):
        case = root / CASE_ROOT / f"SHF-{stamp}-{secrets.token_hex(3)}"
        if not case.exists():
            return case
    raise SystemExit("could not mint a free SHF id")


def scan_repo(name: str, repo: Path, scope: list[str], repos: dict[str, Path]) -> tuple[list[dict], dict]:
    specs = [f"{s}/**" if (repo / s).is_dir() else s for s in scope] if scope else []
    files = tracked(repo, specs)
    workflows = "\n".join(read_text(p) or "" for p in sorted((repo / ".github/workflows").glob("*.y*ml")))
    lean_files = [f for f in files if f.endswith(".lean") and not excluded(f)]
    lean, lean_summary = scan_lean(name, repo, lean_files, workflows)
    zk = scan_zk(name, repo, files)
    claims = scan_proof_claims(name, repo, scope)
    dev = scan_dev_mode(name, repo, scope)
    prose, prose_counts = scan_language(name, repo, scope)
    numbers, number_summary = trace_numbers(name, repo, repos, scope)
    summary = {"lean": lean_summary, "strong_words_by_file": dict(sorted(
        prose_counts.items(), key=lambda kv: -kv[1])[:40]), "papers": number_summary}
    return lean + zk + claims + dev + prose + numbers, summary


def cap(rows: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """Keep every blocker/major/minor finding; cap leads per rule and repo."""
    kept, dropped, per = [], {}, {}
    for row in rows:
        key = f"{row['repo']}:{row['rule']}"
        if row["kind"] == "lead" and row["severity"] in ("info", "minor"):
            per[key] = per.get(key, 0) + 1
            if per[key] > LIST_CAP:
                dropped[key] = dropped.get(key, 0) + 1
                continue
        kept.append(row)
    return kept, dropped


def sweep(args: argparse.Namespace) -> int:
    repos = discover(args.repo, siblings=not args.no_siblings)
    scopes = resolve_target(args.target, repos)
    out = Path(args.out) if args.out else mint_case(REPO)
    if out.exists():
        raise SystemExit(f"{out} exists: a sweep writes a new directory, never over an old one")
    started = dt.datetime.now(dt.timezone.utc)
    canary_result = canary()
    before = {n: snapshot(n, p) for n, p in repos.items()}
    rows: list[dict] = []
    summaries: dict[str, Any] = {}
    for name, scope in scopes.items():
        found, summary = scan_repo(name, repos[name], scope, repos)
        rows += found
        summaries[name] = summary
    checks = []
    if not args.no_checkers:
        with tempfile.TemporaryDirectory(prefix="sheriff-") as scratch:
            for spec in CHECKERS:
                if spec["repo"] in scopes or spec["repo"] not in repos:
                    checks.append(run_checker(spec, repos.get(spec["repo"]), args.deep, Path(scratch)))
    after = {n: snapshot(n, p) for n, p in repos.items()}
    for name in repos:
        if after[name]["tree_digest"] != before[name]["tree_digest"] or after[name]["head"] != before[name]["head"]:
            rows.append(finding("B7", "sheriff.checker_wrote", "major",
                                "the working tree changed while the sweep ran: a checker is not read-only",
                                repo=name))
    for check in checks:
        if check["status"] in ("fail", "error"):
            rows.append(finding(check["beat"], f"check.{check['id']}",
                                "major" if check["status"] == "fail" else "minor",
                                f"existing checker `{check['id']}` {check['status']}: "
                                f"{check.get('note') or check.get('reason') or 'see sweep.json tail'}",
                                repo=check["repo"]))
        elif check["status"] == "advisory":
            rows.append(finding(check["beat"], f"check.{check['id']}", "minor",
                                f"advisory checker `{check['id']}` reported findings", repo=check["repo"],
                                kind="lead"))
        elif check["status"] == "not_covered":
            rows.append(finding(check["beat"], f"check.{check['id']}", "info",
                                f"`{check['id']}` not run: {check['reason']}", repo=check["repo"],
                                kind="not_covered"))
    if not canary_result["passed"]:
        rows.append(finding("B7", "sheriff.canary_failed", "blocker",
                            "the instrument missed a planted defect or flagged a clean control; "
                            "no verdict from this sweep may be relied on", kind="finding"))
    kept, dropped = cap(rows)
    record = {
        "schema": SCHEMA, "case": out.name, "target": args.target, "scopes": scopes,
        "instrument": {"path": "tools/sheriff.py",
                       "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                       "repo_head": before[HOME]["head"] if HOME in before else None},
        "started_at": started.isoformat(), "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "deep": args.deep, "repos": before, "canary": canary_result, "checks": checks,
        "summary": summaries, "counts": tally(rows), "findings": kept, "leads_dropped_over_cap": dropped,
        "establishes": "which deterministic checks ran on which commits, and what they flagged",
        "does_not_establish": [
            "that any claim is true: verdicts come from the reader pass (findings.yaml)",
            "anything a not_covered check would have tested",
            "execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)",
            "statement fidelity of any Lean theorem: that is a reader's check",
        ],
    }
    out.mkdir(parents=True)
    (out / "sweep.json").write_text(json.dumps(record, indent=2, sort_keys=False) + "\n")
    (out / "sweep.md").write_text(render_md(record))
    (out / "sweep.svg").write_text(render_svg(record))
    print(out.relative_to(REPO) if out.is_relative_to(REPO) else out)
    print(json.dumps(record["counts"]["by_severity"]), file=sys.stderr)
    return 0 if canary_result["passed"] else 1


def tally(rows: list[dict]) -> dict[str, Any]:
    by_sev = {s: 0 for s in SEVERITIES}
    by_beat: dict[str, dict[str, int]] = {}
    for row in rows:
        label = "not_covered" if row["kind"] == "not_covered" else row["severity"]
        by_sev[label] = by_sev.get(label, 0) + 1
        beat = by_beat.setdefault(row["beat"], {})
        beat[label] = beat.get(label, 0) + 1
    return {"by_severity": by_sev, "by_beat": dict(sorted(by_beat.items()))}


def render_md(rec: dict[str, Any]) -> str:
    out = [f"# Sheriff sweep {rec['case']}", "",
           "Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks "
           "flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.", "",
           f"- target: `{rec['target']}`; deep tier: {rec['deep']}",
           f"- started {rec['started_at']}, finished {rec['finished_at']}",
           f"- canary (positive control): **{'passed' if rec['canary']['passed'] else 'FAILED'}** "
           f"({len(rec['canary']['caught'])} plants caught, {len(rec['canary']['missed'])} missed, "
           f"{len(rec['canary']['false_positives'])} false positives)", "",
           "| repository | HEAD | branch | at origin/main | dirty paths |", "| --- | --- | --- | --- | --- |"]
    for name, r in rec["repos"].items():
        out.append(f"| {name} | `{r['head'][:12]}` | {r['branch']} | {r['at_origin_main']} | {r['dirty_paths']} |")
    out += ["", "## Counts", "", "| beat | " + " | ".join([*SEVERITIES, "not_covered"]) + " |",
            "| --- |" + " --- |" * (len(SEVERITIES) + 1)]
    for beat, c in rec["counts"]["by_beat"].items():
        out.append(f"| {beat} {BEATS.get(beat, '')} | " +
                   " | ".join(str(c.get(s, 0)) for s in [*SEVERITIES, "not_covered"]) + " |")
    out += ["", "## Checkers", "", "| checker | repo | beat | status | note |", "| --- | --- | --- | --- | --- |"]
    for c in rec["checks"]:
        note = (c.get("note") or c.get("reason") or "").replace("|", "/")
        out.append(f"| `{c['id']}` | {c['repo']} | {c['beat']} | {c['status']} | {note} |")
    for title, keep in (("Blockers", ("blocker",)), ("Major", ("major",))):
        rows = [f for f in rec["findings"] if f["severity"] in keep and f["kind"] != "not_covered"]
        out += ["", f"## {title} ({len(rows)})", ""]
        for f in rows:
            where = f"{f['repo']}:{f['path']}" + (f":{f['line']}" if f["line"] else "")
            out.append(f"- **{f['rule']}** ({f['kind']}) `{where}`: {f['message']}")
    minor = [f for f in rec["findings"] if f["severity"] in ("minor", "info") and f["kind"] != "not_covered"]
    by_rule: dict[str, int] = {}
    for f in minor:
        by_rule[f"{f['repo']}:{f['rule']}"] = by_rule.get(f"{f['repo']}:{f['rule']}", 0) + 1
    out += ["", f"## Minor findings and leads ({len(minor)} listed in sweep.json)", ""]
    out += [f"- `{k}`: {v}" for k, v in sorted(by_rule.items(), key=lambda kv: -kv[1])]
    out += ["", "## What this sweep does not establish", ""] + [f"- {x}" for x in rec["does_not_establish"]]
    return "\n".join(out) + "\n"


def render_svg(rec: dict[str, Any]) -> str:
    cols = [*SEVERITIES, "not_covered"]
    colors = {"blocker": "#b3261e", "major": "#e8710a", "minor": "#f2c94c", "info": "#9aa0a6",
              "not_covered": "#5f8dd3"}
    beats = list(rec["counts"]["by_beat"].items())
    top = max([sum(c.values()) for _, c in beats] + [1])
    width, row_h, left = 860, 34, 300
    scale = (width - left - 120) / top
    height = 90 + row_h * max(len(beats), 1) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'font-family="Helvetica, Arial, sans-serif" font-size="13">',
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
           f'<text x="16" y="28" font-size="16" font-weight="bold">Sheriff sweep {html.escape(rec["case"])}: '
           f'findings and leads by beat</text>',
           f'<text x="16" y="48" fill="#444">target {html.escape(rec["target"])}; canary '
           f'{"passed" if rec["canary"]["passed"] else "FAILED"}; counts include leads beyond the listing cap</text>']
    for k, (beat, c) in enumerate(beats):
        y = 70 + k * row_h
        out.append(f'<text x="16" y="{y + 20}">{html.escape(beat + " " + BEATS.get(beat, ""))}</text>')
        x = left
        for col in cols:
            n = c.get(col, 0)
            if n:
                w = max(n * scale, 2)
                out.append(f'<rect x="{x:.1f}" y="{y + 6}" width="{w:.1f}" height="20" fill="{colors[col]}">'
                           f'<title>{beat} {col}: {n}</title></rect>')
                x += w
        out.append(f'<text x="{x + 6:.1f}" y="{y + 20}" fill="#333">{sum(c.values())}</text>')
    ly = 70 + row_h * max(len(beats), 1) + 14
    for k, col in enumerate(cols):
        out.append(f'<rect x="{16 + k * 150}" y="{ly}" width="14" height="14" fill="{colors[col]}"/>'
                   f'<text x="{36 + k * 150}" y="{ly + 12}">{col}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Canary: the instrument's positive control
# ---------------------------------------------------------------------------

CANARY_FILES = {
    "lean/Proj/lakefile.toml": 'name = "Proj"\n',
    "lean/Proj/lean-toolchain": "leanprover/lean4:v4.34.1\n",
    "lean/Proj/Proj/Bad.lean": (
        "/- nested /- sorry -/ still a comment: sorry -/\n"
        "-- sorry in a line comment is not a hole\n"
        'def msg : String := "sorry, not a hole"\n'
        "def hole : Nat := sorry\n"
        "def q : Char := '\"'\n"
        "def nm := ``Lean.ofReduceBool\n"
        "axiom cheat : 1 = 2\n"
        "theorem big : 2 ^ 64 > 1 := by native_decide\n"
        "theorem vac (n : Nat) (h : n < 0) : True := trivial\n"
        "#exit\n"
        "theorem hidden : False := by simp\n"),
    "lean/Clean/lakefile.toml": 'name = "Clean"\n',
    "lean/Clean/lean-toolchain": "leanprover/lean4:v4.34.1\n",
    "lean/Clean/Clean/Good.lean": "/-- `sorry`-free. -/\ntheorem ok : 1 + 1 = 2 := rfl\n#print axioms ok\n",
    "loose/Loose.lean": "theorem t : 2 = 2 := rfl\n",
    "src/zk/stark.rs": (
        "pub fn verify(proof: &Proof, air: &Air) -> bool {\n"
        "    for (pos, val) in proof.openings.iter() {\n"
        "        // we trust the trace via FRI\n"
        "        let _ = val;\n"
        "    }\n"
        "    true\n"
        "}\n"
        "#[cfg(test)]\nmod tests {\n    #[test]\n    fn honest_proof_verifies() { assert!(true); }\n}\n"),
    "src/zk/good.rs": (
        "pub fn verify(proof: &Proof) -> bool {\n"
        "    let _ = log_line(\"verify\");\n"
        "    proof.value == expected(proof.position)\n"
        "}\n"
        "#[cfg(test)]\nmod tests {\n    #[test]\n    fn rejects_tampered_proof() { assert!(true); }\n}\n"),
    "runs/r1/receipt.json": '{"verified": true, "dev_mode": true}\n',
    "runs/r2/receipt.json": '{"verified": true, "dev_mode": false}\n',
    "README.md": "All counts are execution verified by a STARK proof.\nThe Heegner-Stark numbers are 1 and 2.\n",
    "papers/p/main.tex": ("We measure a speedup of 3.217 and solve 12{,}345 targets in 2024 % 9.876 is commented\n"
                          "on a \\includegraphics[width=0.75\\textwidth]{fig1.pdf} figure.\n"
                          "Data: \\texttt{artifact/results\\_all.json}.\n"),
    "papers/q/main.tex": "A ratio of 4.567, with no data cited.\n",
    "papers/r/main.tex": ("Primes $\\{19,37,79,109\\}$ and a ratio of 3.217 from \\texttt{../../elsewhere/other.json}.\n"
                          "\\begin{thebibliography}{9}\\bibitem{x} J. Doe, vol. 4321, 2001.\\end{thebibliography}\n"),
    "papers/p/fig.txt": "",
    "artifact/results_all.json": '{"targets": 12345}\n',
    "elsewhere/other.json": '{"ratio": 3.217, "primes": [19, 37, 79, 109]}\n',
    ".github/workflows/lean.yml": "jobs: {build: {steps: [{run: cd lean/Clean && lake build}]}}\n",
}
CANARY_EXPECT = {
    ("lean.sorry", "lean/Proj/Proj/Bad.lean", 4), ("lean.axiom", "lean/Proj/Proj/Bad.lean", 7),
    ("lean.native_decide", "lean/Proj/Proj/Bad.lean", 8), ("lean.vacuous", "lean/Proj/Proj/Bad.lean", 9),
    ("lean.exit", "lean/Proj/Proj/Bad.lean", 10), ("lean.no_axiom_audit", "lean/Proj", None),
    ("lean.no_ci", "lean/Proj", None), ("lean.unpinned", "loose/Loose.lean", None),
    ("zk.discarded_value", "src/zk/stark.rs", 4), ("zk.trust_comment", "src/zk/stark.rs", 3),
    ("zk.no_negative_test", "src/zk/stark.rs", None), ("zk.dev_mode_receipt", "runs/r1/receipt.json", 1),
    ("zk.proof_language", "README.md", 1), ("paper.untraced_number", "papers/p/main.tex", 1),
    ("paper.no_cited_artifacts", "papers/q", None),
}
# (rule, path, line or None): any hit here is a false positive.
CANARY_FORBID = {
    ("lean.sorry", "lean/Proj/Proj/Bad.lean", 1), ("lean.sorry", "lean/Proj/Proj/Bad.lean", 2),
    ("lean.sorry", "lean/Proj/Proj/Bad.lean", 3), ("lean.sorry", "lean/Clean/Clean/Good.lean", None),
    ("lean.native_decide", "lean/Proj/Proj/Bad.lean", 6),
    ("lean.no_axiom_audit", "lean/Clean", None), ("lean.no_ci", "lean/Clean", None),
    ("zk.discarded_value", "src/zk/good.rs", None), ("zk.no_negative_test", "src/zk/good.rs", None),
    ("zk.dev_mode_receipt", "runs/r2/receipt.json", None), ("zk.proof_language", "README.md", 2),
    ("paper.no_cited_artifacts", "papers/p", None), ("paper.no_cited_artifacts", "papers/r", None),
    ("paper.untraced_number", "papers/r/main.tex", None),
}
CANARY_UNTRACED = {"3.217"}
CANARY_TRACED = {"12345"}


def canary() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="sheriff-canary-") as tmp:
        root = Path(tmp)
        for rel, text in CANARY_FILES.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text)
        quiet = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        env = {**os.environ, **quiet}
        for argv in (["init", "-q"], ["add", "-A"]):
            subprocess.run(["git", "-C", tmp, *argv], check=True, env=env, capture_output=True)
        rows, summary = scan_repo("canary", root, [], {"canary": root})
    hits = {(r["rule"], r["path"], r["line"]) for r in rows}
    loose = {(r, p) for r, p, _ in hits}
    caught = sorted(e for e in CANARY_EXPECT if (e in hits if e[2] else (e[0], e[1]) in loose))
    missed = sorted(set(CANARY_EXPECT) - set(caught), key=str)
    fps = sorted(f for f in CANARY_FORBID if (f in hits if f[2] else (f[0], f[1]) in loose))
    sorry_lines = [r for r in rows if r["rule"] == "lean.sorry"]
    if len(sorry_lines) != 1:
        fps.append(("lean.sorry", "count", len(sorry_lines)))
    untraced = {r["excerpt"] for r in rows if r["rule"] == "paper.untraced_number"}
    for value in CANARY_UNTRACED - untraced:
        missed.append(("paper.untraced_number", value, None))
    for value in CANARY_TRACED & untraced:
        fps.append(("paper.untraced_number", value, None))
    numbers = {v for v, _ in tex_numbers(CANARY_FILES["papers/p/main.tex"])}
    numbers |= {v for v, _ in tex_numbers(CANARY_FILES["papers/r/main.tex"])}
    for bogus in ("2024", "9.876", "0.75", "79109", "4321"):
        if bogus in numbers:
            fps.append(("paper.number_extracted", bogus, None))
    return {"passed": not missed and not fps, "caught": [list(x) for x in caught],
            "missed": [list(x) for x in missed], "false_positives": [list(x) for x in fps]}


# ---------------------------------------------------------------------------
# check-case: the reader pass may not uphold what it did not check
# ---------------------------------------------------------------------------

def resolve_evidence(item: str, repos: dict[str, Path]) -> Path | None:
    name, sep, rest = item.partition(":")
    if sep and name in repos:
        root, rel = repos[name], rest
    else:
        root, rel = REPO, item
    rel = rel.split("#")[0].rstrip("/")
    if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        return None
    path = root / re.sub(r":\d+(-\d+)?$", "", rel)
    return path if path.exists() else None


def check_case(case: Path, repos: dict[str, Path]) -> list[str]:
    errors: list[str] = []
    sweep_path, findings_path = case / "sweep.json", case / "findings.yaml"
    if not sweep_path.is_file():
        return [f"{sweep_path}: missing (run tools/sheriff.py sweep first)"]
    if not findings_path.is_file():
        return [f"{findings_path}: missing (the reader pass writes it)"]
    sweep_rec = json.loads(sweep_path.read_text())
    doc = yaml.safe_load(findings_path.read_text()) or {}
    body = doc.get("sheriff_case")
    if not isinstance(body, dict):
        return ["findings.yaml: top-level key `sheriff_case` missing"]
    if body.get("schema") != CASE_SCHEMA:
        errors.append(f"schema must be {CASE_SCHEMA}")
    if body.get("id") != case.name:
        errors.append(f"id {body.get('id')!r} does not match directory {case.name}")
    canary_ok = bool(sweep_rec.get("canary", {}).get("passed"))
    finds = {f.get("id"): f for f in body.get("findings") or [] if isinstance(f, dict)}
    for fid, f in finds.items():
        if f.get("severity") not in SEVERITIES[:3]:
            errors.append(f"finding {fid}: severity must be one of {SEVERITIES[:3]}")
        if f.get("beat") not in BEATS and f.get("beat") not in ("B1", "B9"):
            errors.append(f"finding {fid}: unknown beat {f.get('beat')!r}")
        for key in ("what", "fix"):
            if not f.get(key):
                errors.append(f"finding {fid}: `{key}` is required (what is wrong, what would make it right)")
    claims = body.get("claims") or []
    if not claims:
        errors.append("no claims: a case audits at least one stated claim (B1)")
    if not body.get("readers"):
        errors.append("readers: name each independent reader, its model and the joint it owned (B9)")
    for c in claims:
        cid = c.get("id", "?")
        verdict = c.get("verdict")
        if verdict not in VERDICTS:
            errors.append(f"claim {cid}: verdict {verdict!r} not in {VERDICTS}")
            continue
        if not c.get("text") or not c.get("location"):
            errors.append(f"claim {cid}: `text` and `location` are required")
        beats = c.get("beats") or {}
        bad = {b: s for b, s in beats.items() if s not in BEAT_STATES}
        if bad:
            errors.append(f"claim {cid}: beat states {bad} not in {BEAT_STATES}")
        linked = [finds.get(x) for x in c.get("findings") or []]
        if None in linked:
            errors.append(f"claim {cid}: cites a finding id that is not defined")
        upheld = verdict in ("upheld", "upheld_scoped")
        if upheld:
            if not canary_ok:
                errors.append(f"claim {cid}: cannot be upheld; the sweep's canary did not pass")
            if any(s == "fail" for s in beats.values()):
                errors.append(f"claim {cid}: a failed beat forbids {verdict}")
            if any(f and f.get("severity") == "blocker" for f in linked):
                errors.append(f"claim {cid}: a linked blocker forbids {verdict}")
            evidence = c.get("evidence") or []
            if not any(resolve_evidence(str(e), repos) for e in evidence):
                errors.append(f"claim {cid}: {verdict} needs at least one evidence path that exists")
            missing = [str(e) for e in evidence if ":" in str(e) or "/" in str(e)
                       if resolve_evidence(str(e), repos) is None]
            if missing:
                errors.append(f"claim {cid}: evidence paths not found: {missing}")
            if not beats:
                errors.append(f"claim {cid}: {verdict} needs a state for every applicable beat")
        if verdict == "upheld" and any(s == "not_covered" for s in beats.values()):
            errors.append(f"claim {cid}: a not_covered beat is never a pass; use upheld_scoped and say what is uncovered")
        if verdict in ("upheld_scoped", "overclaimed") and not c.get("scoped_to"):
            errors.append(f"claim {cid}: {verdict} needs `scoped_to`, the statement the evidence does support")
        if verdict in ("overclaimed", "unsupported", "broken") and not linked:
            errors.append(f"claim {cid}: {verdict} needs at least one linked finding")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("sweep", help="deterministic sweep; writes a new case directory")
    s.add_argument("--target", default="all", help="all | EXP-* | RUN-* | path | repo:path")
    s.add_argument("--deep", action="store_true", help="also run slow and toolchain-dependent checkers")
    s.add_argument("--repo", action="append", default=[], metavar="NAME=PATH")
    s.add_argument("--no-siblings", action="store_true")
    s.add_argument("--no-checkers", action="store_true")
    s.add_argument("--out", help=f"case directory (default: {CASE_ROOT}/SHF-<date>-<hex>)")
    c = sub.add_parser("canary", help="positive control: plant defects, require each to be caught")
    c.add_argument("--json", action="store_true")
    k = sub.add_parser("check-case", help="validate a case's findings.yaml against its sweep")
    k.add_argument("case")
    k.add_argument("--repo", action="append", default=[], metavar="NAME=PATH")
    args = parser.parse_args(argv)
    if args.command == "sweep":
        return sweep(args)
    if args.command == "canary":
        result = canary()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"canary {'passed' if result['passed'] else 'FAILED'}: {len(result['caught'])} caught, "
                  f"missed {result['missed']}, false positives {result['false_positives']}")
        return 0 if result["passed"] else 1
    errors = check_case(Path(args.case).resolve(), discover(args.repo))
    for e in errors:
        print(f"ERROR: {e}")
    print("case ok" if not errors else f"{len(errors)} error(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
