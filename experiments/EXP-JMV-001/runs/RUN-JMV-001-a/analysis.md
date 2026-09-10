# EXP-JMV-001 RUN-JMV-001-a — analysis

Authorized by: `DEC-20260906-b083ce` (the ONLY authorization citation for
this run; see `ledger/handoffs/TASK-20260906-e2719b.yaml`). Experiment
contract: `experiments/EXP-JMV-001/specification.yaml`, version 2, status
`approved`.

**This run stops at the table and the certificates.** No statement below
asserts that arXiv:math/0411378v3 itself contains an error. Per
`invalidation_rules`, the only permitted formulation for a row whose
recomputed arithmetic disagrees with the held transcription is: *"the
transcription we hold is inconsistent with these curves' parameters."*
Condition C1 (independent review of the transcription by a reviewer who did
not produce it) has not run and is out of this task's scope.

## Controls (precondition, per success_criterion)

All four control families pass on every one of the ten `curves_attempted`
rows (`controls.json`, `pipeline_valid: true`):

| control | rows checked | outcome |
|---|---|---|
| CTRL-ORDER-PRIME | P-192/224/256/384/521 | passes on all five |
| CTRL-ORDER-KOBLITZ | K-163/233/283/409/571 | passes on all five (derived order = cofactor x n_NIST) |
| CTRL-CM-KOBLITZ | K-163/233/283/409/571 | passes on all five (`d_pi = -7*c_pi^2` exactly) |
| CTRL-HASSE | all ten | passes on all ten (`|t| <= 2*sqrt(q)`) |

Per specification.yaml, this is a precondition, not a result: it means the
computation pipeline itself is self-consistent on these ten rows, not that
any per-row Figure-1 comparison is correct or informative on its own.

## Conductor branch (D1)

For every one of the ten rows, `t` is odd, so `nu_2(d_pi) = 0` and `d_pi`
(prime rows) or the CM identity (Koblitz rows) place the row in the
`u = 1 (mod 4) -> c_pi = s` branch, matching the applicability note recorded
in `specification.yaml` at approval time. This is now an observation from
this run's own computation, not an inherited assumption
(`cpi_table.csv` columns `t_parity`, `conductor_branch`).

## Per-row table (full detail: `cpi_table.csv`; raw values: `raw.json`)

| curve | c_pi status | Figure-1 verdict | checks applied |
|---|---|---|---|
| P-192 | censored (residual 184 bits after trial division to 1e6) | censored/undecidable | none -- no held Figure-1 value for this row (spec gap, see below) |
| P-224 | censored (residual 182 bits) | censored/undecidable | none -- row stated as absent from Figure 1 as held |
| P-256 | censored (residual 255 bits) | contradicts | mod-9 exclusion (exact, factoring-free) |
| P-384 | censored (residual 386 bits) | censored/undecidable | none -- no held Figure-1 value for this row (spec gap) |
| P-521 | censored (residual 521 bits) | censored/undecidable | none -- no held Figure-1 value for this row (spec gap) |
| K-163 | exact (1824026374634505274957943, 81 bits) | contradicts | product identity, primality, maximality (all three; two separate certificates) |
| K-233 | exact (72051847988516734697809995873370769) | reproduces | product identity, primality, maximality (all three pass) |
| K-283 | exact | reproduces | product identity, primality, maximality (all three pass) |
| K-409 | exact but incompletely factored (96-bit residual after listed factors) | censored/undecidable | divisibility of listed factors |
| K-571 | exact but incompletely factored (263-bit residual after listed factors) | censored/undecidable | divisibility of listed factors |

**Counts:** reproduces = 2 (K-233, K-283); contradicts = 2 (P-256, K-163);
censored/undecidable = 6 (P-192, P-224, P-384, P-521, K-409, K-571);
not_attempted = 0 (all ten `curves_attempted` rows were attempted; the seven
`curves_not_attempted` rows are out of scope entirely and are not reported
with any result, per `invalidation_rules`).

Note on P-256 and K-163: neither verdict above is described as
"reproduces Figure 1 on the product identity alone" -- the P-256 case uses no
product identity at all (a direct mod-9 exclusion on the held value itself),
and the K-163 case fails on primality and on the product simultaneously, so
its `contradicts` classification does not rest on any single weaker check.

## Certificates

Three certificate files under `certificates/`, each independently
re-checked by `verify_certificates.py` (a separate program sharing no code
with `run_conductor_audit.py`, described in that file's own header):

- `P-256_mod9.json` -- result `CONTRADICTS`, independently re-derived from
  the published `(p, n)` pair alone.
- `K-163_composite_P.json` -- result `CONTRADICTS`, requires no curve data.
- `K-163_product_mismatch.json` -- result `CONTRADICTS`, depends on
  CTRL-ORDER-KOBLITZ and CTRL-CM-KOBLITZ passing (both do).

`python3 verify_certificates.py` (run from this directory) prints
`ALL CERTIFICATES INDEPENDENTLY RE-VERIFIED` and exits 0. No certificate
rests on the trial-division search alone (`certificate_discipline.
forbidden_basis`); the P-256 certificate is a pure mod-9 residue argument
and the two K-163 certificates rest on curve-derived exact values and on
direct multiplication of small integers, never on a censored negative.

## Reported specification gaps (reported, not patched, per this task's
## frozen-protocol constraint)

1. **Verdict enum has no value for "row stated as absent from the held
   transcription."** `specification.yaml`'s `metrics.primary` enumerates the
   per-row verdict as one of `{reproduces, contradicts, censored/
   undecidable, not_attempted}`. P-224 is inside `curves_attempted` (its
   curve arithmetic runs and its controls pass), but the held transcription
   explicitly states P-224 has no row in Figure 1 at all. None of the four
   enum values names this case precisely: `not_attempted` is defined
   elsewhere in the same spec as the status of the seven
   `curves_not_attempted` rows, a different and disjoint set, so reusing it
   here would overload one value with two distinct meanings. This run uses
   `censored/undecidable` as the nearest available bucket (meaning "no
   reproduces/contradicts verdict can be rendered"), and records the actual
   reason in `cpi_table.csv`'s `fig1_reason` column and in
   `figure1_transcription.md`. This is flagged as a candidate for a future
   versioned `protocol_amendment`, not resolved by this run.

2. **The held transcription is silent -- not merely absent -- on three
   rows.** P-192, P-384, and P-521 are inside `curves_attempted`, their
   arithmetic is fully computed and their controls pass, but no numeric
   Figure-1 value for any of these three rows exists anywhere in this
   program's held transcription artifact (`research/
   JMV2005_experiment_suite_20260726.md` or `cpi_audit.py`). This is
   different in kind from the P-224 case (explicitly stated as absent): here
   the artifact never addresses these rows at all, so it is unknown whether
   the paper's Figure 1 even lists them, let alone what values it gives.
   `specification.yaml`'s own `figure1_transcription_artifact` note
   anticipates only the P-224 gap ("contains no P-224 row") and the K-409/
   K-571 `P(c_pi)` gap; it does not anticipate this three-row silence. This
   run reports it explicitly rather than silently treating these rows as
   `reproduces` or inventing a value, and uses `censored/undecidable` for
   the same enum-coverage reason as (1) above.

3. **P-256's row carries no listed-factor product to run the three-part
   CTRL-FIG1-ROWCHECK against.** The held transcription states only a single
   value, `c_pi = 3`, `P(c_pi) = 3`, for P-256 -- there is no separate list of
   smaller factors multiplied by a claimed largest prime, unlike the K-rows.
   `CTRL-FIG1-ROWCHECK` as written is framed around "a row whose
   transcription carries a COMPLETE claimed factorization
   `c_pi = f_1*...*f_j*P(c_pi)`" (plural factors) or an incomplete one with
   listed non-P factors; P-256's held row fits neither shape exactly (it is
   a factorization with zero non-P factors). This run treats the mod-9
   argument as the applicable check for this row (it is exact, sufficient by
   itself to exclude the held value, and requires no factoring), and does
   not claim to have executed the three-part rubric's `primality`/
   `maximality` sub-checks on a factor list this row's held content does not
   contain.

None of these three gaps is patched, worked around silently, or resolved by
this run; each is reported here and in `figure1_transcription.md` /
`transcription_fidelity.md` for the Coordinator to consider as candidate
`protocol_amendment` material.

## Level counts (D2)

Level count (number of divisors of `c_pi`) is reported ONLY for K-233 and
K-283 (both = 8, from three distinct prime factors each with exponent 1:
`2^3 = 8`), the only two rows with a complete, primality-checked
factorization of `c_pi` itself. It is censored for every other row,
including P-256, K-163 (its `c_pi` is exact but this run does not establish
a complete prime factorization of it independently of the held, contested
Figure-1 factors -- the certificate shows the printed factorization is wrong,
not what the correct one is), K-409, and K-571 (`c_pi` exact but
unfactored). No naive square-part value is reported as a D1 conductor
anywhere in this run's output; the naive square part below the trial bound
is reported only in the `secondary` column, explicitly labelled.

## What this run does not claim

- No statement anywhere in this file, `figure1_transcription.md`,
  `transcription_fidelity.md`, `controls.json`, `raw.json`, or
  `cpi_table.csv` asserts that arXiv:math/0411378v3 contains an error.
- The words "verified", "confirmed", and "finding" are not used in this file
  to describe any Figure-1 result; controls and certificates are described
  as "passing," "checked," "established by exact computation," or
  "re-derived," and results are described as observations, not findings.
- No CORR- record is produced by this task for any Figure-1 discrepancy.
- No statement about dlog difficulty, Theorem 1.1, Corollary 1.2, or GRH is
  made anywhere in this run's artifacts.
- This run's output does not by itself satisfy control C1; the
  UNCHECKED-AGAINST-SOURCE banner in `figure1_transcription.md` stands until
  a separate, later reviewer task checks the held transcription against
  arXiv:math/0411378v3 itself.
