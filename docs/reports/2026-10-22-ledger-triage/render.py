"""Verify the exact ledger-gate delta and draw its error-class counts."""

from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "2026-10-21-ledger-integrity-audit/evidence/validate-ledger.log"
MID = HERE / "evidence/validate-ledger.log"
NEW = HERE / "evidence/validate-ledger-merged.log"
EXPECTED_REMOVED = {
    "experiments/EXP-ECDLP-daee4d/specification.yaml: missing required field 'success_criterion'",
    "experiments/EXP-ECDLP-daee4d/specification.yaml: approved experiment has null 'success_criterion'",
    "experiments/EXP-ECDLP-daee4d/specification.yaml: approved experiment has null 'falsification_criterion'",
    "experiments/EXP-ECDLP-daee4d/specification.yaml: missing 'decision_impact' (on_positive/on_negative): say before the run what each outcome changes",
    "ledger/evidence/EV-QSP-2c78d3.yaml: evidence references unknown run 'RUN-QSP-715b58'",
}
EXPECTED_MAIN_REMOVED = {
    "ledger/decisions/DEC-20260929-21bb51.yaml: decision references unknown target 'EXP-AUXIN-bafa2e'",
    "ledger/decisions/DEC-20260929-4eade7.yaml: decision references unknown target 'EXP-AUXIN-369078'",
    "ledger/decisions/DEC-20260929-7efa82.yaml: decision references unknown target 'EXP-AUXIN-bafa2e'",
    "ledger/decisions/DEC-20260929-93fc4d.yaml: decision references unknown target 'EXP-AUXIN-55c6c0'",
    "ledger/decisions/DEC-20260929-cfb294.yaml: decision references unknown target 'EXP-AUXIN-92dccc'",
}
CATEGORIES = ["Prior-art metadata", "Review/handoff fields",
              "Citation provenance", "Run-manifest schema",
              "Broken references", "Zero-compute stage artifacts",
              "Experiment-spec fields"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


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


def draw(before, middle, after):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="530" viewBox="0 0 820 530">',
             '<rect width="820" height="530" fill="#fff"/>',
             '<text x="22" y="31" font-family="sans-serif" font-size="20" font-weight="bold">Ledger validation messages by class</text>',
             '<text x="22" y="54" font-family="sans-serif" font-size="12" fill="#555">162 initial; 157 after two source corrections; 152 after merging main. Messages, not scientific results.</text>',
             '<rect x="420" y="73" width="15" height="10" fill="#a6adb4"/><text x="440" y="83" font-family="sans-serif" font-size="12">initial</text>',
             '<rect x="510" y="73" width="15" height="10" fill="#087e8b"/><text x="530" y="83" font-family="sans-serif" font-size="12">source corrections</text>',
             '<rect x="663" y="73" width="15" height="10" fill="#b45f22"/><text x="683" y="83" font-family="sans-serif" font-size="12">merged head</text>']
    for i, name in enumerate(CATEGORIES):
        y = 106 + 56*i
        a, b, c = before[name], middle[name], after[name]
        parts += [f'<text x="22" y="{y+22}" font-family="sans-serif" font-size="12">{name}</text>',
                  f'<rect x="265" y="{y}" width="{a*6}" height="12" fill="#a6adb4"/>',
                  f'<rect x="265" y="{y+15}" width="{b*6}" height="12" fill="#087e8b"/>',
                  f'<rect x="265" y="{y+30}" width="{c*6}" height="12" fill="#b45f22"/>',
                  f'<text x="{272+a*6}" y="{y+11}" font-family="sans-serif" font-size="11">{a}</text>',
                  f'<text x="{272+b*6}" y="{y+26}" font-family="sans-serif" font-size="11">{b}</text>',
                  f'<text x="{272+c*6}" y="{y+41}" font-family="sans-serif" font-size="11">{c}</text>']
    parts += ['<text x="22" y="518" font-family="sans-serif" font-size="11" fill="#555">Five missing files for the zero-compute hand derivation remain reported.</text>',
              '</svg>']
    (HERE / "error-delta.svg").write_text("\n".join(parts) + "\n")


def main():
    old_raw, mid_raw, new_raw = OLD.read_bytes(), MID.read_bytes(), NEW.read_bytes()
    old_lines, mid_lines, new_lines = [raw.decode().splitlines()
                                        for raw in (old_raw, mid_raw, new_raw)]
    old, mid, new = [errors(raw) for raw in (old_raw, mid_raw, new_raw)]
    assert old_lines[0] == "FAIL: 162 new validation error(s):"
    assert mid_lines[0] == "FAIL: 157 new validation error(s):"
    assert new_lines[0] == "FAIL: 152 new validation error(s):"
    assert len(old) == 162 and len(mid) == 157 and len(new) == 152
    assert Counter(old) - Counter(mid) == Counter(EXPECTED_REMOVED)
    assert not Counter(mid) - Counter(old)
    assert Counter(mid) - Counter(new) == Counter(EXPECTED_MAIN_REMOVED)
    assert not Counter(new) - Counter(mid)
    assert len({e.split(": ", 1)[0] for e in old}) == 49
    assert len({e.split(": ", 1)[0] for e in mid}) == 47
    assert len({e.split(": ", 1)[0] for e in new}) == 42
    before, middle, after = [Counter(map(category, lines))
                             for lines in (old, mid, new)]
    assert sum(before.values()) == 162 and sum(middle.values()) == 157
    assert sum(after.values()) == 152
    result = {"status": "pass", "initial_log_sha256": digest(old_raw),
              "source_corrected_log_sha256": digest(mid_raw),
              "merged_log_sha256": digest(new_raw),
              "initial_errors": 162, "source_corrected_errors": 157,
              "merged_errors": 152,
              "initial_affected_paths": 49, "source_corrected_affected_paths": 47,
              "merged_affected_paths": 42,
              "source_correction_removed_errors": sorted(EXPECTED_REMOVED),
              "main_merge_removed_errors": sorted(EXPECTED_MAIN_REMOVED),
              "added_errors": [],
              "categories": {name: {"initial": before[name],
                                   "source_corrected": middle[name],
                                   "merged": after[name]}
                             for name in CATEGORIES},
              "initial_advisory_summary": old_lines[-1],
              "source_corrected_advisory_summary": mid_lines[-1],
              "merged_advisory_summary": new_lines[-1]}
    (HERE / "counts.json").write_text(json.dumps(result, indent=2) + "\n")
    draw(before, middle, after)
    print(json.dumps({"status": "pass", "initial": 162, "source_corrected": 157,
                      "merged": 152, "removed": 10, "added": 0, "paths": 42}))


if __name__ == "__main__":
    main()
