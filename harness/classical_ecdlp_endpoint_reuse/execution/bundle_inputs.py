#!/usr/bin/env python3
"""Package already sealed public inputs locally; never upload or draw inputs."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cohort.public_inputs import load_inputs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--public-root", required=True, type=Path)
    p.add_argument("--inputs-manifest-sha256", required=True)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    cohort = load_inputs(a.public_root, a.inputs_manifest_sha256)
    if a.out.exists() or a.out.with_suffix(a.out.suffix + ".json").exists():
        p.error("fresh bundle and receipt paths required")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|") as tar:
                for path in sorted(a.public_root.rglob("*")):
                    if not path.is_file() or path.is_symlink():
                        if path.is_symlink():
                            raise ValueError("public symlinks are forbidden")
                        continue
                    data = path.read_bytes()
                    info = tarfile.TarInfo("public/" + path.relative_to(a.public_root).as_posix())
                    info.size, info.mtime, info.mode = len(data), 0, 0o644
                    info.uid, info.gid, info.uname, info.gname = 0, 0, "", ""
                    tar.addfile(info, io.BytesIO(data))
    record = {"schema": "classical.ecdlp.endpoint-reuse.public-bundle/v1",
              "local_path": str(a.out.resolve()), "bytes": a.out.stat().st_size,
              "sha256": hashlib.sha256(a.out.read_bytes()).hexdigest(),
              "inputs_manifest_sha256": a.inputs_manifest_sha256,
              "protocol_sha256": cohort.protocol_sha256, "nonce_hex": cohort.nonce_hex,
              "uploaded": False, "s3_uri": None, "s3_version_id": None,
              "private_input_files_included": False}
    a.out.with_suffix(a.out.suffix + ".json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
