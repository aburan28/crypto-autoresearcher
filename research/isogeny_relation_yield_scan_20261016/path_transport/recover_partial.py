"""Preserve an interrupted edge checkpoint before resuming a verified chain.

Invoke only after the producer process has stopped. The completed chain is
replayed first; the partial file is hard-linked to a new archive name and then
removed from the producer's fixed temporary path. No content is overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets

from verify_chain import WALKS, verify

PARTIAL = re.compile(r"edge-(\d{4})\.json\.partial\Z")


def recover(stratum: str, directory: Path) -> dict:
    result = verify(stratum, directory)
    last = result["edges_checked"]
    partials = sorted(directory.glob("edge-????.json.partial"))
    if not partials:
        return {"status": "no_partial", "stratum": stratum, "verified_edges": last}
    if len(partials) != 1:
        raise ValueError("expected at most one interrupted checkpoint")
    partial = partials[0]
    match = PARTIAL.fullmatch(partial.name)
    if match is None or partial.is_symlink() or not partial.is_file():
        raise ValueError("unexpected partial checkpoint path")
    index = int(match.group(1))
    if index not in (last, last + 1):
        raise ValueError("partial index is not the completed or next edge")
    if index == last and not (directory / f"edge-{index:04d}.json").exists():
        raise ValueError("completed-edge partial has no committed checkpoint")
    raw = partial.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    archive = directory / f"{partial.name}.preserved-{secrets.token_hex(6)}"
    archive.hardlink_to(partial)
    if archive.read_bytes() != raw:
        raise ValueError("partial changed while preserving it")
    partial.unlink()
    return {"status": "partial_preserved", "stratum": stratum,
            "verified_edges": last, "interrupted_index": index,
            "partial_sha256": digest, "preserved_path": str(archive)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stratum", choices=sorted(WALKS), required=True)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(recover(args.stratum, args.checkpoint_dir), sort_keys=True))
