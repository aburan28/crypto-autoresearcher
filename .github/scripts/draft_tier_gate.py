#!/usr/bin/env python3
"""Put PR workflows behind the draft tier gate (docs/ci-tiers.md).

A draft PR runs only the fast tier. Every other workflow that a
`pull_request` event can start must:

  * list `ready_for_review` in its `pull_request` types, so marking the PR
    ready starts the full tier on the current head, and
  * gate every job on `!github.event.pull_request.draft`, so a push to a
    draft starts no runner. Non-PR events have no `pull_request` payload and
    are unaffected.

`--check` (the default) fails on any workflow that is neither gated, fast
tier, nor byte-pinned. `--apply` edits the YAML text in place, keeping every
other byte, and verifies that each edited file still parses to the original
structure plus only those two changes.
"""
from __future__ import annotations

import argparse
import copy
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
GATE = "!github.event.pull_request.draft"
READY = "ready_for_review"
DEFAULT_TYPES = ["opened", "synchronize", "reopened"]

# Cheap checks every draft push still gets.
FAST_TIER = {
    "progress-fidelity.yml",
    "ci-tier.yml",
}
# Workflows whose exact bytes are pinned by a sealed evidence record (none
# here on 2026-10-23); editing them would break that record.
PINNED: set[str] = set()


def load(text: str) -> dict:
    return yaml.load(text, Loader=yaml.BaseLoader) or {}


def triggers(doc: dict) -> dict:
    on = doc.get("on", {})
    if isinstance(on, str):
        return {on: None}
    if isinstance(on, list):
        return {k: None for k in on}
    return on or {}


def pr_types(doc: dict) -> list[str] | None:
    """The workflow's pull_request types, or None if it has no PR trigger."""
    on = triggers(doc)
    if "pull_request" not in on:
        return None
    pr = on["pull_request"]
    if isinstance(pr, dict) and "types" in pr:
        t = pr["types"]
        return [t] if isinstance(t, str) else list(t)
    return list(DEFAULT_TYPES)


def wants_ready(types: list[str]) -> bool:
    """Only workflows that run on pushes need to re-run when marked ready."""
    return bool({"opened", "synchronize"} & set(types))


def gated(doc: dict) -> bool:
    types = pr_types(doc)
    if types is None:
        return True
    jobs = doc.get("jobs") or {}
    return (READY in types or not wants_ready(types)) and all(GATE in str(j.get("if", "")) for j in jobs.values())


# ------------------------------------------------------------------ editing

def _block_end(lines: list[str], start: int, indent: int) -> int:
    """Index after the block that begins below lines[start] (deeper indent)."""
    i = start + 1
    while i < len(lines):
        s = lines[i]
        if s.strip() and not s.lstrip().startswith("#"):
            if len(s) - len(s.lstrip()) <= indent:
                break
        i += 1
    return i


def add_ready_type(text: str) -> str:
    lines = text.split("\n")
    on_idx = next((i for i, l in enumerate(lines)
                   if re.match(r"^(on|\"on\"|'on'):\s*(#.*)?$", l)), None)
    if on_idx is None:
        m = next(((i, l) for i, l in enumerate(lines) if re.match(r"^on:\s*\[", l)), None)
        if m and "pull_request" in m[1]:
            raise ValueError("flow-sequence `on:` list; edit by hand")
        raise ValueError("no block `on:` mapping")
    end = _block_end(lines, on_idx, 0)
    pr_idx = next((i for i in range(on_idx + 1, end)
                   if re.match(r"^\s+pull_request:\s*(#.*)?$", lines[i])
                   or re.match(r"^\s+pull_request:\s*(\{\}|null|~)?\s*$", lines[i])), None)
    if pr_idx is None:
        raise ValueError("pull_request trigger is not a block mapping")
    pr_line = lines[pr_idx]
    ind = len(pr_line) - len(pr_line.lstrip())
    pr_end = _block_end(lines, pr_idx, ind)
    child = None
    for i in range(pr_idx + 1, pr_end):
        if lines[i].strip() and not lines[i].lstrip().startswith("#"):
            child = len(lines[i]) - len(lines[i].lstrip())
            break
    child = child or ind + 2
    t_idx = next((i for i in range(pr_idx + 1, pr_end)
                  if re.match(rf"^\s{{{child}}}types:", lines[i])), None)
    if t_idx is None:
        new = f"{' ' * child}types: [{', '.join(DEFAULT_TYPES + [READY])}]"
        head = re.sub(r":\s*(\{\}|null|~)\s*$", ":", pr_line)
        return "\n".join(lines[:pr_idx] + [head, new] + lines[pr_idx + 1:])
    line = lines[t_idx]
    m = re.match(r"^(\s*types:\s*)\[(.*)\](\s*(#.*)?)$", line)
    if m:
        items = [x.strip() for x in m.group(2).split(",") if x.strip()]
        lines[t_idx] = f"{m.group(1)}[{', '.join(items + [READY])}]{m.group(3)}"
        return "\n".join(lines)
    m = re.match(r"^(\s*types:\s*)([A-Za-z_]+)\s*$", line)
    if m:
        lines[t_idx] = f"{m.group(1)}[{m.group(2)}, {READY}]"
        return "\n".join(lines)
    t_end = _block_end(lines, t_idx, child)
    items = [i for i in range(t_idx + 1, t_end) if lines[i].strip().startswith("- ")]
    if not items:
        raise ValueError("unrecognised pull_request types")
    last = items[-1]
    dash = lines[last][: len(lines[last]) - len(lines[last].lstrip())]
    return "\n".join(lines[: last + 1] + [f"{dash}- {READY}"] + lines[last + 1:])


def _strip_expr(expr: str) -> str:
    e = expr.strip()
    m = re.fullmatch(r"\$\{\{(.*)\}\}", e, re.S)
    return (m.group(1) if m else e).strip()


def gate_jobs(text: str) -> str:
    lines = text.split("\n")
    jobs_idx = next((i for i, l in enumerate(lines) if re.match(r"^jobs:\s*(#.*)?$", l)), None)
    if jobs_idx is None:
        raise ValueError("no block `jobs:` mapping")
    end = _block_end(lines, jobs_idx, 0)
    job_ind = None
    for i in range(jobs_idx + 1, end):
        if lines[i].strip() and not lines[i].lstrip().startswith("#"):
            job_ind = len(lines[i]) - len(lines[i].lstrip())
            break
    if job_ind is None:
        raise ValueError("empty jobs")
    starts = [i for i in range(jobs_idx + 1, end)
              if re.match(rf"^\s{{{job_ind}}}[^\s#][^:]*:\s*(#.*)?$", lines[i])]
    out = lines[: jobs_idx + 1]
    bounds = starts + [end]
    out += lines[jobs_idx + 1: starts[0]] if starts else []
    for a, b in zip(starts, bounds[1:]):
        block = lines[a:b]
        key_ind = None
        for l in block[1:]:
            if l.strip() and not l.lstrip().startswith("#"):
                key_ind = len(l) - len(l.lstrip())
                break
        key_ind = key_ind or job_ind + 2
        pad = " " * key_ind
        if_i = next((k for k in range(1, len(block))
                     if re.match(rf"^\s{{{key_ind}}}if:", block[k])), None)
        if if_i is None:
            block = [block[0], f"{pad}if: ${{{{ {GATE} }}}}"] + block[1:]
        else:
            rest = block[if_i].split("if:", 1)[1].strip()
            if rest in (">", ">-", "|", "|-", ">+", "|+"):
                k_end = if_i + 1
                while k_end < len(block) and (not block[k_end].strip() or
                                              len(block[k_end]) - len(block[k_end].lstrip()) > key_ind):
                    k_end += 1
                body = [l.strip() for l in block[if_i + 1:k_end] if l.strip()]
                expr = _strip_expr(" ".join(body) if rest.startswith(">") else "\n".join(body))
                span = (if_i, k_end)
            else:
                if re.search(r"\s#", rest) and not rest.startswith(("'", '"')):
                    rest = re.split(r"\s+#", rest, 1)[0]
                if rest.startswith(("'", '"')):
                    rest = yaml.safe_load(rest)
                expr = _strip_expr(rest)
                span = (if_i, if_i + 1)
            new = [f"{pad}if: >-", f"{pad}  {GATE} &&", f"{pad}  ({expr})"] \
                if "\n" not in expr else \
                [f"{pad}if: |-", f"{pad}  {GATE} && (",
                 *[f"{pad}  {l}" for l in expr.split("\n")], f"{pad}  )"]
            block = block[:span[0]] + new + block[span[1]:]
        out += block
    out += lines[end:]
    return "\n".join(out)


def expected(doc: dict) -> dict:
    exp = copy.deepcopy(doc)
    on = exp.get("on")
    pr = on["pull_request"] if isinstance(on, dict) else None
    if not isinstance(pr, dict):
        pr = {}
        on["pull_request"] = pr
    types = pr.get("types")
    types = [types] if isinstance(types, str) else list(types or DEFAULT_TYPES)
    if wants_ready(types) and READY not in types:
        pr["types"] = types + [READY]
    for job in (exp.get("jobs") or {}).values():
        old = job.get("if")
        job["if"] = f"${{{{ {GATE} }}}}" if old is None else f"{GATE} && ({_strip_expr(old)})"
    return exp


def norm(doc):
    """Compare `if` expressions modulo whitespace."""
    if isinstance(doc, dict):
        return {k: (re.sub(r"\s+", " ", v).strip() if k == "if" and isinstance(v, str) else norm(v))
                for k, v in doc.items()}
    if isinstance(doc, list):
        return [norm(v) for v in doc]
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    missing, failed, changed = [], [], []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        name = path.name
        text = path.read_text()
        doc = load(text)
        if name in FAST_TIER or name in PINNED or gated(doc):
            continue
        if not args.apply:
            missing.append(name)
            continue
        try:
            types = pr_types(doc)
            if wants_ready(types) and READY not in types:
                text = add_ready_type(text)
            new = gate_jobs(text)
            if norm(load(new)) != norm(expected(doc)):
                raise ValueError("edited workflow does not parse to the expected structure")
        except (ValueError, yaml.YAMLError) as exc:
            failed.append(f"{name}: {exc}")
            continue
        path.write_text(new)
        changed.append(name)
    if args.apply:
        print(f"gated {len(changed)} workflows")
        for f in failed:
            print(f"NOT GATED {f}")
        return 1 if failed else 0
    for m in missing:
        print(f"::error file=.github/workflows/{m}::PR workflow is not draft-gated; "
              "run python3 .github/scripts/draft_tier_gate.py --apply or add it to FAST_TIER")
    print(f"{len(missing)} PR workflows outside the draft tier gate")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
