#!/usr/bin/env python3
"""Rebuild machine-readable inventory of both autolab research ledgers (fresh 2026-07-18 copies)."""
import json, re, hashlib
from pathlib import Path

IN = Path("/Volumes/Volume/crypto-autoresearcher/inputs")
FILES = {
    "autolab_research_ledger": IN / "research_ledger_main.md",
    "ecdlp_ic_research_ledger": IN / "research_ledger_ic.md",
}
ID_RE = re.compile(r"^([A-Z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)+)\s*$")

MECH_RULES = [
    ("semaev-summation", r"semaev|summation polynomial|summation-polynomial"),
    ("grobner-solver", r"groebner|gröbner|macaulay|f4|f5|minors? model"),
    ("sat-solver", r"\bSAT\b|sat[- ]based|crossbred"),
    ("resultant", r"resultant"),
    ("first-fall-degree", r"first fall|fall degree|ffd"),
    ("weil-descent", r"weil (descent|restriction)|weil-restrict"),
    ("ghs-cover", r"\bGHS\b|cover attack"),
    ("isogeny-volcano", r"volcano|ascending isogeny|horizontal isogen"),
    ("isogeny-transfer", r"isogen(?:y|ous) (transfer|class|neighbor|deck)"),
    ("cm-endomorphism", r"\bCM\b|complex multiplication|endomorphism ring|frobenius endomorphism"),
    ("self-pairing-torsion", r"self-pairing"),
    ("pairing-transfer", r"pairing|MOV|frey-rueck|frey-rück|tate"),
    ("kani-interpolation", r"kani|interpolation reconstruct"),
    ("prym", r"prym"),
    ("kummer-theta", r"kummer|theta"),
    ("jacobian-transfer", r"jacobian"),
    ("bielliptic-cover", r"bielliptic|genus-2|genus-two|genus 2"),
    ("trielliptic", r"trielliptic|degree-3 map|cofiber"),
    ("cyclic-cover-norm", r"cyclic cover|norm smooth|z\^d"),
    ("trace-zero", r"trace-zero|trace zero|ker\(Tr"),
    ("hessian-kummer-cover", r"hesse"),
    ("functional-graph-ecfg", r"\bECFG\b|functional graph|evans"),
    ("rho-baseline", r"pollard|rho\b"),
    ("bsgs", r"\bBSGS\b|baby-step"),
    ("wagner-k-list", r"wagner|k-list|generalized birthday"),
    ("large-prime", r"large[- ]prime|\bLP\b"),
    ("krylov-linear-algebra", r"krylov|lanczos|wiedemann|block-krylov|sparse (linear|solve)"),
    ("factor-base-structure", r"factor base|factor-base"),
    ("relation-surface", r"relation surface|relation-surface|relation generation surface"),
    ("selector-scheduling", r"selector|schedul|routing|leaf"),
    ("character-bucket", r"character (bucket|residual)|division.character|quotient character"),
    ("tensor-rank", r"tensor|border.rank|flattening rank"),
    ("jet-divided-power", r"\bjet\b|divided.power|dual number|hasse"),
    ("tropical-bkk", r"tropical|newton poly|mixed volume|\bBKK\b|bernshtein"),
    ("transfer-operator-spectral", r"koopman|ruelle|transfer operator|spectral"),
    ("path-algebra", r"path algebra|quiver|noncommutative"),
    ("matchgate-spinor", r"matchgate|spinor|clifford|pfaffian"),
    ("toric-cremona", r"toric|cremona"),
    ("eds-elliptic-net", r"elliptic divisibility|\bEDS\b|elliptic net|somos"),
    ("miller-unit", r"miller"),
    ("height-lift", r"height.compress|global lift|canonical height"),
    ("incidence-geometry", r"incidence|plucker|plücker|secant"),
    ("displacement-rank", r"displacement.rank|toeplitz|low.displacement"),
    ("galois-deck", r"deck (orbit|transformation)|galois (cover|group|closure)"),
    ("modular-curve", r"modular (curve|form|polynomial)|lattes|lattès"),
    ("lang-torsor", r"lang (map|torsor|algebra|quotient)|artinn?-schreier"),
    ("adams-transform", r"adams"),
    ("torsion-field", r"torsion field|torsion basis|E\[\d"),
    ("point-counting", r"schoof|SEA\b|point.count"),
    ("anomalous", r"anomalous|smart|satoh-araki|sssa"),
    ("pohlig-hellman", r"pohlig"),
    ("twist-invalid-curve", r"twist|invalid.curve"),
    ("index-calculus-generic", r"index calculus|index-calculus"),
    ("linear-algebra-rank", r"\brank\b|nullity|kernel"),
    ("meet-in-middle", r"meet.in.the.middle|\bMITM\b"),
    ("hash-collision", r"collision|hash"),
    ("graph-feature-ml", r"feature|classifier|machine learning|\bML\b|graph feature"),
    ("divisor-decomposition", r"divisor|cantor|mumford"),
    ("gluing-abelian", r"gluing|weil factor|howe"),
    ("rosati-hom-lattice", r"rosati|hom.lattice|hom saturation"),
    ("sigma-function", r"sigma function|p-adic sigma"),
    ("edwards-model", r"edwards"),
    ("montgomery-ladder", r"montgomery"),
    ("differential-state", r"differential state|x\(A-B\)"),
    ("preprocessing-table", r"preprocess|precomput|amortiz|advice"),
    ("correspondence", r"correspondence"),
    ("fiber-product", r"fiber product|fibre product"),
    ("resolvent-symmetric", r"resolvent|symmetric (trace|function)"),
]

def classify(text):
    t = text.lower()
    tags = [name for name, rx in MECH_RULES if re.search(rx, t)]
    return tags if tags else ["misc-relation-surface"]

def split_cells(line):
    # split a markdown table row, respecting that content may contain escaped pipes
    s = line.strip()
    if s.startswith("|"): s = s[1:]
    if s.endswith("|"): s = s[:-1]
    return [c.strip() for c in s.split("|")]

entries = []
for source, path in FILES.items():
    section = None
    ofq_counter = 0
    prefix = "OFQ-autolab" if "main" in path.name else "OFQ-ic"
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^##\s+(.*)", raw)
        if m:
            section = m.group(1).strip()
            continue
        line = raw.rstrip("\n")
        if section and section.lower().startswith("open frontier"):
            mm = re.match(r"^- \[( |x)\]\s+(.*)", line)
            if mm:
                ofq_counter += 1
                done = mm.group(1) == "x"
                text = mm.group(2).strip()
                entries.append({
                    "id": f"{prefix}-{ofq_counter:02d}",
                    "source_ledger": source, "section": "Open frontier questions",
                    "date": None, "title": text[:120],
                    "mechanism": ";".join(classify(text)),
                    "representation": None, "exploited_structure": None,
                    "factor_base": None, "relation_shape": None,
                    "relation_generation": None, "compression": None,
                    "linear_algebra": None, "descent": None, "cost_bottleneck": None,
                    "outcome": "answered-closed" if done else "open-question",
                    "negative_boundary": None, "next_branch": None,
                    "full_text": text,
                })
            continue
        if line.startswith("|"):
            cells = split_cells(line)
            if len(cells) < 2: continue
            first = cells[0].replace("`", "").strip()
            if first in ("ID", "") or set(first) <= set("-: "): continue
            # first cell may hold multiple ids
            idcand = first.split(",")[0].split("/")[0].strip()
            if not ID_RE.match(idcand): continue
            body = " | ".join(c for c in cells[1:] if c)
            status = None
            for c in cells[1:]:
                cu = c.strip().upper().replace("`","")
                if cu in ("NEGATIVE RESULT","OPEN","OBSERVATION","HYPOTHESIS","RESTRICTED THEOREM","CONJECTURE","POSITIVE SIGNAL","SUPPORTED","REJECTED","INCONCLUSIVE","SUPERSEDED","WEAKENED","THEOREM","HEURISTIC"):
                    status = cu; break
            if status is None and "negative" in section.lower(): status = "NEGATIVE RESULT"
            if status is None and "positive" in section.lower(): status = "POSITIVE SIGNAL"
            entries.append({
                "id": first, "source_ledger": source, "section": section,
                "date": None, "title": cells[1][:160] if len(cells) > 1 else "",
                "mechanism": ";".join(classify(body + " " + first)),
                "representation": None, "exploited_structure": None,
                "factor_base": None, "relation_shape": None,
                "relation_generation": None, "compression": None,
                "linear_algebra": None, "descent": None, "cost_bottleneck": None,
                "outcome": status,
                "negative_boundary": cells[1][:300] if "negative" in (section or "").lower() else None,
                "next_branch": cells[-1][:300] if len(cells) > 3 else None,
                "full_text": body[:2000],
            })

out = IN / "ledger_inventory_20260718.json"
out.write_text(json.dumps(entries, indent=1))
print(f"total entries: {len(entries)}")

from collections import Counter
fam = Counter()
for e in entries:
    base = re.match(r"^([A-Za-z]+)", e["id"])
    fam[(e["source_ledger"], base.group(1) if base else "?")] += 1
for k, v in sorted(fam.items()):
    print(k, v)

# diff vs old inventory
old = json.loads((IN / "ledger_inventory.json").read_text())
old_ids = {e["id"] for e in old}
new_ids = {e["id"] for e in entries}
added = [e for e in entries if e["id"] not in old_ids]
print(f"\nold inventory: {len(old_ids)} ids; new: {len(new_ids)}; added: {len(added)}; removed: {len(old_ids - new_ids)}")
added_path = IN / "ledger_added_20260718.json"
added_path.write_text(json.dumps(added, indent=1))
print("added entries written to", added_path)
