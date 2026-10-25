"""Independently verify one exact-point Pollard-rho receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from matched_rho import rho_module, sha


def check(input_path: Path, manifest_path: Path, result_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    result = json.loads(result_path.read_text())
    if (result.get("schema") != "ectd.graph-matched-rho-result/v1" or
            result.get("input_sha256") != sha(input_path) or
            result.get("prepared_manifest_sha256") != sha(manifest_path) or
            any(result.get(key) != manifest.get(key)
                for key in ("p", "a", "b", "r", "generator", "Q"))):
        raise ValueError("rho receipt is not bound to this prepared curve point")
    if result.get("status") == "censored_step_cap":
        if result.get("scalar") is not None or result.get("verified") is not False:
            raise ValueError("rho cap receipt carries an unverified scalar")
        return {"status": "valid_censored", "steps": result.get("steps"),
                "group_ops": result.get("group_ops")}
    if result.get("status") != "verified_scalar" or result.get("verified") is not True:
        raise ValueError("rho result has an invalid terminal state")
    module = rho_module()
    scalar = result.get("scalar")
    if (not isinstance(scalar, int) or
            not module.independent_verify_discrete_log(
                scalar, tuple(manifest["generator"]), tuple(manifest["Q"]),
                manifest["a"], manifest["p"])):
        raise ValueError("independent rho scalar equation failed")
    return {"status": "valid_verified_scalar", "scalar": scalar,
            "steps": result["steps"], "group_ops": result["group_ops"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.input, args.manifest, args.result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
