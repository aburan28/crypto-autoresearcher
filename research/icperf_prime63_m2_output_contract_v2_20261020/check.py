#!/usr/bin/env python3
"""Independent structural checker for no-science canned output fixtures."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import output_contract
def main():
    p=argparse.ArgumentParser(); p.add_argument("--run-dir",type=Path,required=True); a=p.parse_args()
    output_contract.verify_outputs(a.run_dir)
    raw=json.loads((a.run_dir/"raw-result.json").read_text())
    if raw.get("attack_claimed") is not False or raw.get("verification_status") != "pending_independent_checker": raise output_contract.ContractError("false successful response")
if __name__ == "__main__": main()
