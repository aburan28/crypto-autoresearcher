# RT-20260803-f55e34 — what I re-derived, and how

Red team, independent session. Reviewed snapshot `1cd863b1`. Nothing below was
taken from the producer's transcript; every number is from a command I ran in
this session, or is marked `unable_to_check` with a reason in `report.yaml`.

**Nothing here is an ML-KEM break, a security proof, or a claim that any FIPS 203
parameter set does or does not meet its NIST category. Cost-model estimates, not
measurements. AGENTS.md rule 12 UNMET and UNWAIVED.**

---

## 0. Archive integrity (before reading anything)

Recomputed all eight `source_path_sha256` entries in
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-012/archives/TASK-20260803-3fac41/snapshot_receipt.json`
from the blobs at `1cd863b1` (`git show 1cd863b1:<path> | sha256sum`). All eight
matched, including `sage_attempt_transcript.txt` and `run_stdout_raw.log`, which
the `--stat` output truncated and which I initially suspected were working-tree
only. Parent `079bdb8b` confirmed. **Content-verified.** The package is a durable
artifact and I reviewed it as one.

## 1. Environment

- `/tmp/le` at `3e48ef4` (`git status --porcelain` empty, `git diff 3e48ef421ec2` empty).
- `/tmp/sagevenv/bin/python` → `sage.all` at
  `/tmp/sagevenv/lib/python3.11/site-packages/sage/all.py`, `sage.version` `10.8.7`.
- Every run below: `PYTHONPATH=` (cleared) so the shim cannot resolve, `cd /tmp/le`.

Caveat I applied to my own work: this is the **same** passagemath the producer
used, and the **same** estimator source. My agreement with the producer is a
third instance of one implementation, not independent corroboration of the model.

## 2. Direct reproduction of the headline numbers

| set | `primal_bdd` | `matzov` | margin |
|---|---|---|---|
| Kyber-512 | 140.1994731076207 | 139.65604148085845 | **0.5434316267622421** |
| Kyber-768 | 200.9587149140538 | 196.36624335005874 | **4.592471563995048** |
| Kyber-1024 | 270.7236234535225 | 262.3356800074737 | **8.387943446048837** |

All six values identical to the producer's to every printed digit. The report's
`+4.592472` uses the shim's `matzov` value (196.36624335399668); mine uses Sage's.
Difference 3.94e-09 bits.

## 3. Source loci — checked line by line

| claim | verdict |
|---|---|
| `lwe.py:13` `from .lwe_dual import matzov as dual_hybrid` | confirmed |
| `lwe_dual.py:493` `DH = DualHybrid()` | confirmed |
| `lwe_dual.py:496` `class MATZOV` | confirmed |
| `lwe_dual.py:689` `matzov = MATZOV()` | confirmed |
| `lwe_dual.py:551` `# p.29, we're ignoring O()` | confirmed |
| `mu = 0.5` at `lwe_dual.py:526` | **corrected: it is at :539.** `def Nf` is at :525-526; :526 is the docstring line. Immaterial, but the brief and the BATCH-011 coordinator note both cite :526 and future citations should say :539. |
| `nd.py:69` `class NoiseDistribution`, `nd.py:296` `class CenteredBinomial` | confirmed — DEF-A's root cause is correctly diagnosed |
| `type(RC.MATZOV).__mro__` = MATZOV → GJ21 → Kyber → ReductionCost | confirmed by reading `reduction.py` class declarations at :963, :860, :697, :12 |

## 4. The success-probability asymmetry (OBJ-3) — the producer's statement is wrong

`report.md` says "neither exposes a success probability". From source and from
running `PrimalHybrid.cost(beta_opt, params, zeta=0, babai=False, mitm=False,
red_cost_model=RC.MATZOV)` directly:

```
Kyber-512  ... "prob": "1.0", "repetitions": "1"
Kyber-768  ... "prob": "1.0", "repetitions": "1"
Kyber-1024 ... "prob": "1.0", "repetitions": "1"
```

and `lwe_primal.py:624-628`:

```python
# Repeat whole experiment ~1/prob times
if probability and not RR(probability).is_NaN():
    ret = ret.repeat(prob_amplify(0.99, probability),)
```

`primal_bdd` is therefore costed as **per-attempt × inverse success probability at
a declared 0.99**, with the multiplier reported. `MATZOV.__call__` has no
`success_probability` parameter and `MATZOV.cost` returns `Cost(rop=T_sample +
T_guess)` with no `prob`, no `repeat`, and no amplification. The public
`primal_bdd()` wrapper happens to strip `prob`/`repetitions` from what it returns,
which is presumably how the producer missed it.

Numerically the multiplier is 1 today. Structurally, one side has a slot for a
success-probability correction and the other has none — so a Ducas–Pulles-style
correction has nowhere to land on the dual side.

I also checked whether `mu` is the exploitable knob. It is not: moving `mu` from
0.5 to 2^-40 changes `N` by **0.4147 / 0.2828 / 0.2164 bits only**, because
`log(1/mu)` is additive inside a bracket dominated by `k_fft·log p`. Any real
correction must multiply `N`, which is exactly what S4's δ knob does. **S4's design
is right**; its coverage is what I fault in OBJ-1.

## 5. Cost decomposition (OBJ-2) — where the margin actually lives

From the returned `Cost` dicts at each optimum:

| set | log2 red | log2 guess | guess share | guess contributes |
|---|---|---|---|---|
| Kyber-512 | 139.5466 | 135.8809 | 7.304 % | 0.1094 bits |
| Kyber-768 | 196.3653 | 185.7707 | **0.0646 %** | **0.00093 bits** |
| Kyber-1024 | 261.9473 | 260.2526 | 23.600 % | 0.3884 bits |

At Kyber-768, 99.94 % of the claimed `matzov` cost is `T_sample` — lattice
reduction plus one sieve. The FFT distinguisher, the `N` short vectors and the
disputed independence law together account for **0.0009 bits**. The 4.59-bit
undercut is a block-size comparison (β 589 vs 606, sieve 583 vs SVP 640), not a
statement that the dual distinguisher is cheap.

And the two sides do not price short vectors the same way. `primal_bdd` calls
`costf(red_cost_model, β, d)`; `matzov` calls `red_cost_model.short_vectors(...)`,
which for `RC.MATZOV` resolves through the MRO to `GJ21.short_vectors`
(`reduction.py:863`) — a model that sizes `sieve_dim` so one sieve ≈ one BKZ call
and then returns `floor(2^(0.2075·sieve_dim))` vectors essentially free.

Corroborating tell: `N` sits immediately under that capacity at all three optima.

| set | log2 N | 0.2075·β_sieve | slack |
|---|---|---|---|
| Kyber-512 | 81.0788 | 81.1325 | **0.0537** |
| Kyber-768 | 119.7530 | 120.9725 | 1.2195 |
| Kyber-1024 | 165.9385 | 166.8300 | 0.8915 |

The optimiser drives `N` to the seam of the model Ducas–Pulles dispute.

## 6. The control nobody ran: margin vs n (OBJ-1)

Kyber shape held fixed (`q=3329`, `Xs=Xe=CenteredBinomial(2)`, `m=n`,
`RC.MATZOV`), only `n` moved.

| n | primal_bdd | matzov | margin | β_m/β_p |
|---|---|---|---|---|
| 256 | 70.4898 | 71.9111 | **−1.4213** | 1.028 |
| 384 | 101.4006 | 102.1657 | **−0.7651** | 1.008 |
| 512 | 133.6635 | 132.8403 | +0.8232 | 0.992 |
| 640 | 166.8863 | 163.8487 | +3.0376 | 0.975 |
| 768 | 200.9587 | 196.3662 | +4.5925 | 0.972 |
| 896 | 235.5473 | 228.5279 | +7.0194 | 0.964 |
| 1024 | 270.7236 | 262.3357 | +8.3879 | 0.963 |
| 1280 | 342.1951 | 329.1058 | +13.0893 | 0.958 |
| 1536 | 414.9150 | 397.0334 | +17.8816 | 0.952 |

(n=512 here is η=2, hence +0.823 rather than Kyber-512's η=3 value +0.543.)

Monotone, roughly linear (≈0.0151 bits per unit n), **sign change between 384 and
512**, no flattening at 1536. Both sides use the same `RC.MATZOV` gate count, so an
unbounded margin in n is an exponent-gap claim. The campaign has never made that
claim and cannot support it from three points; the alternative is systematic drift
of the truncated side. Either way, the inventor-protocol §3 question — *what should
this quantity do as the parameter meant to destroy it increases?* — has an answer
S4 never reached: it should stay bounded, and it does not.

Kyber-512's entire margin (0.543432 bits) is smaller than the margin's own
variation across one 128-step in n, and smaller than its distance to the sign
change. No ordering claim there is supportable.

## 7. NULL-1, run to completion (OBJ-4)

The producer's NULL-1 died on `NoiseDistribution.CenteredBinomial` and was
budget-barred from a rerun, so DEF-7's null goes unrun for a second batch. **I did
not repair the package.** I wrote my own implementation of the design the producer
described (same seed 20260803, same 24-point Kyber-shaped-but-non-Kyber ensemble,
module-level `CenteredBinomial` import) and ran it under real Sage.

```
SUMMARY {"n_requested": 24, "n_evaluated": 24, "n_errors": 0,
         "positive_margin_count": 13, "negative_margin_count": 11,
         "margin_min": -207.036..., "margin_max": 13.162...}
```

**13 of 24 — 0.542, a coin flip** — against NULL-2's 17 of 18 (0.944). The two
nulls are not interchangeable and they disagree, because they remove different
things: NULL-2 varies the reduction frame at fixed Kyber parameters, NULL-1 varies
the parameters at the fixed frame. NULL-2's 0.944 does **not** cover the
Kyber-specificity question.

Reading it honestly cuts both ways. The ordering is *not* a generic property of the
two cost functions — that is real and it argues against a pure-artifact reading.
But the positive cells cluster at large n and the negative at small n, so what
NULL-1 detects is specificity to **large dimension**, not to Kyber. It is §6 seen
through a random ensemble, not a second finding.

On NULL-2's implausible cells: `CheNgu12` and `ABLR21` do not override
`short_vectors`, so they inherit `ReductionCost.short_vectors` (`reduction.py:275`),
the rerandomize+LLL model returning `rho=2.0, cost + N·LLL(d)`. Those six cells
compare an enumeration-priced primal against a dual buying N vectors at LLL prices.
That is a harness category error, not an ordering finding, and they should be struck
rather than counted. Sieve cells only: **11 of 12**.

Spot-checked two NULL-2 cells exactly: `LaaMosPol14`/K-512 = −1.622882 (report
−1.6229); `BDGL16`/K-512 = +0.4093625 (report +0.4094).

## 8. S2, S5, and cross-checks

**S2 β-coverage annotation reproduces exactly.** 8127·14 + 6727·11 = 187,775 and
8127·15 + 3472·19 = 187,873, matching the reported point counts to the unit with
all four remainder checks zero. The producer reconstructed this post-run and it is
sound. Unstated and worth stating: both scanned β bands lie *entirely below* both
incumbents, so a null there is structurally guaranteed — the same failure mode as
the prior 1701-point scan, in a different coordinate.

**S5 c\* reproduces exactly**, all six values, from the stated definition:

- Model A: (143−139.65604148)/89.74352 = 0.03726128; (207−196.36624335)/130.15985 =
  0.08169770; (272−262.33568001)/176.48105 = 0.05476123.
- Model P: /116.09640 = 0.02880329; /130.16111 = 0.08169688; /240.0 = 0.04026800.

**Ownership label checks out.** `EV-MLKEM-020` records `log2 M_peak` 88.494071 /
131.657286 / 180.924993 and c\* 0.03164649 / 0.04588645 / 0.00705473 computed from
`primal_bdd`'s own d4f-reduced SVP dimensions (385.08 / 590.13 / 825.24). So
0.0071 is genuinely `primal_bdd`'s and the refusal to transfer it is correct.

Extra trap for the next reader, not an objection to this package: `matzov`'s Model
A memory uses the reported `beta_` (391/583/804), which is GJ21's *upward*-adjusted
`sieve_dim`, while `EV-MLKEM-020` used *downward* d4f-reduced dimensions. The two
c\* families are in different conventions and must never be differenced.

**Free-memory margins cross-check exactly**: 2.800527+0.543432 = 3.343959,
6.041285+4.592472 = 10.633757, 1.276377+8.387943 = 9.664320.

## 9. Security-claim audit

I read every sentence of `report.md`, `results.json`, `receipt.json`, the snapshot
receipt, and the commit message `1cd863b1` looking for a sentence that reads as a
security claim. **One found**, in the commit message:

> "S4 decays on all three parameter sets under full re-optimisation, so the
> inventor-protocol artifact tell is not triggered."

The premise reproduces. The conclusion is unscoped: S4 tested N-inflation, §6 tests
n and the tell fires. In an immutable commit message this asserts the package
discharged inventor-protocol §3, and it did not. `report.md` is better — its
"What survives" entry names the knob ("does decay under N-inflation") — the commit
message dropped the qualifier. Same class as the BATCH-010 overclaim, smaller.

Two wording faults in `report.md`, below blocking: the S1 heading "the gap is
closed" contradicts ANOM-A in the same document (the known-answer control still
covers `matzov` at **no** parameter set, and the `MATZOV_REFERENCE` block was
"recorded as needed, not made"); and "**are VERIFIED, not unverified**" runs bolded
and unqualified for one sentence before the correct qualification arrives.

Everything else is clean, and unusually so. The non-claim block appears in all five
artifacts, rule 12 is stated UNMET and UNWAIVED throughout, the snapshot receipt's
`scope_note` pre-emptively says S1 leaves the model objection untouched, and S5's
`transfer_prohibition` correctly refuses to move 0.0071 onto `matzov`. This is a
producer that argued against its own result in six places. That is why the verdict
is `blocking_objections` against the *conclusion* and not against the *package*.

## 10. Real, or merely unfalsified?

**Merely unfalsified.** S2, S3 and S4 vary the search box, the reduction frame and
N. All three hold the LWE parameters fixed at the three Kyber sets — none varies
the thing the quantity is a function of. When I varied it, the margin changed sign
128 dimensions below Kyber-512 and then grew without bound. A survivor of three
probes that all fix the one live variable is unfalsified, not corroborated.

## 11. Close or continue

**Close** — and as a completed goal, not `closed_at_budget`.

Not premature, because the closure meets the §4 standard rather than reporting
fatigue. Named obstruction: the instrument cannot answer the question. Every
quantity it produces is a difference of two estimator outputs, one of which drops
an unbounded O() on the term that sets its own block size, and neither of which was
built to be differenced at 0.5-bit resolution. That is a method ceiling and it does
not reach the headline under any tuning. Argument: §5 locates the truncation on the
load-bearing term, §6 shows the resulting quantity has no stable value, §4 shows the
two sides use different bookkeeping. Forward guidance: `KN-OPEN-016`'s actual
question — does the dual-sieve attack work as costed — is untouched by twelve
batches, is **not** closed by this recommendation, and is not reachable through the
estimator at all. It needs the score distribution of sieve-produced dual vectors
measured, which is a different instrument and the right successor goal.

The four controls I name (`CTRL-RT-1`…`CTRL-RT-4`) total under 30 minutes of
compute and none of them can change this. CTRL-RT-2 can only reallocate the margin
between two components that both sit on the truncated side; CTRL-RT-4 is harness
hygiene that should have existed in BATCH-008. They belong in the successor's
setup, not in a thirteenth batch of the same kind.

---

## Reproduction pointers

Scripts I ran live in this session's scratchpad and are **not** research artifacts:
`rt_rederive.py` (§2), `rt_asym.py` (§4–5), `rt_null1.py` (§7), `rt_nsweep.py` (§6).
Each is ~30 lines against `/tmp/le` at `3e48ef4` under `/tmp/sagevenv/bin/python`
with `PYTHONPATH` cleared; §6 and §7 are the two worth rebuilding, and both are
specified precisely enough in `report.yaml` (OBJ-1, OBJ-4) to rewrite from the
description. I did not commit and I wrote nothing outside
`coordination/goals/GOAL-MLKEM-003/batches/BATCH-012/tasks/TASK-20260803-f55e34/`.
