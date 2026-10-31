# BINSTD algebra proof fidelity: pre-review plan

Prepared before reviewer dispatch, 2026-10-31 UTC. This is a technical review, not an experiment decision.

## Frozen inputs and producer claims

- Auto-researcher main commit: `7a40243d9db4de7c1310e2534897b7d6e7d02929`.
- Lean sources and Git blob IDs: `Factorization.lean` `eff52d75ffe368301977e4a2ae735ac5cfae8a14`; `Irreducibility.lean` `83a4db9614030b06e466147cc20b8ffd808572c5`; `CanonicalFrobenius.lean` `e96483cca80a5a884306a691c69deaf8127e3c04`; `EncodedDivisors.lean` `6c2a577afb11f2893ad3973266c11f1575444f2f`. All are under `formal/CryptoResearch/Binstd/`.
- Runner field source: `experiments/EXP-BINSTD-8bdf86/implementation/gf2.py` blob `d891897b9c5e00e176b52fb0067eb6bfca322ebe`. Historical report: `research/binstd_end_to_end_20261026/REPORT.md` blob `3c0c373fb2402dd1e37818e4d2a3afec64d8bae7`.
- Toolchain and dependency manifest blobs: `formal/lean-toolchain` `3d1dc1d0f50b488e6c6b3496524dd7df672082e8`, `formal/lake-manifest.json` `bed58e530beda3e048c5f537af47fdf987c96a78`.
- Producer's current Lean claims: `x17_factorization` gives the exact product in `(ZMod 2)[X]`; `factor8_irreducible_pair` proves both degree-eight polynomial declarations irreducible; `canonicalFrobenius_order_and_minpoly` concerns abstract `GaloisField 2 17`. `EncodedDivisors` independently certifies finite bitmask trial outcomes. The 2026-10-26 report predates the irreducibility and canonical-field modules and says those steps remain open; review the present theorem state without rewriting historical execution evidence.

## Prior and load-bearing joints

Prior, recorded before reviewer findings: the polynomial and abstract-field theorem types appear narrower than the actual Python field and empirical yield claim; expect the two degree-eight irreducibility statements to be valid at their declared polynomial scope, with the concrete encoding and execution bridges open. This is a hypothesis for attack, not a verdict.

| Joint | Reviewer owner | Worked attack / known-false control |
| --- | --- | --- |
| J1: archived masks and runner arithmetic match the declared polynomials | source reviewer | Decode masks 313, 471, 131081 independently; compare all coefficients and modulus with pinned Python and receipts. Flip one bit in a mask and show it changes at least one identity. |
| J2: exact Lean declaration types and machine evidence | Lean reviewer | Inspect elaborated types, exact pins, named hosted receipts, transitive axioms and module inclusion. Test a false factor or altered cyclotomic order under the same gate if capacity permits; missing execution is `not_verified`, not proof failure. |
| J3: blind mathematical derivation of factorization and factor degrees | blind reviewer | From only the requested polynomials and base field, recompute the product and a degree-eight irreducibility argument without reading producer proof, reports, receipts or sibling verdicts. Use a reducible nearby polynomial as a negative control. |

## Blindness and decision rule

J3 may read only this section's mathematical input: over `F₂`, let `a=X^8+X^5+X^4+X^3+1`, `b=X^8+X^7+X^6+X^4+X^2+X+1`; determine whether `(X+1)ab=X^17+1` and whether `a,b` are irreducible. J3 must not read the source files, the rest of this plan, archived reports or J1/J2 reports until its answer is frozen. J1 and J2 must not read each other's work before freezing their own reports. Reviewers record paths read and sibling access.

The coordinator will check reviewer independence and separate machine status from semantic fidelity. No acceptance of a concrete runner/Frobenius or performance claim follows solely from the abstract polynomial and canonical-field theorems. A reported correction needs exact source binding, current-head verification and its own review; an old receipt is not silently promoted.
