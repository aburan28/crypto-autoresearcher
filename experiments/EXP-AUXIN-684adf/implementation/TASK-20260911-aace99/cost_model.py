"""Measured operation accounting; no predicted costs are substituted for observations."""
from __future__ import annotations
def new_counters(): return {"gcd_calls":0,"inverse_calls":0,"candidate_enumerations":0,"residue_tests":0,"pow_calls":0,"scalar_equalities":0}
def descriptive_rows(measured):
    return [{"id":f"F{i}","value":measured.get(key,0),"status":"measured" if i<6 else "not_executed"} for i,key in enumerate(("gcd_calls","inverse_calls","candidate_enumerations","residue_tests","pow_calls","scalar_equalities",None,None,None))]
