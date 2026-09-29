# Execution report — RUN-RELN-141a86-stage0bcde

Experiment: EXP-RELN-141a86 (frozen, approved, DEC-20260907-93a502).
Handoff: TASK-20260907-a3097e (Stage 0b onward, continuation of
RUN-RELN-141a86-stage0a).

## 1. Stage-0a hash re-verification

Recomputed sha256 over `candidate-list.yaml` + `grammar.yaml` +
`environment.lock.json` (concatenated in that order, no separators) from
`RUN-RELN-141a86-stage0a/`:

```
f1aec620f8cb19318e6d6459174bd79b80daf6dd46fdacf6afdf2468c7cac7f2
```

Identical to `candidate-list-hash.txt` and the value cited in the handoff.
**Match confirmed. Proceeded.**

## 2. Recovery-control table

| Control | Canonical complexity | Numeric verification (real data, zero residual) | Structural blind-search | Gate verdict |
|---|---|---|---|---|
| INV-1 (conservation mean) | 9 | EXACT (144/144 real committed FB3 cells) | resource_exhaustion (6-leaf pack, complexity 9 not reached) | **NOT AFFIRMATIVELY RECOVERED** |
| INV-7 (x-class m=2, p_fail/p_exist) | 9 / 11 | EXACT (15/15; both p_fail and p_exist) | resource_exhaustion (complexity 9 not reached; complexity 11 not attempted) | **NOT AFFIRMATIVELY RECOVERED** |
| INV-8 (semiregular degree) | 10 | EXACT (549/549, independent integer convolution) | resource_exhaustion (4-leaf pack, complexity 10 not reached) | **NOT AFFIRMATIVELY RECOVERED** |
| INV-A4 (Sidon floor, Bose-Chowla) | 7 / 3 | EXACT (4/4 q values, real GF(q^3) construction) | **COMPLETED — found**, exact string match at both complexities | **PASS** |
| INV-A6 (convention identity) | 7 | EXACT (572/572 real committed FB3 cells) | **COMPLETED — found**, algebraically-equivalent representative at complexity 7 | **PASS** |

Full detail, tables and the exact search-termination measurements are in
`recovery-controls.json` and `implementation.md`.

**Why structural search failed to complete for INV-1/INV-7/INV-8:**
the frozen exhaustive-grammar engine's enumerated-candidate-set size grows
~6-8x per complexity level (measured directly, not estimated — e.g. the
6-leaf `enum_zn_and_sidon` pack reaches 427,569 canonical forms already at
complexity 7, in 251.6s). Reaching complexity 9-11 for the 6-leaf packs
(INV-1, INV-7) or complexity 10 for the 4-leaf pack (INV-8) requires
enumerated-candidate counts estimated in the tens of millions, which
exceeded this host's 15GB total RAM (measured, `free -h`) before
completing, even after two real implementation bugs were found and fixed
(see below). Three real, timed subprocess jobs were launched, monitored via
`ps`/`free`, and terminated (SIGKILL) by the executor's own
resource-protection judgment after 9-13 minutes each, at 1.5-5.4GB resident
memory, well short of their target complexity, to avoid an uncontrolled
host OOM. This is `failed_infrastructure` / `resource_exhaustion` for the
structural-search portion of those three controls specifically, **never
a negative or positive scientific result**, per the contract's own
`invalidation_rules`.

## 3. Two real implementation bugs found and fixed in `grammar_engine.py`

1. **Pow/binomial magnitude blow-up during fingerprinting** could hang
   indefinitely on a tower-exponential intermediate value (and, separately,
   crashed on `complex` results from a non-integer power of a negative
   base). Fixed with a magnitude cap (domain-invalid → `None`, same
   convention as division-by-zero) and a proper domain check. This never
   changes node counts or the grammar's semantics — only prevents the
   dedup pass from hanging.
2. **Every CONST leaf in a tree shared ONE fingerprint value** (`CONST=1`
   for all occurrences), which is unsound for expressions with two
   independent free constants (explicitly permitted by the frozen
   `constant_fitting` clause). This **silently discarded the true INV-A4
   coverage law**, `div(binomial(add(B,CONST),CONST),N)`, from the
   enumerated candidate set before the fix — confirmed empirically, not
   theoretically. Fixed by assigning each CONST occurrence its own
   distinct integer fingerprint value; re-verified INV-A4's coverage and
   Delta laws are now both present at their canonical complexities.

Full detail in `implementation.md`. Both fixes are disclosed, minimal,
scoped to the fingerprinting/dedup pass only, and change no frozen grammar,
node-counting rule, or threshold.

## 4. Positive controls

- **Z/N interval ("proves too much")**: PASS. Real, exact, deterministic
  enumeration (no sampling) of the interval base `[1..B]` at the three FB3
  rungs. Measured Delta = 210 / 515 / 1275 at 2^14/2^16/2^18, vs INV-A1's
  prediction of ≈0.99 in every case — not remotely within tolerance.
  `Delta/B^2` is approximately constant (0.093–0.095) across rungs and
  `E_3/B^5` is approximately constant (0.016–0.017), directly confirming
  the contract's predicted `B^2` / `B^5` growth signature and clear
  non-equivalence to INV-A1.
- **Small-multiples decay ladder**: PARTIAL. The q=0 point (pure
  small-multiples base, read directly from the already-committed FB3
  `exploratory[]` arrays, no new computation) confirms concentration ratio
  188x / 480x / 1224x at 2^14/2^16/2^18 — matches the contract's own cited
  values exactly and is clearly not INV-A1. The full decay ladder
  (q ∈ {0.25, 0.5, 0.75, 1}) needs own-enumeration (Stage 0e), not built
  in this dispatch (scoped out per the handoff's priority order); its
  monotonicity-to-zero-at-q=1 claim is **untested**.

## 5. Stage 0d — P2 zero-compute check

Used ONLY the already-committed FB3 `metrics.<stat>.null_detail` values
(no new data). Discovered during implementation that the raw per-draw
`null_sd` field is the wrong quantity for this comparison (it measures
cell-vs-null-distribution spread, not the precision of the null MEAN
estimate); the correct SE is the curve-cluster standard error of the mean
over the 16 genuinely independent `(curve_index, rep_seed)` draws per
rung (the FB3 null draws are literally SHARED across the three untyped
geometries — confirmed by direct value comparison). See
`implementation.md` section 6 for the full derivation.

| Rung | Delta_null (mean) | curve-cluster SE | vs INV-A1 | vs trivial (1-1/N) |
|---|---|---|---|---|
| 2^14 | 0.99139 | 0.000407 | 0.39 SE (within 3 SE) | 21.00 SE (**> 10 SE, matches prediction**) |
| 2^16 | 0.99680 | 0.000332 | 0.42 SE (within 3 SE) | 9.59 SE |
| 2^18 | 0.99873 | 0.000175 | 0.30 SE (within 3 SE) | 7.27 SE |

**PASS at both stated checkpoints**: agrees with INV-A1 within 3 SE at
2^14 and 2^16 (and 2^18), and rejects the trivial `1-1/N` prediction by
>10 SE at 2^14 (measured 21.0 SE) — this exact quantitative match to the
contract's own pre-stated ">10 SE at 2^14" prediction is strong internal
cross-validation that the curve-cluster SE convention is correct.

## 6. DREG series transcription (P6, prediction only)

| n_vars | rank | sr_pred | deficit | source |
|---|---|---|---|---|
| 12 | 28,096 | 29,418 | 1,322 | ledger/EV-DREG-001.yaml lines 16-17 |
| 15 | 69,073 | 70,935 | 1,862 | ledger/EV-DREG-001.yaml lines 19-20 |
| 17 | 125,099 | 126,922 | 1,823 | ledger/EV-DREG-002.yaml lines 14-15 |
| 18 | 143,882 | 145,881 | 1,999 | ledger/EV-DREG-001.yaml lines 24-26 |

Prediction target only, per the contract; not fitted or scored in this
experiment.

## 7. Sibling data source usage

`EXP-RELN-f202be` was **not consulted** — not needed at Stage 0b-0d, which
uses only committed FB3 cells, own-computed closed-form tables (INV-7 x-class,
INV-8 convolution, INV-A4 Bose-Chowla), and own exact deterministic
enumeration (Z/N interval control). Would be consulted at Stage 1 open,
which was not reached. `EXP-RELN-82f487`'s predictor tables were not
consulted (explicitly optional; Stage 1 not reached).

## 8. Overall Stage-0c hard-gate verdict

**NOT PASSED.** Per specification.yaml's `success_criterion` clause (1),
ALL FIVE recovery controls must show `recovered on the primary engine at
or below its canonical node count with zero residual`. Two (INV-A4,
INV-A6) meet this fully. Three (INV-1, INV-7, INV-8) have exact numeric
identity but **undetermined** blind structural recoverability, due to
measured, real `resource_exhaustion` of the reference exhaustive-grammar
engine implementation on this host — not a scientific negative, and not
grounds for a "not recovered" verdict either (the search never completed,
so it never definitively failed to find the target). Per the contract's
own `stopping_rules` ("Stop at the end of Stage 0c if any recovery
control is not recovered on the primary engine ... instrument failure,
Stage 1 does not run"), **Stage 1 was NOT run.** This is treated as an
instrument-limitation finding under `decision_paths.negative` in spirit
(hypothesis stays untested), though it is more precisely "incomplete"
than "failed": a successor dispatch with either (a) a memory-efficient
streaming/on-disk implementation of the exhaustive enumeration, or (b) a
larger-memory host, could complete the same, unmodified, frozen search and
resolve INV-1/INV-7/INV-8 definitively.

## 9. Wall-clock spent

Approximately 40 minutes of interactive session wall-clock time,
including: hash re-verification, five new source modules
(count_vectors.py, controls_m2_exhaustive_and_convolution.py,
adapters_fb3_dreg_enum.py, recovery_check.py, structural_presence.py; ~700
lines total), two grammar_engine.py bugfixes discovered and fixed through
direct empirical debugging, real exact computation of all five control
tables and two positive controls, and ~13 minutes of real, monitored
background CPU/memory use on the three exhaustive-search jobs (two
terminated at ~9 min, one at ~13 min) before their resource-exhaustion
termination.
