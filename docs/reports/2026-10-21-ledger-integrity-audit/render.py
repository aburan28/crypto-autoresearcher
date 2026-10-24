"""Count the full-ledger validator errors and render the evidence figure/PDF.

The chart counts validator lines, not independent scientific findings. The
validator log is an immutable input to this report; this script never edits it.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

from reportlab import rl_config
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


ROOT = Path(__file__).resolve().parent
LOG = ROOT / "evidence" / "validate-ledger.log"
SOURCE_COMMIT = "e20013ae20d2c09019d8ea1b2fed7556c61ad4ba"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def category(line: str) -> str:
    if "prior_art" in line:
        return "Prior-art metadata"
    if "citations[" in line:
        return "Citation provenance"
    if "review_plan" in line or line.startswith("ledger/handoffs/"):
        return "Review/handoff fields"
    if "run directory missing artifact" in line:
        return "Zero-compute stage artifacts"
    if "unknown record" in line or "unknown run" in line or "unknown target" in line:
        return "Broken references"
    if line.startswith("experiments/") and "/runs/" in line:
        return "Run-manifest schema"
    if line.startswith("experiments/") and "/specification.yaml:" in line:
        return "Experiment-spec fields"
    raise ValueError(f"unclassified validator error: {line}")


def escape(value: str) -> str:
    return (value.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def main() -> None:
    raw = LOG.read_bytes()
    lines = raw.decode("utf-8").splitlines()
    errors = [line[4:] for line in lines if line.startswith("  - ")]
    require(bool(lines) and lines[0] == "FAIL: 162 new validation error(s):",
            "unexpected validator summary")
    require(len(errors) == 162, f"expected 162 validator error lines, got {len(errors)}")
    counts = Counter(category(error) for error in errors)
    paths = {error.split(": ", 1)[0] for error in errors}
    require(len(paths) == 49, f"expected 49 affected paths, got {len(paths)}")
    ordered = [
        "Prior-art metadata", "Review/handoff fields", "Citation provenance",
        "Run-manifest schema", "Broken references",
        "Zero-compute stage artifacts", "Experiment-spec fields",
    ]
    require(sum(counts.values()) == 162, "classification did not cover every error")
    summary = {
        "schema": "crypto.autoresearch.ledger_audit_summary.v1",
        "source_commit": SOURCE_COMMIT,
        "validator_log_sha256": hashlib.sha256(raw).hexdigest(),
        "status": "fail",
        "new_error_lines": len(errors),
        "affected_paths": len(paths),
        "grandfathered_legacy_errors": 1210,
        "advisories": 543,
        "categories": [{"name": name, "count": counts[name]} for name in ordered],
    }
    (ROOT / "counts.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    colors = ["#9b3d45", "#bd643b", "#be873c", "#5d80ad", "#8256a7", "#5e997b", "#76859a"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="555" viewBox="0 0 1100 555" role="img" aria-labelledby="title desc">',
        '<title id="title">Full ledger validation errors by category</title>',
        '<desc id="desc">The full validator found 162 unsuppressed error lines in 49 records. The bars show the exact count in each category; 1,210 grandfathered errors and 543 advisories are separate.</desc>',
        '<rect width="1100" height="555" fill="#f8fafc"/>',
        '<text x="35" y="45" font-family="Arial,sans-serif" font-size="25" font-weight="700" fill="#172338">Full ledger gate: 162 unsuppressed errors</text>',
        '<text x="35" y="75" font-family="Arial,sans-serif" font-size="16" fill="#46566c">49 affected records; audited main e20013ae; 2026-10-21</text>',
    ]
    for i, name in enumerate(ordered):
        y = 112 + i * 51
        width = counts[name] * 10
        parts.extend([
            f'<text x="35" y="{y + 25}" font-family="Arial,sans-serif" font-size="17" fill="#172338">{escape(name)}</text>',
            f'<rect x="325" y="{y}" width="{width}" height="34" rx="5" fill="{colors[i]}"/>',
            f'<text x="{335 + width}" y="{y + 25}" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#172338">{counts[name]}</text>',
        ])
    parts.extend([
        '<line x1="325" y1="476" x2="1000" y2="476" stroke="#6a7d91" stroke-width="1"/>',
        '<text x="35" y="510" font-family="Arial,sans-serif" font-size="15" fill="#46566c">Counts are validator messages, not a count of false research conclusions.</text>',
        '<text x="35" y="535" font-family="Arial,sans-serif" font-size="15" fill="#46566c">1,210 grandfathered errors and 543 advisories are outside the seven bars.</text>',
        '</svg>',
    ])
    (ROOT / "error-categories.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    rl_config.invariant = 1
    renderPDF.drawToFile(svg2rlg(str(ROOT / "error-categories.svg")),
                         str(ROOT / "error-categories.pdf"))
    subprocess.run(["tectonic", "report.tex", "--outdir", "."], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
