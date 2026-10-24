"""Verify the exact five-line ledger delta and draw the remaining errors."""

from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BEFORE = HERE.parent / "2026-10-22-ledger-triage/evidence/validate-ledger-citation.log"
AFTER = HERE / "evidence/validate-ledger.log"
RUN = "experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/manifest_v2.yaml"
CAPTURES = ("command.txt", "environment.json", "stdout.log", "stderr.log",
            "raw-result.json")
REMOVED = {f"{RUN}: run directory missing artifact '{name}'" for name in CAPTURES}
CATEGORIES = ("Prior-art metadata", "Review/handoff fields", "Citation provenance",
              "Run-manifest schema", "Broken references", "Zero-compute stage artifacts",
              "Experiment-spec fields")


def errors(raw):
    return [line[4:] for line in raw.decode().splitlines()
            if line.startswith("  - ")]


def category(line):
    if "prior_art" in line:
        return CATEGORIES[0]
    if "citations[" in line:
        return CATEGORIES[2]
    if "review_plan" in line or line.startswith("ledger/handoffs/"):
        return CATEGORIES[1]
    if "run directory missing artifact" in line:
        return CATEGORIES[5]
    if "unknown record" in line or "unknown run" in line or "unknown target" in line:
        return CATEGORIES[4]
    if line.startswith("experiments/") and "/runs/" in line:
        return CATEGORIES[3]
    if line.startswith("experiments/") and "/specification.yaml:" in line:
        return CATEGORIES[6]
    raise ValueError(f"unclassified error: {line}")


def draw(before, after):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="485" viewBox="0 0 760 485">',
        '<rect width="760" height="485" fill="#fff"/>',
        '<text x="22" y="32" font-family="sans-serif" font-size="20" font-weight="bold">Ledger validation messages by class</text>',
        '<text x="22" y="55" font-family="sans-serif" font-size="12" fill="#555">147 before; 142 after source-bound non-execution classification. Counts are not scientific results.</text>',
        '<rect x="265" y="70" width="14" height="10" fill="#a6adb4"/><text x="284" y="80" font-family="sans-serif" font-size="12">before</text>',
        '<rect x="355" y="70" width="14" height="10" fill="#087e8b"/><text x="374" y="80" font-family="sans-serif" font-size="12">after</text>',
    ]
    for i, name in enumerate(CATEGORIES):
        y = 96 + 52 * i
        a, b = before[name], after[name]
        parts.extend((
            f'<text x="22" y="{y+20}" font-family="sans-serif" font-size="12">{name}</text>',
            f'<rect x="265" y="{y}" width="{a*6}" height="14" fill="#a6adb4"/>',
            f'<rect x="265" y="{y+18}" width="{b*6}" height="14" fill="#087e8b"/>',
            f'<text x="{272+a*6}" y="{y+12}" font-family="sans-serif" font-size="11">{a}</text>',
            f'<text x="{272+b*6}" y="{y+30}" font-family="sans-serif" font-size="11">{b}</text>',
        ))
    parts.extend((
        '<text x="22" y="476" font-family="sans-serif" font-size="11" fill="#555">The validator still exits 1; no measurement or proof was added.</text>',
        '</svg>',
    ))
    (HERE / "error-delta.svg").write_text("\n".join(parts) + "\n")


def main():
    old_raw, new_raw = BEFORE.read_bytes(), AFTER.read_bytes()
    old, new = errors(old_raw), errors(new_raw)
    assert old_raw.decode().splitlines()[0] == "FAIL: 147 new validation error(s):"
    assert new_raw.decode().splitlines()[0] == "FAIL: 142 new validation error(s):"
    assert len(old) == 147 and len(new) == 142
    assert Counter(old) - Counter(new) == Counter(REMOVED)
    assert not Counter(new) - Counter(old)
    assert len({x.split(": ", 1)[0] for x in old}) == 41
    assert len({x.split(": ", 1)[0] for x in new}) == 40
    before, after = Counter(map(category, old)), Counter(map(category, new))
    result = {
        "status": "pass", "before_errors": 147, "after_errors": 142,
        "before_affected_paths": 41, "after_affected_paths": 40,
        "before_log_sha256": hashlib.sha256(old_raw).hexdigest(),
        "after_log_sha256": hashlib.sha256(new_raw).hexdigest(),
        "removed_errors": sorted(REMOVED), "added_errors": [],
        "categories": {name: {"before": before[name], "after": after[name]}
                       for name in CATEGORIES},
        "before_advisory_summary": old_raw.decode().splitlines()[-1],
        "after_advisory_summary": new_raw.decode().splitlines()[-1],
    }
    (HERE / "counts.json").write_text(json.dumps(result, indent=2) + "\n")
    draw(before, after)
    print(json.dumps({"status": "pass", "removed": 5, "added": 0, "remaining": 142}))


if __name__ == "__main__":
    main()
