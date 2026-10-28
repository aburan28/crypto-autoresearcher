"""Extract and compare the exact unsuppressed errors from two hosted ledger jobs.

Usage: python3 generate.py OLD_JOB_LOG NEW_JOB_LOG
The logs are downloaded from the two job URLs in REPORT.md. No ledger record
or validator input is modified by this script.
"""

from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import sys


JOBS = [
    {
        "job": 122604839789,
        "head": "64da2f50560c3565c36880fc86b0aad8addeb223",
        "url": "https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40624063556/job/122604839789",
    },
    {
        "job": 122616982776,
        "head": "a94a304f1e76d81e4a9899e8bcb709b8fdb0e21c",
        "url": "https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40627808095/job/122616982776",
    },
]
LINE = re.compile(r"^.*?Z\s+-\s+((?:ledger/|experiments/)[^\n]+)$")


def read_log(path: Path) -> tuple[list[str], str]:
    raw = path.read_bytes()
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", raw.decode("utf-8"))
    lines = [m.group(1) for line in text.splitlines() if (m := LINE.match(line))]
    assert "FAIL: 65 new validation error(s)" in text, path
    assert len(lines) == 65 and len(set(lines)) == 65, path
    return sorted(lines), sha256(raw).hexdigest()


def kind(path: str) -> str:
    if path.startswith("ledger/proposals/"):
        return "proposal prior art"
    if path.startswith("ledger/handoffs/"):
        return "handoff review plan"
    if path.endswith("/specification.yaml"):
        return "experiment schema"
    return "run manifest schema"


def main() -> None:
    assert len(sys.argv) == 3
    old, old_digest = read_log(Path(sys.argv[1]))
    new, new_digest = read_log(Path(sys.argv[2]))
    assert old == new, "CI error sets differ; inspect before publishing"
    errors = []
    for line in new:
        path, message = line.split(": ", 1)
        errors.append({"path": path, "category": kind(path), "message": message})
    counts = Counter(x["category"] for x in errors)
    paths = Counter(x["path"] for x in errors)
    result = {
        "schema": "ledger-validation-observation/v1",
        "observation_utc": "2026-10-28T03:47:00Z",
        "base_main_sha": "7b16f392d39c00e558bdaf44a35063303cd550ab",
        "jobs": [{**job, "downloaded_log_sha256": digest} for job, digest in zip(JOBS, (old_digest, new_digest))],
        "normalized_error_set_sha256": sha256("\n".join(new).encode()).hexdigest(),
        "unsuppressed_errors": len(errors),
        "affected_paths": len(paths),
        "category_counts": dict(sorted(counts.items())),
        "path_counts": dict(sorted(paths.items())),
        "added_vs_prior_job": [],
        "removed_vs_prior_job": [],
        "errors": errors,
    }
    directory = Path(__file__).parent
    (directory / "errors.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    labels = ["Handoff review plan", "Run manifest schema", "Proposal prior art", "Experiment schema"]
    values = [counts["handoff review plan"], counts["run manifest schema"], counts["proposal prior art"], counts["experiment schema"]]
    colors = ["#a23a4a", "#315f9e", "#a7781f", "#5b7484"]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="460" viewBox="0 0 1000 460" role="img" aria-label="65 unsuppressed ledger errors by record category">',
           '<rect width="1000" height="460" fill="#fff"/>',
           '<text x="48" y="50" font-family="sans-serif" font-size="25" font-weight="bold">Current full-ledger validation failures</text>',
           '<text x="48" y="79" font-family="sans-serif" font-size="15" fill="#555">Two hosted jobs, 2026-10-28 · 65 unsuppressed errors · 22 paths</text>']
    for i, (label, value, color) in enumerate(zip(labels, values, colors)):
        y = 125 + i * 76
        svg.extend([f'<text x="48" y="{y + 22}" font-family="sans-serif" font-size="17">{escape(label)}</text>',
                    f'<rect x="275" y="{y}" width="{value * 19}" height="35" fill="{color}"/>',
                    f'<text x="{290 + value * 19}" y="{y + 24}" font-family="sans-serif" font-size="18" font-weight="bold">{value}</text>'])
    svg += ['<text x="48" y="435" font-family="sans-serif" font-size="13" fill="#555">Source: ledger jobs 122604839789 and 122616982776; counts are validator messages, not false-result counts.</text>', '</svg>']
    (directory / "categories.svg").write_text("\n".join(svg) + "\n")


if __name__ == "__main__":
    main()
