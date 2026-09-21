#!/usr/bin/env python3
"""Compare unchanged rho walk semantics across field implementations."""
from __future__ import annotations
import hashlib,json
from typing import Any

class RhoSemanticError(RuntimeError): pass

KEYS=("published_fixture_scalar","recovered_fixture_scalar","published_q","verified",
      "reference_group_validation","quotient_mode","arithmetic_backend","walk_steps",
      "charges","restarts","table_entries")

def canonical(record:dict[str,Any])->dict[str,Any]:
    missing=[key for key in KEYS if key not in record]
    if missing:raise RhoSemanticError(f"rho receipt missing mandatory fields: {missing}")
    return {key:record[key] for key in KEYS}

def check(old:dict[str,Any],new:dict[str,Any])->dict[str,Any]:
    left,right=canonical(old),canonical(new)
    if left!=right:
        keys=[key for key in KEYS if left[key]!=right[key]]
        raise RhoSemanticError(f"rho semantics mismatch: {keys}")
    digest=hashlib.sha256(json.dumps(left,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {"valid":True,"semantic_sha256":digest,"fields":list(KEYS)}

def self_test()->None:
    record={key:0 for key in KEYS}
    assert check(record,dict(record))["valid"]
    mutated=dict(record);mutated["walk_steps"]=1
    try:check(record,mutated)
    except RhoSemanticError:pass
    else:raise AssertionError("changed walk accepted")
    missing=dict(record);missing.pop("charges")
    try:check(missing,missing)
    except RhoSemanticError:pass
    else:raise AssertionError("same missing field accepted")
    print(json.dumps({"self_test":"PASS","tests":3},sort_keys=True))

if __name__=="__main__":self_test()
