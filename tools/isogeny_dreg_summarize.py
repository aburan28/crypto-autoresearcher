#!/usr/bin/env python3
"""Turn full isogeny-dreg-search run outputs into compact committed summaries.

A full run JSON carries one row per class member (up to ~5.5e5 rows at
p ~ 2^40).  The committed artifact keeps everything except the member table
and records the table's SHA-256 and row count, so a reader can re-run the
seed and verify they reproduced the same table without the repository
carrying megabytes of rows.  A separate members file (from
`--checkpoint-dir`) is hashed the same way when present.

    python3 tools/isogeny_dreg_summarize.py runs/*.json --outdir analysis/isogeny-dreg-search/runs
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def summarize(path: Path, outdir: Path, members_file: Path | None = None) -> Path:
    with open(path) as fh:
        rep = json.load(fh)
    members = rep.pop("members", None)
    if members is None and members_file and members_file.exists():
        with open(members_file) as fh:
            members = json.load(fh)
    if members is not None:
        blob = json.dumps(members, sort_keys=True, separators=(",", ":")).encode()
        rep["members_table"] = {
            "rows": len(members),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "columns": sorted({k for m in members[:1] for k in m}),
            "kept_in_repository": False,
            "regenerate": ("python3 tools/isogeny_dreg_search_fast.py --p {p} --a {a} --b {b} --seed {seed} "
                           "--samples {samples} --nulls {nulls} --k {k} --h {h} --checkpoint-dir <dir> "
                           "--members-limit 0 --out <file>").format(**{**rep["input"], "p": rep["class"]["p"]}),
        }
        rep.pop("members_omitted", None)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / path.name
    with open(out, "w") as fh:
        json.dump(rep, fh, indent=1)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--outdir", default="analysis/isogeny-dreg-search/runs")
    ap.add_argument("--members-dir", help="directory holding members-<bits>-<seed>.json files")
    args = ap.parse_args(argv)
    for p in args.paths:
        p = Path(p)
        mf = None
        if args.members_dir:
            # ladder-<bits>bit-seed<seed>.json  ->  members-<bits>-<seed>.json
            stem = p.stem
            if stem.startswith("ladder-") and "bit-seed" in stem:
                bits = stem[len("ladder-"):stem.index("bit")]
                seed = stem[stem.index("seed") + 4:]
                mf = Path(args.members_dir) / f"members-{int(bits)}-{seed}.json"
        out = summarize(p, Path(args.outdir), mf)
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
