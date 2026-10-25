# Frozen first-stage Frobenius conductor audit

Frozen 2026-10-23 UTC before exact factoring of the omitted P-256 discriminant in this round.

## Question and fixed inputs

Does the omitted P-256 seed block 876 have a nontrivial Frobenius-order conductor `f_pi` while published P-256 block 1842 has `f_pi=1`? This is a first-stage necessary test for a universal omitted-curve rule based on nonmaximal `Z[pi]`. It does not test the representative conductor `f_E` or establish an ECDLP advantage.

Inputs are the exact archived `p,n` and EC1 identities for those two rows from `research/nist_seed_skipped_curves_20261016/assessed.json` (SHA-256 `370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`) and `traits.json` (SHA-256 `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`). Group-order certificates are inherited from those records. Recompute `Delta=t^2-4p`, `t=p+1-n`; factor `|Delta|` exactly, certify every factor prime, and derive the fundamental negative discriminant `D_K` and `f_pi` with `Delta=f_pi^2 D_K`.

## Method, controls and limits

- One PARI/GP `factor` call per fixed real row, with a 180-second wall watchdog and 2 GiB address-space cap. Preserve each stdout, stderr, exact command, tool version, exit status and elapsed time. A timeout or failure is `INDETERMINATE`.
- Synthetic arithmetic positives: `Delta=-75` must yield `D_K=-3, f_pi=5`; `Delta=-7` must yield `D_K=-7, f_pi=1`. A deliberately nonfundamental candidate `D=-12` must not be reported as fundamental when `Delta=-12` (canonical answer `D_K=-3, f_pi=2`).
- Before the real rows, run the launcher's `--inject-exception` and `--inject-early-return` controls in separate write-once directories. Both must exit nonzero without `complete.ok`; retain their logs. A pass marker is written only after independent verification succeeds.
- Independently verify product, proof-enabled primality of every factor, fundamental-discriminant criterion, and the square identity with Sage. Check all four target/synthetic rows. Preserve raw and verification output. No result is inferred from a probable-prime factor or from a partial factorization.
- Stop the first stage after the two fixed real rows and three controls. Do not retune the test after reading the omitted result. Memory and watchdog protect the host, not the research budget.

## Outcome policy

- If block 876 has `f_pi=1`, then nontrivial Frobenius-order conductor is not shared by all eleven omissions. The narrower tested first pair is a counterexample; other structural routes remain open.
- If block 876 has `f_pi>1` and published P-256 has `f_pi=1`, freeze a second-stage protocol for all eleven omissions and ten controls. Do not infer a weakness from this pair alone.
- If any certificate or control fails, report `INDETERMINATE` and repair the implementation under an additive new record. Historical selection remains unproven in every branch.

Required artifacts: raw transcript/receipt, exact factor list and derived values, independent Sage verification, dated report, editable diagram and SVG, quantitative chart if useful, PDF visually inspected, source hashes and exact commands. No official research-state transition is made by this audit.
