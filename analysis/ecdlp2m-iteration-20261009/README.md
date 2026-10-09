# GOAL-ECDLP2M-001 iteration, 2026-10-09: derived audits

This directory holds pre-compute audits and derivations made during a read-only
`/deep-research` pass and a follow-up iteration on GOAL-ECDLP2M-001 (binary-field
ECDLP). Each one can be regenerated from the scripts here.

Nothing here is an experiment, a run record, evidence, or a decision. No ledger
record was written and no status changed. A conclusion becomes official only
through the normal lifecycle: a contract, `/run`, and a Coordinator archive or
correction. Every figure here is labelled measured, derived, or published, with
its provenance given in the sub-directory README.

| sub-directory | what it is | headline |
| --- | --- | --- |
| `certbin-k2-collision-audit/` | Replay audit of EXP-CERTBIN-66e167 Stage 1 (EV-CERTBIN-691499, DEC-20261004-d70aac) that classifies every colliding pair | The archived k=2 "excess" (17 and 38 pairs against a birthday expectation of 5.00) is an instrument artifact. Structural identities that hold for every generator account for 16/17 and 33/38 pairs. The kernel span held only 2G+tG+t^2G per generator, so it missed P+(-P) and the tau-shifted relations. The genuine collision ratios are 0.20, 0.40, 1.00 and 0.80. |
| `c1-gaudry-n4-c2pnb/` | Three-metric cost model: Gaudry-Diem fixed-n=4 double-large-prime index calculus with a pi_16 orbit factor base on the ANSI X9.62 example curves c2pnb176v1/208w1/272w1/304w1/368w1 | Time only, it beats matched rho on all five rows across c_trial in [2^15.5, 2^32.5]. Under the program's time x memory convention against vOW, it loses on every row inside that band. Under mesh area-time, it wins only on 304w1 and 368w1 at c_trial <= 2^27. The per-trial cost at toy size has never been measured. |
| `ctrial-harvest/` | Every recorded per-attempt point-decomposition cost (411 rows, 1554 per-target values) from main and the unmerged branches, fitted against l and extrapolated to ECC2K-130 | At m=3 and m=4, measured per-attempt costs extrapolate 50 to 150 bits above every budget line at n=131. WDSat UNSAT conflict counts match exhaustive search, 2^(3l)/3!, with a slope of 2.9985 bits per unit l. m=5 and m=6 have no usable data. |

## The criterion these results share (derived)

Relation collection beats rho only if a failed decomposition attempt costs
2^(alpha*l) with alpha < m/2 - 1, where l is about n/m. Every measured SAT or
enumeration method has alpha of about m, so it never qualifies.

The only mechanism that could give alpha near 0 is refutation by closure at a
bounded degree D, where D does not grow with n. This has been measured only at
m=2 (KN-FIND-5a8d3e, -c3a917), where it cannot help because m/2 - 1 = 0. At m >= 3
it has not been measured (KN-OPEN-3c8f51 item B, KN-OPEN-d218ec). That question is
the dispute recorded in KR-IC-889857.

## Instruments and environment

- Python 3 with the standard library, plus sympy where noted. M4RI and Sage are not
  needed for these three audits.
- The CERTBIN audit imports the archived implementation unchanged from
  `experiments/EXP-CERTBIN-66e167/implementation/`. It reproduces the archived raw
  pair counts exactly: 17, 5, 38, 7.
- `SHA256SUMS` binds every file in this directory.
