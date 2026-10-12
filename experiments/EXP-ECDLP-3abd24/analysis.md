# Analysis EXP-ECDLP-3abd24

Review task TASK-20261003-ffea51. Hypothesis H-ECDLP-3091c2. Approval
DEC-20261003-2cf084. Producer task TASK-20261003-5a2a7c. No exponent.

## Observation

Stage 0 run RUN-ECDLP-4e0a4f is O-STAGE0-OK. The raw result records
twin_ok, easy_control_pass, and s3_addition_pass, with claims.break false
and claims.exponent_move false. The receipt is output_validated, returncode
0, check_returncode 0. stdout.log is 0 bytes. check.stdout.log is the
five-byte checker token PASS. That token is not a second scientific outcome.

Stage 1 run RUN-ECDLP-73cb29 is O-FULL. RESULTS.md names that single O-*
label and the same three cells. Each cell has frac_full 1, null_frac_full 1,
easy_ok true, dual_fail 0, unsat_count 20, and frac_bounded 0:

- n=8, s=4, p=8209
- n=10, s=5, p=65537
- n=12, s=6, p=524309

The Stage-1 receipt is output_validated, returncode 0, check_returncode 0.
stdout.log is 0 bytes. Archived raw-result wall time is 60.367 seconds.
The Stage-1 manifest records code.commit
e37186568e5e87cd9e1bfffb00bbc51158e0cf2f and code.dirty true. claims.break
is false and claims.exponent_move is false. The four implementation source
hashes in that manifest match the bytes in this checkout.

decide() returns O-ARTIFACT when any cell has a dual failure or a failed
easy control, O-INCONCLUSIVE when the only failure in that gate is an unsat
shortfall below 20, and O-ARTIFACT when any null_frac_full is below 0.90.
Only after those gates does it test O-BOUNDED (frac_bounded at least 0.90
on every cell) and, if that test is false, O-FULL. frac_bounded 0 does not
select O-BOUNDED.

A Stage-1 replay under /tmp/review-ecdlp-3abd24, from a copy whose stage1
json and RESULTS.md had been removed, returned O-FULL. Replay cells repeat
frac_full 1, frac_bounded 0, null_frac_full 1, easy_ok true, dual_fail 0,
and unsat_count 20 at the same three primes. Replay wall time was 66.546
seconds. The replay did not write the repository stage files.

## Comparison

Blind re-derivation, done before implementation/, stage0/, or runs/ were
opened: for s in {4, 5, 6}, n=2s and the least prime strictly greater than
2^{3s+1}.

| s | n | bound 2^{3s+1} | least prime | archived p | match |
| --- | --- | --- | --- | --- | --- |
| 4 | 8 | 8192 | 8209 | 8209 | yes |
| 5 | 10 | 65536 | 65537 | 65537 | yes |
| 6 | 12 | 524288 | 524309 | 524309 | yes |

The replay primes are the same three values. Archived O-FULL and replay
O-FULL agree on the label and on the per-cell fractions. O-BOUNDED would
require frac_bounded at least 0.90. The measured fraction is 0, so the
bounded branch does not fire. Null frac_full is 1, which is above the 0.90
artifact line.

## Inference

O-FULL is the expected full-degree obstruction for plain Macaulay on these
three cells: deg(f^{-1}) equals n on every counted unsatisfiable draw, the
same-support null is also full, and the easy control reads degree 1. That
is support for the scoped degree label in H-ECDLP-3091c2. It is not a
speedup, not an exponent move, and not O-BOUNDED. O-BOUNDED is the reading
that would treat plain Macaulay as a poly-time inner oracle, and these rows
do not have it. Null FULL is the calibration the hypothesis requires before
O-FULL is available. It does not say the unsatisfiable residual is
low-degree.

## Limitation

The label covers s in {4, 5, 6} only, with the frozen sample counts, the
frozen prime rule, and the dual Möbius meters in this experiment. It does
not transfer to n greater than or equal to 131. Stage-2 W_D is not
authorized and was not run. FULL is not a break. Strength is preliminary
and the basis is empirical. The Stage-1 manifest's code.dirty true is
disclosed; this review did not reconstruct the uncommitted diff from the
execution host. Empty stdout is not a second outcome: the label lives in
raw-result.json and RESULTS.md, and both agree with the replay.
