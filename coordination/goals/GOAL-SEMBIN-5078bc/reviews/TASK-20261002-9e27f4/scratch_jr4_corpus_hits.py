"""SCRATCH (TASK-20261002-9e27f4, validator). Read-only corpus search for JR-4.

The kb MCP `search_knowledge` tool was not in this session's tool surface, so the
card's fallback (grep) is used. This regenerates the hit table the JR-4
classification in validation_report.yaml was made from: every file under
knowledge/ matching any of the card's five terms, with the terms it matches, a
characteristic-2 marker, and its title. Classification itself is in the report.

Usage (from the repository root):
    python3 coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261002-9e27f4/scratch_jr4_corpus_hits.py \
        > coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261002-9e27f4/scratch_jr4_corpus_hits_output.tsv
"""
import os
import re
import sys

TERMS = {"filter": r"filter", "solvdeg": r"solving[ -]degree", "firstfall": r"first[ -]fall",
         "member": r"membership", "canon": r"canonicali"}
C2 = r"characteristic[- ]?(2|two)|binary|F_\{?2\^|F_2\b|GF\(2"


def title_of(text):
    m = re.search(r"^title:\s*(>-\s*\n)?(.*?)(\n[a-z_]+:|\Z)", text, re.S | re.M)
    t = re.sub(r"\s+", " ", m.group(2)).strip() if m else ""
    if not t:
        m = re.search(r"^#\s+(.*)$", text, re.M)
        t = m.group(1) if m else ""
    return t[:160]


def main(root="knowledge"):
    rows = []
    for dp, _, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                t = open(p, errors="replace").read()
            except OSError:
                continue
            hits = [k for k, v in TERMS.items() if re.search(v, t, re.I)]
            if hits:
                rows.append((p, ",".join(hits), "c2" if re.search(C2, t, re.I) else "", title_of(t)))
    rows.sort()
    print("path\tterms\tchar2\ttitle")
    for r in rows:
        print("\t".join(r))
    print(f"# {len(rows)} files", file=sys.stderr)


if __name__ == "__main__":
    main()
