#!/usr/bin/env python3
"""Build a machine-readable inventory of every ledger ID in both copied ledgers.

Inputs (copied into workspace on 2026-07-19):
  inputs/main_research_ledger.md        (autolab/research_ledger.md, 2026-07-18 19:35)
  inputs/index_calculus_research_ledger.md (ecdlp_index_calculus_state/research_ledger.md)

Output:
  inputs/ledger_inventory_20260719.json  -- one record per ledger ID with the 13
    required extraction fields filled by rule-based classification over the full
    entry text, plus section/outcome/family tallies printed to stdout.
"""
import json
import re
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INP = ROOT / "inputs"

LEDGERS = [
    ("autolab_main", INP / "main_research_ledger.md"),
    ("ecdlp_index_calculus", INP / "index_calculus_research_ledger.md"),
]

ID_RE = re.compile(
    r"^\s*\|?\s*`?((?:ECFG|TRANSFER|ISO|OFQ|SHA1?|NR|RT|PO|BAR|MODHECKE|DRINFELD|RITT|ISOWALK|ZILBERPINK|PADICHT|AMORT)[A-Za-z0-9_.\-]*\d[A-Za-z0-9_.\-]*|P\d{3,4}|S\d+)`?\s*\|"
)

FIELD_LEXICON = {
    "representation": [
        "x-line", "x-only", "kummer", "theta", "jacobian", "weil restriction",
        "weil-restriction", "twist", "isogeny class", "volcano", "functional graph",
        "ecfg", "tensor", "resultant", "eliminant", "ideal", "orientation",
        "prym", "cover", "correspondence", "divisor", "picard", "abelian surface",
        "galois representation", "trace-zero", "subfield", "lattes", "lattès",
        "montgomery", "edwards", "hessian", "jacobi", "supersingular", "ordinary",
    ],
    "exploited_structure": [
        "negation", "frobenius", "cm", "endomorphism", "torsion", "2-torsion",
        "symmetry", "symmetrized", "automorphism", "galois", "trace", "norm",
        "subgroup", "smooth", "volcano", "orientation", "self-pairing", "pairing",
        "isogeny", "deformation", "lift", "kernel", "isotropic", "polarization",
        "cycle", "component", "sparsity", "low-weight", "birthday", "spectral",
    ],
    "factor_base": [
        "factor base", "factor-base", "x-coordinate", "slice", "rational points",
        "large prime", "large-prime", "two-large-prime", "divisor class",
        "degree-1", "degree-2", "fb ", "columns", "row bank", "row-bank",
    ],
    "relation_shape": [
        "summation", "m-sum", "3-sum", "4-sum", "5-sum", "two-large-prime",
        "2lp", "cofiber", "ternary", "incidence", "pencil", "tuple",
        "weight-2", "weight-3", "linear relation", "dependency", "kernel row",
    ],
    "relation_generation": [
        "semaev", "summation polynomial", "grobner", "gröbner", "sat", "resultant",
        "interpolation", "evaluation", "elimination", "solving degree",
        "first fall", "crossbred", "xl", "f4", "f5", "wu", "boolean",
        "point decomposition", "harvesting", "walk", "sampler", "hit stream",
        "membership",
    ],
    "compression": [
        "symmetriz", "negation", "shared", "reuse", "row bank", "compression",
        "compressed", "cycle-basis", "homology", "matroid", "batch", "amortiz",
        "selector", "fingerprint", "landmark", "depth-limited", "prefix",
    ],
    "linear_algebra": [
        "sparse", "dense", "krylov", "wiedemann", "lanczos", "block wiedemann",
        "rank", "echelon", "nullspace", "null space", "matrix", "smith",
        "hermite", "lll", "groebner-free", "structured gaussian",
    ],
    "descent": [
        "descent", "individual log", "target descent", "blind descent",
        "target-first", "target coupling", "target-coupled", "recovery",
        "reconstruction", "meet-in-the-middle", "mitm",
    ],
    "cost_bottleneck": [
        "bottleneck", "floor", "x rho", "exponent", "sqrt(n)", "memory",
        "wall-clock", "charged", "oracle floor", "setup", "preprocessing",
        "advice", "offline", "online", "amortiz",
    ],
}

OUTCOME_LEXICON = [
    ("NEGATIVE RESULT", "negative-result"),
    ("POSITIVE SIGNAL", "positive-signal"),
    ("RESTRICTED THEOREM", "restricted-theorem"),
    ("OBSERVATION", "observation"),
    ("HYPOTHESIS", "hypothesis"),
    ("CONJECTURE", "conjecture"),
    ("PREREGISTERED", "preregistered"),
    ("OPEN", "open"),
    ("NEGATIVE CONTROL", "negative-control"),
    ("MODEL-BOUND", "model-bound"),
    ("TOY-EVIDENCE", "toy-evidence"),
    ("ANSWERED", "answered-closed"),
]

NEG_BOUNDARY_RE = re.compile(
    r"(does not close[^.|]{0,180}|closes only[^.|]{0,180}|no recovery[^.|]{0,120}|"
    r"not evidence against[^.|]{0,120}|scoped[^.|]{0,160})", re.I)


def classify(text, key):
    low = text.lower()
    hits = sorted({t for t in FIELD_LEXICON[key] if t in low})
    return ";".join(hits) if hits else None


def outcome_of(text):
    found = []
    up = text.upper()
    for pat, tag in OUTCOME_LEXICON:
        if pat in up:
            found.append(tag)
    return ";".join(dict.fromkeys(found)) if found else None


def family_of(entry_id):
    m = re.match(r"([A-Za-z]+)", entry_id)
    if m:
        return m.group(1).upper()
    m = re.match(r"(P|S)(\d+)", entry_id)
    if m:
        return m.group(1)
    return entry_id[:6]


def parse_ledger(source, path):
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    section = "preamble"
    entries = []
    ofq_counter = 0
    for line in lines:
        h = re.match(r"^##\s+(.*)", line)
        if h:
            section = h.group(1).strip()
            continue
        m = ID_RE.match(line)
        if m and "|" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            eid = cells[0].strip("` ")
            entries.append({
                "id": eid,
                "source_ledger": source,
                "section": section,
                "title": cells[1][:220] if len(cells) > 1 else "",
                "status_cell": cells[2][:400] if len(cells) > 2 else "",
                "next_branch": cells[-1][:400] if len(cells) > 3 else "",
                "full_text": " | ".join(cells[1:]),
            })
            continue
        if section.lower().startswith("open frontier") and re.match(r"^- \[[ xX]\]", line):
            ofq_counter += 1
            body = re.sub(r"^- \[[ xX]\]\s*", "", line).strip()
            m2 = re.match(r"\*\*([A-Za-z0-9_.\-/ ]+)\*\*\s*[:(]?(.*)", body)
            if m2:
                eid = m2.group(1).strip()
                rest = m2.group(2)
            else:
                eid = f"OFQ-{source}-{ofq_counter:02d}"
                rest = body
            done = line.startswith("- [x]") or line.startswith("- [X]")
            entries.append({
                "id": eid,
                "source_ledger": source,
                "section": section,
                "title": rest[:220],
                "status_cell": "answered-closed" if done else "open-question",
                "next_branch": "",
                "full_text": rest,
            })
    return entries


def main():
    all_entries = []
    for source, path in LEDGERS:
        all_entries.extend(parse_ledger(source, path))

    seen = collections.Counter()
    for e in all_entries:
        seen[e["id"]] += 1
        e["family"] = family_of(e["id"])
        e["mechanism"] = classify(e["full_text"], "exploited_structure")
        for key in ["representation", "factor_base", "relation_shape",
                    "relation_generation", "compression", "linear_algebra",
                    "descent", "cost_bottleneck"]:
            e[key] = classify(e["full_text"], key)
        e["exploited_structure"] = e.pop("mechanism")
        e["mechanism"] = ";".join(
            sorted({w for w in re.split(r"[;|,/()]", e["title"].lower())
                    if 4 < len(w.strip()) < 40 and " " not in w.strip()[:6]}))[:200] or None
        e["outcome"] = outcome_of(e["full_text"]) or (
            "open-question" if e["status_cell"] == "open-question" else
            "answered-closed" if e["status_cell"] == "answered-closed" else None)
        nb = NEG_BOUNDARY_RE.search(e["full_text"])
        e["negative_boundary"] = nb.group(0).strip() if nb else None
        e["next_branch"] = e["next_branch"] or None
        e["duplicate_id_occurrence"] = seen[e["id"]]

    out = INP / "ledger_inventory_20260719.json"
    out.write_text(json.dumps(all_entries, indent=1))

    fam = collections.Counter(e["family"] for e in all_entries)
    sec = collections.Counter((e["source_ledger"], e["section"]) for e in all_entries)
    oc = collections.Counter((e["outcome"] or "unclassified") for e in all_entries)
    print(f"total entries: {len(all_entries)}")
    print(f"unique ids: {len(set(e['id'] for e in all_entries))}")
    print("families:", dict(fam.most_common(30)))
    print("sections:")
    for (src, s), n in sorted(sec.items()):
        print(f"  [{src}] {s}: {n}")
    print("outcomes:", dict(oc.most_common(20)))
    dup = {k: v for k, v in seen.items() if v > 1}
    print(f"ids appearing >1 time: {len(dup)}")

    # delta vs 2026-07-18 inventory
    old_path = INP / "ledger_inventory_20260718.json"
    if old_path.exists():
        old = {e["id"] for e in json.loads(old_path.read_text())}
        new = [e["id"] for e in all_entries if e["id"] not in old]
        print(f"ids not in 2026-07-18 inventory: {len(new)}")
        print("new ids:", new[:80])


if __name__ == "__main__":
    main()
