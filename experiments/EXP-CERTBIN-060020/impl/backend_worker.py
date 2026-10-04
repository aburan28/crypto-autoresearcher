#!/usr/bin/env python3
"""Separate-process worker for C-SELF (ix): reads a JSON list of E_hex
systems on stdin and prints their M_4 and W_4 engine records under whatever
CRYPTO_AR_GF2_BACKEND the caller set (reference for C-SELF (ix))."""
from __future__ import annotations

import json
import sys

import common as C
import closures as CL
from crypto_autoresearcher.gf2 import kernels


def main():
    systems = json.loads(sys.stdin.read())
    out = []
    for h in systems:
        eqs = C.E_to_eqs(C.E_from_hex(h))
        r4, _ = CL.macaulay(C.NV, 4, C.NEQ, eqs, want_cert=True)
        w, *_ = CL.w_closure(C.NV, 4, C.NEQ, eqs, want_cert=True)
        out.append({"M_4": r4, "W_4": w})
    print(json.dumps({"backend": kernels.backend(), "records": out}))


if __name__ == "__main__":
    main()
