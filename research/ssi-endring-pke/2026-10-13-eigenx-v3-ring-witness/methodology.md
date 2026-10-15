# EigenX-v3 ring-witness methodology

This is a prospective, zero-run theory-construction-or-obstruction round under
`GOAL-SSI-2fa82a`. It evaluates exactly one public-key encryption candidate:
a polynomial-time complete-EndRing certificate relation `R_CER`, a
relation-specific distributional extractable witness-encryption core, and a
Naor--Yung plus simulation-sound-NIZK CCA transform. KEM/DEM is optional and
cannot replace the PKE core.

The round keeps complete-EndRing separate from DXWE/XWE, auxiliary-input EWE,
simulation-sound NIZK, transform, setup, KDF and DEM assumptions. In
particular, ordinary XS-WE that generates its own instances and cannot accept
an external complete-EndRing challenge is an explicit negative control, not a
reduction interface. Auxiliary-input extractability is reviewed for
circularity and over-strength.

Five mutually blind reviewers own: `R_CER` algebra and correctness;
extractor/reduction direction and oracle simulation; full-ring necessity
against quotient controls; CCA and malformed-ciphertext handling; and primary
sources, nonduplication, setup, assumptions and total cost. A Coordinator
composes their verdicts without voting. The documentation package then
contains `report.md`, editable `flow.mmd`, `flow.svg`, this methodology,
`report.pdf`, and `visual-inspection.yaml`, followed by an independent J6
documentation review.

No scientific, implementation, formalizer, benchmark or parameter-selection
run is authorized. A populated contract is not a secure-scheme claim. The
terminal archive records a construction, scoped obstruction or exact open
obligations, checkpoints the still-active goal as warranted, and closes only
this lane.
