# INDEPENDENT PRECONDITION CHECK - TASK-20260906-28e6de

GOAL-SSI-001, BATCH-1fa3fb. Role: validator (review-adversarial, xhigh).
This is my own working record. A successor can re-check every conclusion here
against committed bytes without re-running anything, except where noted.

**ANTI-LEAK.** Nothing read from `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`
lines 234-238 appears in this file - not transcribed, paraphrased, rounded,
ordered, bucketed, ranged, compared or unit-converted. The field size 512
appears only as the published locator label and never adjacent to anything read
out of the block. I ran my own digit scan over my own three artifacts and it
found no governed numeric content (see validation_report.yaml
`citation_prohibition.did_either_limb_fire_on_my_own_report`).

---

## 1. ATTESTED ORDERING (J5)

I produced my own OBJ-A, OBJ-B, OBJ-C and OBJ-E results, and my own J3 and J4
answers, **BEFORE** opening the P-2 (TASK-20260906-6c5e0a) and P-3
(TASK-20260906-decbd5) producers' own control sections. I recorded them
durably in a scratch file outside the repository
(`/Volumes/SSD990/llm/tmp/opencode/ssi-review/my_own_results_BEFORE_producers.md`)
before opening those sections. I then opened the producers' control sections
and compared. **I did the attested ordering.**

For OBJ-D the ordering is structurally different: I had to read the P-1 ruling
(TASK-20260906-6afb30/rt4_licensing_ruling.yaml) in full first, to learn which
counterfactual artifact it names. I then opened that artifact
(DEC-20260905-3b8e94.yaml) and checked that it bears. This is the ordering the
card anticipates ("the reviewer must read the ruling to know what to open").

My scratch scripts (`mechanical_checks.py`, `digit_scan.py`,
`digit_runs_by_value.py`) live outside the repository and are archived by
nothing. They are not reproducible from this package. What IS reproducible is
the procedure as described here, together with the recorded digests and counts.

---

## 2. MY OWN OBJ-A (J3) - THE KNOWN-ABSENT KEY PATHS

Object: `coordination/goals/GOAL-SSI-001/batches/BATCH-2e6130/tasks/TASK-20260809-ef3e58/protocol_amendment.yaml`,
opened at the file itself.

Procedure: `yaml.safe_load`, then a walk descending the exact named segments in
order, reporting an ABSENT sentinel the moment a segment is missing from a
mapping; plus an independent raw-text search counting occurrences of each key
token. The SAME procedure applied to the real key paths and to the probes.

My results (produced before reading P-2's answers):

| key path | my result |
|---|---|
| `amendment.corrected_model.log2_law` | PRESENT |
| `amendment.corrected_model.endpoint_behavior` | PRESENT |
| `amendment.corrected_model.crossover` | PRESENT |
| `amendment.corrected_model.log_two_law_restated` (probe) | ABSENT |
| `amendment.corrected_model.sign_convention` (probe) | ABSENT |
| `amendment.corrected_model.invariants` (probe) | ABSENT |
| `amendment.status` | PRESENT, value `prospective_and_frozen` |
| `amendment.in_force` | ABSENT (0 keys containing `force` anywhere under `amendment`) |

The control discriminated in both directions: PRESENT on the three real paths,
ABSENT on the three probes and on `in_force`. Clean.

**Comparison with P-2:** P-2's part (a) and part (b) report exactly these
facts. **No difference.**

---

## 3. MY OWN J3 INVARIANT ANSWERS (FORM QUESTIONS, NOTHING EVALUATED)

Checked against the record's own text, the redraft's clause_2 invariants, and
the contract's own C3/C4 controls (`experiments/EXP-WESOVOW-001/specification.yaml`,
read-only). No field size substituted, no number evaluated, no sign computed.

- **Invariant 1 (C3: T(w) non-increasing in w for every (p, overhead); T(w) =
  T_full for w >= M).** The record's stated `log2_law` is non-increasing in w
  BY FORM (the clamped shortfall term is non-increasing in w; the overhead term
  is constant in w). The record states the w >= M endpoint in words
  (`endpoint_behavior.w_above_M`: the high-memory cap is flat). It states
  monotonicity as a required control, not as a proven property. Form: the
  record states both limbs; whether the stated law satisfies the control as a
  mathematical matter is NOT answered (that would be an evaluation).
- **Invariant 2 (C4: T(M) = T_full exactly, before the declared overhead
  multiplier).** The record states `endpoint_behavior.w_equals_M` =
  "T(M) = T_full before overhead", which matches the invariant AS WRITTEN,
  including the "before ... overhead" qualifier. RT-6 (whether that qualifier
  belongs, given C4's own text lacks it) is RESERVED and is NOT settled by me
  or by P-2.
- **Invariant 3 (the crossover must be the crossover OF THAT SAME LAW).** The
  record's `crossover.equation` is the algebraic solution of its own
  `log2_law` set equal to the baseline `log2(T_DG)` on the non-flat branch. I
  verified this as an identity of form (symbolic rearrangement, substituting
  nothing), not by evaluating at any field size. Form: satisfied under the
  reading that the overhead is inside the law; P-2 additionally notes the
  invariant's own equation, read literally, would carry the overhead term
  twice, and leaves the arbitration reserved.

**Comparison with P-2:** P-2's part (c) answers the same three the same way,
with the same form-level qualifier differences recorded and the same refusal to
evaluate. **No difference in substance.** P-2's two-reading split on invariant
3 is the honest shape of the answer and I reach the same split.

---

## 4. MY OWN J4 HALF ONE (THE LOCATOR, READ-ONLY)

Object: `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, opened READ-ONLY at
lines 234-238 (for my own S1-S7) and lines 1-5 (for OBJ-B) and a past-end range
(for OBJ-C). No other range opened. No content recorded here.

My resolution facts (commands emit only the digest or the count):

| fact | my result |
|---|---|
| file exists | True |
| total line count | 350 |
| lines 234-238 exist | True |
| lines 234-238 all non-empty | True |
| block byte length (incl. line terminators) | 802 |
| block byte length (trailing EOL stripped) | 801 |
| block_sha256 (exact bytes incl. trailing EOL) | `4ef80d2559c74acfb5749516cfe4c9e521b8f36b4aae8552913541c1a32c4668` |
| block_sha256 (trailing EOL stripped) | `4fb5ceaa5f8ed87b22839b79191374df2b901bac7cda035b376438fde666b5e9` |
| whole_file_sha256 | `ca34a0f784351992df72458b2410ed92a137a1811d5401a24810121116c7a9cf` |

My own S1-S7 (booleans and counts only; no governed content):

| predicate | my answer |
|---|---|
| S1 (five contiguous lines) | TRUE |
| S2 (tabular per-field-size listing, not running prose) | TRUE |
| S3 (rows carrying a field-size key) | 5 |
| S4 (a row keyed to the field size the records call P=512 is present) | TRUE (presence boolean, never the row's contents) |
| S5 (value columns per row) | 2 |
| S6 (block states IN WORDS that figures are lower bounds / from an underestimation) | FALSE |
| S7 (the location a reader of clause_3 `what_the_five_pairs_are` reaches for the five pairs) | TRUE |

**Digest comparison with P-3:** P-3 recorded block_sha256
`4ef80d2559c74acfb5749516cfe4c9e521b8f36b4aae8552913541c1a32c4668` and
whole_file_sha256 `ca34a0f784351992df72458b2410ed92a137a1811d5401a24810121116c7a9cf`.
**BOTH MATCH my independent recomputation exactly.** A digest mismatch would
have been a STOP; there is none.

**Comparison with P-3's S1-S7:** P-3's answers are S1 TRUE, S2 TRUE, S3 5,
S4 TRUE, S5 2, S6 FALSE, S7 TRUE. **All seven match mine.**

---

## 5. MY OWN OBJ-B (J4) - THE WRONG-SHAPE RANGE

The predicate list S1-S7 applied UNCHANGED to lines 1-5 of the same file (the
document head). I verified with a boolean-only command that lines 1-5 are:
line 1 non-empty, line 2 EMPTY, line 3 non-empty, line 4 EMPTY, line 5
non-empty.

My results:

| predicate | my answer |
|---|---|
| S1 (five contiguous lines) | **TRUE** (lines 1-5 exist and are a contiguous run of exactly five lines) |
| S2 (tabular per-field-size listing) | **FALSE** (the document head is a title/author/note, not a row listing) |
| S3 (rows carrying a field-size key) | 0 |
| S4 (a row keyed to the field size the records call P=512) | FALSE |
| S5 (value columns per row) | 0 |
| S6 (lower-bound characterization in words) | FALSE |
| S7 (the location a reader reaches for the five pairs) | FALSE |

The required outcome - **S2 MUST come out FALSE** - is satisfied. The shape
predicate is not vacuous.

**Comparison with P-3's OBJ-B:** P-3 reported S1 **FALSE** (on the ground that
"not every line of that range carries non-whitespace content"), S2 FALSE, S3 0,
S4 FALSE, S5 0, S6 FALSE, S7 FALSE. **The one difference is S1: mine is TRUE,
P-3's is FALSE.** The S1 predicate as written on P-3's card is "The block is a
contiguous run of exactly five lines. TRUE or FALSE." - a structural fact about
the range, with no non-emptiness condition. Lines 1-5 satisfy that as written,
so the predicate as written is TRUE. P-3's FALSE rests on a non-emptiness
condition the predicate does not state. This does not affect the control's
discriminating power (the required outcome is S2 FALSE, which matches), but it
is a concrete finding about P-3's predicate interpretation, recorded here and in
validation_report.yaml J4-F2. It is a NEW finding no committed record has raised.

---

## 6. MY OWN OBJ-C (J4) - THE NON-RESOLVING LOCATOR

The resolution procedure applied to a line range of the same file beyond its
end, chosen from my own measured line count (350). I chose lines 360-364 (a
five-line range starting ten lines past the measured last line, so the whole
range lies beyond the end of the file).

My result: **DOES NOT RESOLVE** (the range does not resolve; the procedure
halts before any extraction, digest or predicate step). As required.

**Comparison with P-3's OBJ-C:** P-3 chose lines 361-365 (a five-line range
starting eleven lines past the measured last line) and also got **DOES NOT
RESOLVE**. **No substantive difference** - both ranges are entirely past the
end and both return DOES NOT RESOLVE.

---

## 7. MY OWN OBJ-E (J4) - THE LEAK-SCAN POSITIVE CONTROL

I exercised my digit scan on the synthetic string `SYNTHETIC-LEAK-PROBE
1234.5678`, written OUTSIDE the repository
(`/Volumes/SSD990/llm/tmp/opencode/ssi-review/synthetic_probe.txt`). The string
has no relation to any campaign quantity, anchor, crossover or margin.

My result: the scan **FIRED** - it found two digit runs (`1234`, `5678`), both
unclassifiable into the closed list, i.e. a leak. As required. A scan that
stayed silent on a plainly leaking string would not be a scan.

**Comparison with P-2's and P-3's OBJ-E:** both reported the scan FIRED on the
synthetic probe. **No difference.**

---

## 8. MY OWN J4 HALF TWO - THE DIGIT SCAN OVER THE P-2 AND P-3 ARTIFACTS

I re-ran the digit scan myself over ALL SIX P-2 and P-3 artifacts
(`digit_runs_by_value.py`, run with `PYTHONDONTWRITEBYTECODE=1`): 852 digit
runs in total. I classified every run. Every run is accounted for by a
declared, checkable rule:

- **Identifiers:** task, batch, goal, experiment, decision, correction, run and
  commit identifiers; the numbered finding labels (RT, CF, AF, F, F-J, IMP, PD,
  NA); the predicate names (S1-S7); the precondition names (P1-P8); the control
  names (C1-C4); the clause key names; the hash algorithm name (`sha256`); the
  interpreter name (`python3`); the model identifiers; the git branch and
  revision names; the function name `log2`; the frozen source directory name.
- **Dates:** calendar dates in year-month-day form and the UTC timestamp
  components.
- **Line numbers:** the locator bounds (234, 238), the OBJ-C past-end range
  bounds, and the in-artifact line and column numbers in the scan enumerations.
- **Digest fragments:** the two 64-hex sha256 values, broken into digit runs by
  their hex letters.
- **Counts that S3 or S5 requires:** the S3 answer (5) and the S5 answer (2)
  and their control-object counterparts (0).
- **The published locator label (512) and the sign-label numerals:** these sit
  only inside the restated prohibition and the S4 predicate text, each checked
  against its committed source, and are never adjacent to anything read out of
  the block.
- **Resolution facts:** the total line count (350) and the block byte length
  (802) - facts about a file, not values of a table.
- **Budget parameters, exit codes, formula constants:** the authorized wall
  clock, the exit code 0, and the numeric constants internal to the
  verbatim-quoted `log2_law` (P-2 only).

**NONE of the 852 runs is content of the governed block.** No operations count,
no memory bound, no exponent, no ratio, no ordering, no comparison, no unit
conversion. **NO LEAK.**

I also checked the subtler leaks a digit scan cannot see - a value described in
words, an ordering or comparison between rows, a range or bucket, a unit
conversion, a statement of which row is largest, and any sentence placing the
label 512 next to something read out of the block - and found none.

**The control-plane defect:** the batch's closed classification list (a line
number, an identifier, a date, a version, a count that S3 or S5 requires, or a
digest fragment) cannot name several of the categories above (the published
locator label, the resolution facts, the formula constants, the budget
parameters, the exit codes, the column numbers, the scan tallies, the timestamp
components). This is the same defect both producers identified: P-2 declared a
STOP on it; P-3 declared no STOP. My judgment: the STOP condition's premise
(that a digit run that does not classify is a leak) does not hold here, because
none of the unclassifiable runs is a leak. The defect is real but it is a defect
of the list, not of the artifacts, and it is not negative mathematical
evidence. I report it and leave the disposition to the Coordinator.

---

## 9. MY OWN J2 - ANCHORING AND OBJ-D

I opened every key path the P-1 ruling rests on and read the bytes, never
through the ruling's quotations:

- **R1** (red-team report `r4.c.finding_RT_4`): "SMALLER REPAIR: carry the two
  provisos into clause_4's own text; it is about two lines." - PRESENT (lines
  848-849, matching after whitespace normalisation).
- **R2** (DEC-20260905-3b8e94 RT-4 disposition): "Two lines of redraft, or an
  explicit ruling in the enacting decision that the provisos travel." - PRESENT
  (lines 147-152).
- **R3** (redraft clause_4 `licensing` and `licensing_provisos_are_operative`):
  PRESENT (lines 553-574).
- **R4** (BATCH-752ef2 `analysis.licensing`): the block is present (line 223
  onward); the two conditions the ruling names are the only two licence items in
  the block that carry conditions, and both are carried in clause_4's own text.
- **R5** (redraft clause_4 `fuller_statement`): "a reader who never opens the
  pointer is not missing a condition." - PRESENT (lines 575-581).
- **R6** (DEC-20260906-f709b2 `must_be_resolved_in_the_enacting_decision`):
  "RT-4's LICENSING QUESTION, STANDING AND UNCHANGED." - PRESENT (lines
  333-337).

**No proposition's key path is missing its quoted words. No BREAK.**

**One minor inaccuracy (J2-F2):** the ruling's R4 says the analysis's reachable
block "forecloses three further things which clause_4 does not restate in those
words." I checked at the file: the reachable block forecloses FOUR items
(reading reachable as agreement; as validation; any transfer of the status;
exemption from the standing citation prohibition), NONE of which clause_4
restates. So the count is four, not three. This is a counting inaccuracy in R4's
supporting enumeration, not in its operative proposition (that no CONDITION on a
licence is absent from clause_4, which is true), and it does not affect the
ruling's position or the OBJ-D counterfactual.

**OBJ-D:** the ruling's primary counterfactual is DEC-20260905-3b8e94's RT-4
disposition, which states two sufficient dispositions disjunctively. I opened
that artifact and asked whether a different reading would have forced the other
position: had the disposition named ONE sufficient disposition that included a
relocation (rather than the disjunction), the redraft's two lines of carrying
would not have answered RT-4 and POSITION 2 would follow. The ruling turns on
the disjunction and the word "or"; change that and the ruling changes. **The
counterfactual bears. It is not decorative.** The secondary (BATCH-752ef2
`analysis.licensing`) and tertiary (redraft `constraint_compliance.constraint_iii`)
counterfactuals also bear.

---

## 10. MY OWN J5 - CONTAINMENT SEPARATION (A REVIEWER JOINT, NOT A TOOL RESULT)

I read the P-2 agent's declared `sources_read` and confirmed it contains
**NOTHING under inputs/**. I read the P-3 agent's declared `sources_read` and
confirmed it contains **NEITHER the BATCH-2e6130 record NOR cost_model.py NOR
BATCH-256a94's anchor_reconciliation.json** (all three are in its
`sources_deliberately_not_read`). **NO BREACH.**

I say plainly, as the card requires: this is a reviewer joint and not a tool
result, and it is WEAKER than a mechanical `blind_from` comparison, because it
rests on the producers' honest declaration of `sources_read` rather than on a
tool-enforced check.

---

## 11. SUMMARY OF WHERE MY CONTROLS DIFFER FROM THE PRODUCERS'

| control | mine | producer's | difference |
|---|---|---|---|
| OBJ-A (J3) | 3 real paths PRESENT, 3 probes ABSENT, status present, in_force ABSENT | P-2: identical | none |
| OBJ-B S2 (J4) | FALSE | P-3: FALSE | none (the required outcome) |
| OBJ-B S1 (J4) | TRUE (predicate as written) | P-3: FALSE (stricter reading) | **one difference - see section 5** |
| OBJ-C (J4) | DOES NOT RESOLVE (lines 360-364) | P-3: DOES NOT RESOLVE (lines 361-365) | none substantive |
| OBJ-E (J4) | FIRED | P-2 and P-3: FIRED | none |
| digests (J4) | block + whole-file, both recomputed | P-3: recorded | **both match exactly** |
| S1-S7 real block (J4) | TRUE, TRUE, 5, TRUE, 2, FALSE, TRUE | P-3: identical | none |

The single difference - the OBJ-B S1 discrepancy - is a NEW finding no
committed record has raised, and it does not affect the control's discriminating
power (the required outcome S2 FALSE matches).
