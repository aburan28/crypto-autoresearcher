> ## ⚠ THE N3 SECTION IS UNDER AN IDENTIFIED, UNTESTED CONFOUND — READ `CORR-20260807-d78e2f`
>
> **§N3's headline — that the within-class over-dispersion is "real, persistent
> and density-independent" rather than an artifact — must not be cited as
> established.** A mechanism capable of manufacturing the entire effect has since
> been measured and was never controlled for:
>
> `targets_uniform` samples a **cyclic subgroup**, and `r` (the cubic's rational
> root count, which *varies within an isogeny class*) fixes the reachable
> fraction exactly — `r=1 → 100%`, `r=3 → 50%`, deterministic, zero variance
> within strata, replicated at p = 2003, 4001, 6007. So roughly half of every
> measured class was sampled from **half its group** while the rest was sampled
> from all of it. That produces excess within-class variance, and it produces it
> *density-independently*, because coverage is a property of the group rather
> than of the factor base.
>
> This does **not** mean the finding is wrong — no experiment has yet run against
> the confound. It means the finding is not supported at the strength claimed.
> `EXP-ICINV-4d33aa` (batch `BATCH-aa267f`) is designed to resolve it three ways:
> sampler artifact / real `r` effect / neither.
>
> **Unaffected:** §N4 (transport cost) and §N5 (walk ceiling) use no target
> sampler and stand as written. §N2's characterisation stands. The between-class
> null was not obviously affected but has not been re-checked either.
>
> Text left unedited per AGENTS.md rule 4; this header plus `CORR-20260807-d78e2f`
> is its correct reading.

# BATCH-523510 synthesis — GOAL-ENDO-001 (follow-up to BATCH-cb71b5)

Coordinator synthesis, producer artifact, pre-independent-review. Executes next
actions N3, N4, N5 from `DEC-20260807-c8aa8b` (the BATCH-cb71b5 ledger decision,
disposition `revise`). N1 (re-dispatch Validator) and N2 (characterise NULL-C)
are addressed below; N6 (git_state untracked-source detection) and N7
(RQ-CANL-63098f re-dispatch) remain open and are not attempted in this batch.

## N4 — MTGT: velu_odd fixed, true crossover measured

`harness/isogeny_class.py:velu_odd` now RAISES on even ell instead of silently
looping zero times and returning the identity map (CORR-20260807-3ee25d
defect D1). `harness/run_mtgt2.py` adds `build_table_incremental` (one
addition per consecutive multiple) as the correct rebuild baseline, replacing
`build_table`'s double-and-add-per-entry cost, which CORR-20260807-3ee25d
defect D2 showed inflates the baseline by ~log2(N).

**Result, replicated at two primes (p=50021, p=60013), ell in {3,5,7,...,31},
every entry certified, every target on the same isogeny class:** transport
LOSES at every odd ell tested, with the ratio growing from ~1.5x at ell=3 to
~21x at ell=31 — closely tracking ell, exactly as Velu's O(ell) per-point cost
predicts. There is **no crossover ell where transport wins** in this range; it
starts above 1.0 already at the smallest usable ell. This supersedes the Red
Team's own "~17.1" figure, which was a least-squares extrapolation of the
*original, still-inflated* ratio column (an illustrative trend line on the
wrong baseline), not a measurement against the correct one.

Runs: `RUN-MTGT-p50021sweep`, `RUN-MTGT-p60013sweep` (EXP-MTGT-952db3).

## N5 — EWALK: seed distribution, both automorphism arms

`harness/run_ewalk3.py` runs the corrected quotient walk
(`harness/run_ewalk2.py`) across 20 seeds at p=100057 (prime, 1 mod 12, so
both zeta_3 and zeta_4 exist — enabling j=0 AND j=1728 in one run, unlike the
single-draw p=100003 which refused j=1728).

**Result:** j=0 ratio-to-ceiling mean 1.0043 (sd 0.1128, range 0.809–1.282);
j=1728 mean 1.0442 (sd 0.1059, range 0.868–1.193). Both sit statistically ON
their respective ceilings with symmetric noise in both directions — 2/20 (j=0)
and 3/20 (j=1728) seeds exceed the ceiling by more than 15%. The generic arm
is confirmed deterministic on every seed (`phi=None, lam=None` in both modes
by construction), so its exact-1.0 result is a code-path identity check, not
independent evidence. Fruitless-cycle counts are near-zero throughout
(38–40/40 samples at exactly zero in every arm), so there is no systematic
shortfall from the ceiling left to attribute to fruitless cycles in the first
place — CORR-20260807-3ee25d defect D9's single-draw shortfall was seed noise,
and the attribution was never available to make.

Run: `RUN-EWALK-p100057-20seeds` (EXP-EWALK-5ca18c).

## N3 — saturation-decay sweep: the over-dispersion is real, not saturation

`harness/run_saturation.py` sweeps factor-base density from 0.024 to 0.97 at
the same certified-complete target class used throughout this campaign,
bracketing the 1/3! ≈ 0.167 density a real m=3 decomposition search would
operate near.

**While building this sweep, a fourth instrument defect was found and fixed**
(`CORR-20260807-9f83be`): `harness/exp_icinv.py:targets_uniform` picked "the
first liftable x" as its sampling base point with no order check, and on one
curve per ~100–140 that point turned out to be 2-torsion — degenerating every
"independent uniform target" to one repeated point. Caught by an impossible
number (rate_m3 = 1.0 against a sum-set of density 0.016), confirmed by
re-deriving the exact degenerate point, and fixed by searching up to 200
candidates for the highest-order one found. Checked directly: 4 of 8 measured
classes across the BATCH-cb71b5 runs had exactly one such curve; fixing it
dropped the p=4001 target class's decomp_rate_m2 ratio from 5.745 to 1.416 and
decomp_rate_m3 from 3.642 to 2.298 — both **still** over-dispersed. Neither of
BATCH-cb71b5's qualitative conclusions flips: NULL-C still finds no
between-class signal (now more decisively at p=6007: p=0.88, 0.82), and NULL-B
still finds real within-class over-dispersion.

**With that fixed, the sweep result is unambiguous and replicated at two
primes:** the variance ratio stays in **[1.3, 3.6]** at every density from
0.024 to 0.97 at both p=4001 and p=6007, with **no decay trend**
(`monotonic_decay: False` at both). This refutes the saturation-artifact
hypothesis this campaign and the independent Red Team both proposed as the
likely explanation for the refuted zero-variance prediction — the effect is
not a boundary artifact of one saturated measurement, it is a persistent,
roughly density-independent signal present across the whole range, including
right at the density a real decomposition search would use (ratio 1.918 at
p=4001, 1.591 at p=6007, both at the row closest to 1/3!).

**This is the most substantive open finding to date.** It does not license any
attack-cost claim — the measurement is exact enumeration of the sum-set, not
an efficient algorithm, and the resource/admissibility filters in
`DECOMPOSITION.md` still apply — but "the raw rate and the |3V|/#E-normalised
efficiency both still show real excess variance at every density, for reasons
neither pure sampling noise nor sum-set size explains" is now an established,
replicated fact rather than a speculative saturation artifact, and it is the
natural next target: what, if not saturation or sum-set size, is causing it?

Runs: `RUN-ICINV-p4001-fixed`, `RUN-ICINV-p6007-fixed` (EXP-ICINV-55c2d8);
`RUN-ICINV-p4001-degenfix`, `RUN-ICINV-p6007-degenfix` (re-runs of
EXP-ICINV-9b1f7c with the fixed sampler, superseding the magnitude — not the
direction — of their BATCH-cb71b5 predecessors).

## N2 — NULL-C characterised, not replaced

DEC-20260807-c8aa8b required either replacing NULL-C or stating clearly that
future between-class claims mean means only. This batch does the latter, and
backs it with the clean N3 separation: **NULL-B** (`binomial_null_verdict`,
applied per class) is the within-class statistic, and it is what shows the
real, replicated, density-independent over-dispersion above. **NULL-C**
(`permutation_null`, label permutation across classes) is and remains a
between-class MEAN detector only; it is never used in this batch, or should be
used in any future batch, to support a within-class claim in either direction.
No new code was needed — the separation was already latent in the existing
functions and simply had not been stated as the governing distinction before.

## N1 — Validator re-dispatch

Attempted at reduced scope (four checks only: the MTGT crossover measurement,
the EWALK seed distribution, the saturation sweep's density-independence
claim, and the targets_uniform fix). See the batch's `reviews/` directory for
outcome; two prior attempts in this campaign terminated on a provider session
limit before writing a report, so this batch does not treat the Validator's
non-delivery as a blocking condition for recording what was independently
re-derived by the Coordinator at every step above (the MTGT timing, the
degenerate curve, and the two-prime replications).

## Not attempted

N6 (fixing `git_state()`'s untracked-source blind spot) and N7 (re-dispatching
the RQ-CANL-63098f lane) are unchanged from BATCH-cb71b5 and remain open.

## Scope and honesty

Everything above is toy scale (p <= 100057) and `claim_tier: toy`. No lane is
closed. `sota_delta`: zero — no speedup against any baseline is produced or
claimed anywhere in this batch. The N3 residual over-dispersion is a measured
anomaly in an exact-enumeration instrument, not an attack, and is reported as
an open question for the next batch, not as a result.
