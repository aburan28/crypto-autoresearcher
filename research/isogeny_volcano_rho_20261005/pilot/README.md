# Pilot: Koblitz curve vs 8 curves on its 73-floor (superseded by the parent study)

First run of this question. 10 arms × 5,000 verified solves: the crater with
negation + Frobenius, the crater with negation only (control), and 8 curves
from explicit 73-isogenies (`iso.gp`, `curves.txt`). Result: the 8 isogenous
curves equal the control (KW p = 0.97 steps, 0.93 time; each within ±5%);
Frobenius saves 5.55× steps / 2.76× time. Protocol in `PROTOCOL.md`; numbers in
`results.json`; figure `isogeny_rho_measured.png`. Note: this pilot's `rho.c`
is identical to the parent's (sha256 in both PROTOCOL.sha256 files).
