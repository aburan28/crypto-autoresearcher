# EXP-PFDR-4bfc6f -- analysis.md (TASK-20260903-3a77d3)

Scope disclosure first (see `implementation.md` section 9.4 for the full
list): this analysis covers ONLY the work actually executed in this
dispatch -- one curve (structured 13-bit, `p=4111`, `a=-3`), the e-ring
representation, `|FB|` in `{4,5,6,7,8}`, seed 42, no targets, no weighted
grading, no POS-C. It is NOT the full contract battery (3 curves x 3 primes
x 3 representations x targets x 5 null seeds x 2 gradings). Every table
below is scoped accordingly; nothing here should be read as covering cells
this dispatch did not measure.

## 1. Reproduction table (CTRL-ARCHIVE-REPRODUCTION, e-ring only, 2/16 cells)

| |FB| | profile (measured) | profile (archived) | d_ff (measured) | d_ff (archived) | D_reg (measured) | D_reg (archived) | match |
|---|---|---|---|---|---|---|---|---|
| 4 | [2,2,2,4] | [2,2,2,4] | 3 | 3 | 4 | 4 | YES |
| 5 | [3,3,3,4] | [3,3,3,4] | 4 | 4 | 5 | 5 | YES |

2 of 2 measured cells reproduce integer for integer on the reconstructed
inline meter. **14 e-ring cells, 16 power-sum cells, 16 x-ring cells are
NOT independently reproduced in this dispatch** (cited from the archive in
`stage0-derivation.md` part 4 only).

## 2. Meter agreement table (CTRL-METER-CROSSCHECK)

| |FB| | arm | inline d_ff | F_p-port d_ff (normalised, see note) | D_reg | fires | shrink | agree |
|---|---|---|---|---|---|---|---|---|
| 4 | semaev | 3 | 3 | 4 | True | 0/0 | YES |
| 4 | null_s4 | 3 | 3 | 4 | True | -- | YES |
| 4 | null_fb | 4 | 4 | 4 | False | -- | YES |
| 4 | generic_twin | 4 | 4 | 4 | False | -- | YES |
| 5 | semaev | 4 | 4 | 5 | True | 0/0 | YES |
| 5 | null_s4 | 4 | 4 | 5 | True | -- | YES |
| 5 | null_fb | 5 | 5 | 5 | False | -- | YES |
| 5 | generic_twin | 5 | 5 | 5 | False | -- | YES |
| 6 | semaev | 5 | 5 | 7 | True | 0/0 | YES |
| 6 | null_s4 | 5 | 5 | 7 | True | -- | YES |
| 6 | null_fb | 7 | 7 | 7 | False | -- | YES |
| 6 | generic_twin | 7 | 7 | 7 | False | -- | YES |
| 7 | semaev | 6 | 6 | 8 | True | 0/0 | YES |
| 7 | null_s4 | 6 | 6 | 8 | True | -- | YES |
| 7 | null_fb | 8 | 8 | 8 | False | -- | YES |
| 7 | generic_twin | 8 | 8 | 8 | False | -- | YES |
| 8 | semaev | 7 | 7 | 10 | True | 0/0 | YES |
| 8 | null_s4 | 7 | 7 | 10 | True | -- | YES |
| 8 | null_fb | 10 | 10 | 10 | False | -- | YES |
| 8 | generic_twin | 10 | 10 | 10 | False | -- | YES |

20/20 agree. **Convention note (disclosed, see `implementation.md` 9.3
item 9):** the inline meter defaults `d_ff = D_reg` when no fall is found;
the F_p port's `first_nontrivial_syzygy` returns `None` in that case. Both
report the same `fires` bit and `D_reg` unconditionally; the "F_p-port
d_ff" column above substitutes `D_reg` for `None` to make the table
readable, exactly as the raw agreement check in `stage1_fp_crosscheck.py`
does (disclosed there, not silently patched).

POS-A/NEG-1/NEG-2 cross-check: inline meter (this dispatch) POS-A
`d_ff=4,D_reg=7,fires=True`; NEG-1 `d_ff=4,D_reg=4,fires=False`; NEG-2
`d_ff=7,D_reg=7,fires=False`. F_p port: identical values, already
documented at `harness/macaulay_fp/VALIDATION.md` section 8 and
`tests/test_macaulay_fp.py::test_localization_gate_reproduces_alpf013_controls`
(cited, not re-run by this dispatch's own script, since the F_p port's own
test suite already covers this exact control and the values match this
dispatch's independent Sage-side measurement).

## 3. Ladder table, e-ring arm, one curve (p=4111, structured, a=-3)

| |FB| (k) | predicted d_ff = k-1 | measured d_ff | predicted D_reg | measured D_reg | shrink test | gap D_reg-d_ff |
|---|---|---|---|---|---|---|---|
| 4 | 3 | 3 | 4 | 4 | 0 | 1 |
| 5 | 4 | 4 | 5 | 5 | 0 | 1 |
| 6 | 5 | 5 | 7 | 7 | 0 | 2 |
| 7 | 6 | 6 | 8 | 8 | 0 | 2 |
| 8 | 7 | 7 | 10 | 10 | 0 | 3 |

Every predicted value matches measured with zero deviation across the full
`|FB| in {4..8}` range on this one curve. Gap grows `1,1,2,2,3` (matches the
predicted decay-ladder signature of H-PFDR-e02f3b.mechanism, "the gap D_reg
- d_ff grows with |FB| ... 1, 1, 2, 2, 3 at |FB| = 4..8").

## 4. Null tables

**NULL-S4** (S4 top form replaced by a random degree-4 polynomial in
`e1,e2,e3`, same membership generators): `d_ff`, `D_reg`, `fires` identical
to the Semaev arm at every `|FB|` in `{4..8}` on both meters. Matches P3's
FORCED prediction under M2 exactly. **Single seed (42) only** -- the
contract's 5-seed battery `{7,11,13,17,19}` was not run.

**NULL-FB** (S4sym kept genuine, membership constraints replaced by random
polynomials of the same degree profile): no fire (`d_ff = D_reg`) at every
`|FB|` in `{4..8}` on both meters. Matches P4's FORCED prediction exactly
(no F4 signature). **Single seed (42) only**, same gap as NULL-S4.

**CTRL-GENERIC-TWIN** (all four generators replaced by random polynomials
of the measured profile): no fire at every `|FB|`, matching the archive's
own Discriminator-1 finding exactly.

## 5. Weighted-grading arm

**NOT RUN.** No cell in this dispatch used `deg e_i = i`; only the standard
grading `deg e_i = 1` was measured.

## 6. Unit-ideal table

**NOT RUN.** No planted or random target was drawn; CTRL-TARGET-ARM, Q1,
and the 200-random-target unit-ideal enumeration were not attempted in this
dispatch. HEUR-001's falsification condition is untested here.

## 7. Classification per archived arm, by the pre-registered signatures

Signature definitions (`stage0-predictions.yaml`, verbatim from
H-PFDR-e02f3b): M1 = shrink test strictly positive AND null does not fire;
M2 = `d_ff = |FB|-1`, shrink test zero, null fires identically; M3/M4 are
about Q1/the reduced basis, not measured here.

**E-ring arm (EXP-ALPF-011, the arm this dispatch actually measured):** at
every `|FB|` in `{4..8}` on the one curve measured, `d_ff = |FB|-1` exactly,
shrink test `= 0` exactly, NULL-S4 fires identically to the Semaev arm.
**This is the M2 signature, matching the pre-registered prediction with
zero deviation, at every cell this dispatch measured.** No F1 (archive
mismatch), F2 (P1 failure), F3 (shrink positive), or F4 (NULL-FB fires)
condition was observed anywhere in this dispatch's scope. This is an
OBSERVATION about the cells actually measured (1 curve, e-ring only,
`|FB| 4-8`, seed 42); it is NOT a claim about the power-sum arm, the x-ring
arm, the other two curves/primes, or the null seeds not run, all of which
remain to be measured. Per the executor's authority (AGENTS.md,
`agents/executor.md`), this is reported as observation only; whether this
constitutes sufficient evidence to classify the archived signal, and what
it means for H-PFDR-e02f3b or EV-ALPF-001, is left to Coordinator-directed
independent review (validator, red-team), not decided here.

**Power-sum arm, x-ring arm, `m=2` symmetric arm (EXP-ALPF-001):** not
independently measured by this dispatch; no classification is offered
beyond citing the archive's own text (`stage0-derivation.md` part 4-5).

## 8. Tail checks

Not performed: this dispatch made no statistical claim requiring a tail
check (no target enumeration, no binomial-interval comparison against
HEUR-001 was run).

## 9. Verdict against the frozen criteria, as observation

`stage0-predictions.yaml`'s P1-P4 all match measured values with zero
deviation across `|FB| in {4..8}` on the one (curve, p) cell this dispatch
measured, on both meters. P5 (Q1) is untested. The escape clauses for F3
(shrink positive) and F4 (NULL-FB fires) did not trigger anywhere in this
dispatch's scope. This is stated as an observation restricted to the
measured scope (`implementation.md` section 9.4); it is not a claim about
H-PFDR-e02f3b's full test_boundary (3 curves, 3 primes, both arms, targets,
5 null seeds), which remains substantially unmeasured by this dispatch.
