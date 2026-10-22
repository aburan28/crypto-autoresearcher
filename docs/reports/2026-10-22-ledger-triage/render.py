"""Verify the exact ledger-gate delta and draw its error-class counts."""

from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "2026-10-21-ledger-integrity-audit/evidence/validate-ledger.log"
NEW = HERE / "evidence/validate-ledger.log"
EXPECTED_REMOVED = {
    "experiments/EXP-ECDLP-daee4d/specification.yaml: missing required field 'success_criterion'",
    "experiments/EXP-ECDLP-daee4d/specification.yaml: approved experiment has null 'success_criterion'",
    "experiments/EXP-ECDLP-daee4d/specification.yaml: approved experiment has null 'falsification_criterion'",
    "experiments/EXP-ECDLP-daee4d/specification.yaml: missing 'decision_impact' (on_positive/on_negative): say before the run what each outcome changes",
    "ledger/evidence/EV-QSP-2c78d3.yaml: evidence references unknown run 'RUN-QSP-715b58'",
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


def draw(before, after):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="480" viewBox="0 0 820 480">',
             '<rect width="820" height="480" fill="#fff"/>',
             '<text x="22" y="31" font-family="sans-serif" font-size="20" font-weight="bold">Ledger validation messages by class</text>',
             '<text x="22" y="54" font-family="sans-serif" font-size="12" fill="#555">Initial audit: 162; source-corrected branch: 157. Bars count messages, not scientific results.</text>',
             '<rect x="563" y="73" width="15" height="10" fill="#a6adb4"/><text x="584" y="83" font-family="sans-serif" font-size="12">initial</text>',
             '<rect x="653" y="73" width="15" height="10" fill="#087e8b"/><text x="674" y="83" font-family="sans-serif" font-size="12">corrected</text>']
    for i, name in enumerate(CATEGORIES):
        y = 107 + 50*i
        a, b = before[name], after[name]
        parts += [f'<text x="22" y="{y+16}" font-family="sans-serif" font-size="12">{name}</text>',
                  f'<rect x="265" y="{y}" width="{a*6}" height="12" fill="#a6adb4"/>',
                  f'<rect x="265" y="{y+15}" width="{b*6}" height="12" fill="#087e8b"/>',
                  f'<text x="{272+a*6}" y="{y+11}" font-family="sans-serif" font-size="11">{a}</text>',
                  f'<text x="{272+b*6}" y="{y+26}" font-family="sans-serif" font-size="11">{b}</text>']
    parts += ['<text x="22" y="469" font-family="sans-serif" font-size="11" fill="#555">Five missing files for the zero-compute hand derivation remain reported.</text>',
              '</svg>']
    (HERE / "error-delta.svg").write_text("\n".join(parts) + "\n")


def main():
    old_raw, new_raw = OLD.read_bytes(), NEW.read_bytes()
    old_lines, new_lines = old_raw.decode().splitlines(), new_raw.decode().splitlines()
    old, new = errors(old_raw), errors(new_raw)
    assert old_lines[0] == "FAIL: 162 new validation error(s):"
    assert new_lines[0] == "FAIL: 157 new validation error(s):"
    assert len(old) == 162 and len(new) == 157
    assert set(old) - set(new) == EXPECTED_REMOVED
    assert not set(new) - set(old)
    assert len({e.split(": ", 1)[0] for e in old}) == 49
    assert len({e.split(": ", 1)[0] for e in new}) == 47
    before, after = Counter(map(category, old)), Counter(map(category, new))
    assert sum(before.values()) == 162 and sum(after.values()) == 157
    result = {"status": "pass", "initial_log_sha256": digest(old_raw),
              "corrected_log_sha256": digest(new_raw),
              "initial_errors": 162, "corrected_errors": 157,
              "initial_affected_paths": 49, "corrected_affected_paths": 47,
              "removed_errors": sorted(EXPECTED_REMOVED), "added_errors": [],
              "categories": {name: {"initial": before[name], "corrected": after[name]}
                             for name in CATEGORIES},
              "initial_advisory_summary": old_lines[-1],
              "corrected_advisory_summary": new_lines[-1]}
    (HERE / "counts.json").write_text(json.dumps(result, indent=2) + "\n")
    draw(before, after)
    print(json.dumps({"status": "pass", "initial": 162, "corrected": 157,
                      "removed": 5, "added": 0, "paths": 47}))


if __name__ == "__main__":
    main()
