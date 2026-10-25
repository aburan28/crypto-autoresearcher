# Frozen card v2 (proposed, not approved): degree-5 closure of C19a/b with `hky_par`

Supersedes the engine choice, not the question, of `CARD-d5-c19.md` (which is unchanged). Numbers: `crosscheck-hky-par-20261020.md` (derived, extrapolated 6.2x).
- Task: decide 1 in W_5 for C19a and C19b (`../semaev-m2-last-fall-degree/results/instances_t3.json`). A "no" needs a closure certificate checked by `cert_check.py`. `hky_par` produces none, so a "no" from it alone is a measurement, not a certificate; a certificate would still need `lfdclose2` (256 GB card).
- Command: `hky_sys sys C19a.sys --cmax 5` (scratch subcommand; see raw diff) at crypto commit 981f80710b7efd7513ff6f3f70296a1148688b41.
- Host (planning, unvalidated): 128 GB RAM, >= 16 cores. Expected 6-41 h on 4 cores by extrapolation; floor for RAM 33 GB, quadratic estimate 93 GB.
- Cross-check done at degree 4: identical dimensions to #2410 on C19a/b.
- Not covered: W_6, certificate production, descent agreement.
