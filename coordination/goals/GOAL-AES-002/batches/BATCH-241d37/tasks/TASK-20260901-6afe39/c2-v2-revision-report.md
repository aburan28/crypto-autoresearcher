# TASK-20260901-6afe39 — C2 paired-validation design, v2 revision report

**Goal** GOAL-AES-002 · **Question** RQ-AES-002 · **Batch** BATCH-241d37 ·
**Role** idea-generator · **Requested policy** `research-deep`, effort `high`,
`fallback_allowed: false`, `degraded_allowed: false` · **Model that actually
answered** `claude-opus-5` (genuine self-report from this session's runtime
context; unverified from inside, no fallback used, no downgrade accepted).

**Deliverable superseded (NOT edited):**
`coordination/goals/GOAL-AES-002/batches/BATCH-286bcd/tasks/TASK-20260901-354ef5/c2-paired-validation-design.yaml`

**Superseding deliverable:**
`coordination/goals/GOAL-AES-002/batches/BATCH-241d37/tasks/TASK-20260901-6afe39/c2-paired-validation-design-v2.yaml`

**Standing disclosures, up front.** This report and the v2 design state **no
margin**, make **no comparison against the published state of the art in
either direction** (SC-6), and **assert nothing about AES at any round count**
(SC-8). Nothing was approved, dispatched or executed; **no EXP-\* and no H-\***
identifier was minted. `approved`, `dispatched`, `executed` and `compute_run`
are all `false` in v2's `not_yet_approved_not_yet_executed_statement`, carried
forward from v1. **Zero compute** was run: no benchmark, no sample draw, no AES
evaluation, no statistical replicate. The only network act in this session was
a clock read, disclosed in §7.

---

## 1. DEFECT 1 — the seed policy contradicted ARM-NULL's own claim

### 1.1 The v1 text replaced, verbatim

From `experiment.inputs`:

```yaml
    seed_policy: >-
      Deterministic, reproducible, and fully specified so no executor
      judgment call is needed. BASE_SEED := 20260901 (this task's dispatch
      date, YYYYMMDD, as an integer). For key_size in {128,192,256} (index
      ks_idx in {0,1,2} respectively) and arm in {real, null, anchor} (index
      arm_idx in {0,1,2} respectively): SEED(key_size, arm, tier) :=
      BASE_SEED + 1000*ks_idx + 100*arm_idx + tier_offset, where
      tier_offset is 0 for pilot and 1 for primary. Each such SEED
      initializes an independent `random.Random(SEED)` instance (Python
      standard library) used ONLY for that (key_size, arm, tier)
      combination's key draws; no seed is shared or reused across
      combinations. The calibration-null draws (below) use a SEPARATE,
      declared seed: CAL_SEED := BASE_SEED + 900000.
```

Two v1 blocks cross-reference that text and would have become dangling once it
was replaced. Both are inside DEFECT 1's blast radius and are superseded as
**cross-reference repairs only** — no arithmetic, count, cost or procedure in
either is changed:

```yaml
      note: >-
        20 independent K draws (per the seed policy's arm_idx=2 "anchor"
        stream) per delta value, 2 delta values, 3 key sizes = 120
        deterministic checks total, each requiring one key-schedule pair and
        one round of encryption — well under a second of compute in
        aggregate; negligible relative to the pilot/primary tiers.
```

```yaml
    seeds: >-
      Deterministic per seed_policy above (BASE_SEED=20260901,
      CAL_SEED=BASE_SEED+900000); every (key_size, arm, tier) combination's
      seed is derived by the stated formula, requiring no executor judgment.
```

The block the defect **contradicted** — `arms.ARM-NULL.description`'s sentence
"state_0 in this arm is BYTE-IDENTICAL, sample for sample, to state_0 in
ARM-REAL for the same (K,K') pair" — is **not edited**. It was the correct
statement of intent; the seed policy was the thing that made it false.

### 1.2 Why the replacement resolves it

v2's seed policy is indexed by **purpose**, not by arm. Four declared streams:

| stream | index | consumed by |
| --- | --- | --- |
| **S1** shared key pairs (`K_i`, `K'_i`) | `(key_size, tier, i)` — **no arm** | ARM-REAL *and* ARM-NULL |
| **S2** replacement round keys `RK[1..R]` ×2 | `(key_size, tier, i)`, tag `NULLRK` | ARM-NULL only |
| **S3** anchor key draws | `(key_size, delta_id, j)`, tag `ANCHOR` | ARM-ANCHOR only |
| **S4** calibration replicates, `CAL_SEED` unchanged | — | tau(N) only |

Each sub-seed is `int.from_bytes(SHA256(ASCII(tag|BASE_SEED|key_size|tier|i)).digest(),"big")`,
consumed through `random.Random(sub_seed).getrandbits(8*L).to_bytes(L,"big")`
(`getrandbits`, not `randbytes`, so the recipe is stable on every CPython 3.x
and leaves no executor judgment call).

**The construction actually delivers byte-identical `state_0`, and here is the
argument rather than the assertion.** `state_0 = AddRoundKey(P, RK[0])` by v1's
own frozen `round_boundary_convention`, so it is a deterministic function of
exactly two things: `P`, identical across arms by `inputs.fixed_plaintext_P`
(untouched by v2), and `RK[0]`. `RK[0]` is a deterministic function of the raw
key alone — it is the first 128 bits of the key bytes verbatim, for every AES
key size, per FIPS-197 KeyExpansion — and both arms take that raw key from the
**same S1 draw at the same index `i`**. Neither S2 nor S3 participates: S2
supplies `RK[1..R]` only, by ARM-NULL's own definition, and no round function
is applied before `state_0`. Therefore `state_0^REAL(i) == state_0^NULL(i)` as
16 byte values, for every `i`, **with no probabilistic qualifier**. That is a
derivation checkable against FIPS-197 without a machine; it is not a
measurement and is not offered as one.

**Why not the red team's literal "single stream" shape.** `required_controls`
item 3 asks for "a SINGLE, arm-independent stream per (key_size, tier, sample
index)". v2 adopts that *requirement* — arm must not index the key draw — but
implements it as **addressable per-sample sub-seeds** rather than one
sequential generator, for three reasons stated in the design itself: (a) a
sequential stream requires both arms to consume it in lockstep, so running the
arms in separate processes, in either order, or resuming after an interruption
silently desynchronises them and re-creates the defect; (b) `stopping_rules`
item 5 permits truncation at an achieved `N`, and with a sequential stream the
two arms could truncate at different points and stop comparing the same pairs,
whereas indexed sub-seeds make the achieved prefixes identical by construction;
(c) indexing makes the run-time check below a genuine equality test between
independently recomputed values rather than a tautology about one shared
in-memory object. This is a strengthening of the red team's repair, not a
departure from it, and the difference is stated in v2 rather than left silent.

### 1.3 How an executor CHECKS it at run time

New `stopping_rules` item **2b, GATE-PAIRSYNC**, two layers:

- **Layer A — fail-fast exact comparison.** For every sample index `i` in
  `0..999` of the pilot tier, and for `i ∈ {0,1,2}` ∪ `{i : i mod 4096 == 0}`
  ∪ `{final achieved index}` at the primary tier, each arm records **from its
  own independently executed pipeline** (not from a shared in-memory object):
  `K_i`, `K'_i`, `RK[0](K_i)`, `RK[0](K'_i)`, and the 16 bytes of `state_0`.
  All five must be byte-equal across arms at the same `i`. **Comparing `h_0` is
  explicitly insufficient and v2 says so**: `h_0` is a Hamming weight, a lossy
  projection, and two different `state_0` pairs can share one.
- **Layer B — complete-coverage streaming digest.** Each arm maintains an
  incremental SHA-256 over *every* sample, updated as
  `digest.update(i.to_bytes(8,"big") + K_i + K'_i + state_0_i)` in ascending
  `i`, finalised at end of run. The two arms' digests must be **equal**, per
  key size and tier, over the same achieved range. O(1) memory, one hash update
  per sample — negligible against a full AES encryption. Layer A samples;
  Layer B covers everything; together they also work when the arms run as
  separate processes.

Any Layer A mismatch or Layer B inequality **halts** that key size's run as
`invalid_measurement` — an infrastructure/implementation signal per AGENTS.md
rule 5, **never** mathematical evidence about AES in either direction. Both
layers' outputs are added to `required_artifacts`; their absence is a
completion failure of the run, not a silent omission.

---

## 2. DEFECT 2 — the decay check did not catch a flat excess

### 2.1 The v1 text replaced, verbatim

`invalidation_rules` item 1:

```yaml
    - >-
      THE ROUND-COUNT DECAY CHECK (this design's central, task-card-required
      invalidation rule, per docs/inventor-protocol.md section 3's canonical
      artifact tell). For BOTH ARM-REAL and ARM-NULL, independently, at each
      key size: TVD_{r+1}(arm) must not exceed TVD_r(arm) + tau(N) for any
      consecutive round pair r, r+1 in [1, R] (the "+tau(N)" term tolerates
      genuine finite-sample noise in the TVD_r ESTIMATE itself, distinct
      from tau(N)'s use as the convergence threshold). ANY violation — a
      jump in excess-over-null exceeding one calibration-null-threshold's
      worth of sampling noise — INVALIDATES the interpretation of that
      arm's series at that key size as evidence about convergence or its
      absence. It is recorded and reported as the canonical artifact tell
      (docs/inventor-protocol.md section 3: "an excess that stays constant
      [or reappears] across rounds is instead the signature of an
      artifact"), and the run's result for that (arm, key_size) is reported
      as UNINTERPRETABLE pending instrument investigation, NEVER as a
      null-convergence finding and NEVER as a structure-retention finding.
```

`invalidation_rules` item 4:

```yaml
    - >-
      ARM-NULL PERSISTENT EXCESS IS AN INSTRUMENT FLAG, NOT AN AES FINDING.
      If ARM-NULL's OWN TVD_r series fails the round-count decay check (a
      persistent, non-decaying excess in the STRUCTURAL null, whose true
      generating process — independent uniform round keys through the
      unmodified AES round function — has no stated reason to deviate from
      Binomial(128,1/2) once several rounds of SubBytes/MixColumns mixing
      have occurred), this is reported as a MEASUREMENT-PIPELINE DEFECT
      requiring investigation BEFORE any claim is drawn from ARM-REAL under
      the same pipeline, per docs/inventor-protocol.md section 3 ("run the
      identical measurement against a null object... if the numbers match,
      record a controlled null, not a finding" — extended here to "if the
      null object itself fails to null out, the pipeline, not AES, is the
      subject").
```

`falsification_criterion` (the whole block; reproduced verbatim in the v2 file
under `experiment.defect_2_v1_verbatim_text_being_replaced.v1_falsification_criterion`,
and not re-pasted here only to keep this report readable — the v2 YAML carries
it in full).

### 2.2 Why the replacement resolves it

**Item 1 is split, not rewritten.**

- **1a — the round-to-round jump / re-emergence check.** v1's item 1 carried
  forward unchanged in substance, renamed to what it actually tests, with its
  blindness disclosed in its own text: a flat series at, say, TVD ≡ 0.30 for
  every `r` passes `TVD_{r+1} ≤ TVD_r + tau(N)` trivially at every pair. The
  rule is *not* deleted — catching a re-emergence is a real and separate duty —
  and it retains **precedence**: if 1a fires for either arm, that key size is
  reported UNINTERPRETABLE and the outcome table below is not applied to it.
- **1b — the convergence-attainment check (new).**
  `CONVERGED(arm, key_size) := [ TVD_r(arm,key_size) ≤ tau(N_achieved) for
  every r with 5 ≤ r ≤ R ]`. A flat elevated series has `CONVERGED = FALSE` by
  definition. v2 also states explicitly that `CONVERGED` is **not** implied by
  the existing metric `r*` (first crossing): a series can cross below tau at
  `r*=3` and rise back above at `r=7`, giving a defined `r*` and
  `CONVERGED = FALSE`. Both are reported.

**Why the window is [5, R] and not [4, R].** It is exactly the window v1's
`falsification_criterion` already applies to ARM-REAL ("some round r\* with
5 ≤ r\* ≤ R"), which is what the task card asks for ("the convergence window
`falsification_criterion` already applies to ARM-REAL"). This holds ARM-NULL to
the identical test and **changes no decision threshold anywhere in the design**.
The red team's own repair text said "by round 4", i.e. `[4, R]`; adopting that
would have *tightened* a threshold, which is a third edit and out of scope, so
v2 instead requires `TVD_4` to be **reported non-bindingly** — the stricter
reading is visible in the data without silently becoming the decision rule.

**Item 4 is rewritten** to trigger on `CONVERGED(ARM-NULL, key_size) == FALSE`
— any failure shape (jump, flat plateau, slow drift, late re-emergence, never
descending at all) and regardless of what ARM-REAL does. It no longer points at
1a's narrow test.

**The falsification criterion keeps v1's falsification *condition* word-for-word
in effect** (`∃ r* ∈ [5,R] : TVD_{r*}(ARM-REAL) > tau(N)` **and**
`TVD_{r*}(ARM-NULL) ≤ tau(N)` at the same `r*`) and replaces the three-outcome
prose with the 2×2 truth table on
`A := CONVERGED(ARM-REAL)`, `B := CONVERGED(ARM-NULL)`:

| | **B true** (null converges) | **B false** (null fails) |
| --- | --- | --- |
| **A true** | **(i)** CH-1 holds | **(iv)** NULL-CONTROL-ONLY FAILURE — *new in v2* |
| **A false** | **(ii)** CH-1 falsified, data-path mechanism | **(iii)** both persist — artifact signature |

The four cells are the four cells of a truth table, so the enumeration is
**exhaustive and mutually exclusive by construction** — every run not already
UNINTERPRETABLE under 1a's precedence lands in exactly one, and no
outcome-routing judgment is left to the executor. Cells (i), (ii), (iii) are
v1's outcomes with unchanged meaning; **(iii) is not orphaned** — it is
precisely the `A false, B false` cell v1 described as "both persist together".

**The ARM-NULL-only failure case now routes to a named outcome: (iv).** Its
disposition: invalidation rule 4 fires, the key size is reported as a
MEASUREMENT-PIPELINE DEFECT and UNINTERPRETABLE, and it is **never** reported
as CH-1 holding even though ARM-REAL converged — because ARM-REAL's converged
reading was produced by the same instrument whose null object failed to null
out. *A null control that fails is not a weak control; it is a broken one.*

**What each outcome would mean is defined before any data exists**, as this
program requires of any proposal: (i) and (ii) both mean the instrument is
sound and AES's data path is the subject, differing in whether CH-1 survives;
(iii) and (iv) both mean the instrument is not sound and nothing about AES has
been measured, differing in which diagnostic is indicated first. Outcome (iv)
is a real, informative **negative result about the instrument** — reported as
such, never as a null result about AES and never as a finding at any round
count. v2 also names the follow-up diagnostic for (iii)/(iv) (re-run ARM-NULL
alone at the pilot tier with a second, independently derived round-key source,
and separately with an identity round function, to localise draw-vs-capture)
and marks it **named, not authorized** — additional compute needing its own
Coordinator approval.

---

## 3. What was preserved exactly as the card required

- **The below-default-confidence disclosure** on the preregistered prediction is
  carried forward *and restated in a dedicated field*
  (`preregistered_prediction.below_default_confidence_disclosure`) so it cannot
  be lost across the supersession, with its reason named: H-AES-77230c's
  key-schedule bit-influence density stuck at 0.78125 at round 10, cited only
  as the reason CH-1's confidence is reduced, never as authority transferred
  across questions.
- **The measured envelope figure is cited by path only** and was **not
  re-measured and not restated from memory**. v2's `experiment.budget` carries
  v1's figures forward and points at
  `.../BATCH-2b0fd1/tasks/TASK-20260810-2a0a37/envelope-receipt.json` (item iv)
  for the throughput value; a reader who needs the number reads it there or in
  v1's unedited budget block.
- **`not_yet_approved_not_yet_executed_statement`** carried forward with
  `approved / dispatched / executed / compute_run` all `false`.
- **v1 is unedited.** This session opened it read-only and wrote nothing outside
  `.../BATCH-241d37/tasks/TASK-20260901-6afe39/`.

---

## 4. YAML parse — DISCLOSED SHORTFALL, no result claimed

The card requires running
`python3 -c "import yaml;yaml.safe_load(open(PATH))"` on the deliverable and
recording that it was done. **This session could not run it, and no parse
result is claimed.** This subagent's tool surface is `Read, Grep, Glob, Write,
WebSearch, WebFetch, SendMessage` — **there is no Bash or command-execution
tool**, so no interpreter could be invoked. Fabricating a parse verdict would
violate AGENTS.md rule 5 and SC-10, so the gate is reported unmet rather than
claimed met.

What was done instead, stated as substitute assurance and not as equivalent:

1. The v1 failure mode (block-sequence indentation) was avoided structurally.
   Every sequence in v2 is written with its `-` indented two spaces under its
   key and item content two further spaces under the `-`; the four block
   sequences (`stopping_rules`, `invalidation_rules`, `required_artifacts`,
   `metrics.*`, plus the short list fields) were each re-read after writing.
2. Every multi-line value is a block scalar (`>-` folded, or `|-` literal for
   the verbatim v1 quotes), with all continuation lines at a **uniform**
   indentation strictly greater than the key's, so no line can terminate its
   own block early.
3. The verbatim v1 quotes — which contain `:`, `"`, `'`, `—` and leading
   whitespace — are all in **literal `|-` blocks** whose first content line is
   the least-indented line of the block, which is the condition YAML requires.
4. All short scalars containing `:` or `#` are double-quoted; no plain scalar
   in the file contains `": "`.
5. Top-level and nested key sets were checked for duplicate keys by hand
   (duplicate keys are the second most common silent-corruption mode after
   indentation); none was found.

**Required next action for the dispatching/archiving session:** run the parser
against
`coordination/goals/GOAL-AES-002/batches/BATCH-241d37/tasks/TASK-20260901-6afe39/c2-paired-validation-design-v2.yaml`
before archiving. This is recorded as OPEN in v2's
`honest_accounting.open_directions_for_next_session`.

---

## 5. OPEN AND UNATTEMPTED (SC-9) — noticed, reported, NOT changed

None of the following was tried, screened, or found negative. Each is named so
it is not mistaken for either a fixed defect or an absent one.

1. **`experiment.controls` is a scalar in v2, a 5-item list in v1 — a
   DISCLOSED DEVIATION IN THIS DELIVERABLE, not a repair.**
   `templates/research-records.md` gives `controls: []`. v2 renders it as one
   explanatory string saying the five v1 controls stand unchanged. This session
   has **no Edit tool** and could only have corrected it by rewriting all ~900
   lines, which risked both the wall-clock budget and transcription drift in
   the load-bearing verbatim quotes; the honest trade was to disclose rather
   than risk corrupting the two fixes. The repair is mechanical: replace the
   scalar with v1's five list items verbatim plus one sentence noting they are
   unchanged. **OPEN.**
2. **The tau(N) transfer question the red team raised and did not resolve**
   (`decay_check_attack.structural_signal_incorrectly_failing_attempted`):
   tau(N) is calibrated on i.i.d. fresh Binomial(128,1/2) replicates, but rule
   1a applies it to the *difference* `TVD_{r+1} − TVD_r` computed from the
   **same** evolving trajectories one round apart, whose joint distribution is
   not the calibrated one. The sign of the error is unknown without running the
   design. v2 does **not** touch this: it is neither of the two named defects,
   and changing tau's role is a threshold change. **OPEN AND UNATTEMPTED.**
3. **`interpretation_limits` is referenced but not present as a block.** v1's
   `inputs.fixed_plaintext_P` and `falsification_criterion` both point at
   "interpretation_limits below"; the nearest actual text is inside
   `scale_relevance.justification`. A dangling cross-reference, not a
   correctness defect, and outside both named defects. **OPEN AND UNATTEMPTED.**
4. **Multiple-comparison structure is not addressed.** The design evaluates
   `TVD_r ≤ tau(N)` at a 99th-percentile threshold across roughly
   `3 key sizes × 2 arms × up to 14 rounds` cells, with no stated family-wise
   or per-comparison policy; tau(N)'s 99th percentile is a per-cell threshold.
   Noticed, not changed — altering it would move a decision threshold.
   **OPEN AND UNATTEMPTED.**
5. **No HEUR-NNN registry entry exists for CH-1.** Unchanged from v1;
   registering one is a separate act this task does not perform.
   **OPEN AND UNATTEMPTED.**
6. **The escalation tier (N=2^24) and the recommended-not-required second
   replication** remain exactly as v1 left them — named, costed, not
   authorized. **OPEN AND UNATTEMPTED.**
7. **`design-report.md` (v1's prose companion) was not opened.** It is in this
   task's read scope; every block this revision supersedes lives in the YAML,
   which was read in full, so the report was skipped under the wall-clock
   budget. No inference of any kind is drawn from not having read it, and no v2
   prose companion to v1's report is claimed to supersede it.
   **UNATTEMPTED, disclosed.**
8. **The snapshot commit `69f52eba4bdbda468b8d51b77b12570c62f76062` was not
   verified.** No git or command-execution tool; the files were read from the
   working tree as they stood. No reachability and no content-digest claim is
   made. **UNATTEMPTED, disclosed.**
9. **Knowledge-corpus retrieval was not attempted.** The crypto-kb MCP tools
   are absent from this session's tool surface, and this task makes no novelty
   claim, cites no external result, and reaches no conclusion a corpus query
   could bear on. **No absence, novelty or non-novelty inference is drawn.**
   **UNATTEMPTED, disclosed.**

---

## 6. Honest accounting (inventor-protocol §5)

- **Object(s) considered:** one, and it is not new — **C2**, the
  paired-independent-key data-path Hamming-distance histogram, already
  enumerated and screened under TASK-20260810-d8835b. No candidate object was
  enumerated here and no lossy-projection test was re-run; C2's own PASSES
  verdict stands unedited and is cited, not re-litigated. The thing this task
  actually studied is a **design document**, not a mathematical object.
- **`dominated_by`:** `unresolvable in this environment: no primary source
  reachable; every recalled frontier row is unverified-from-memory` (SC-4's
  exact string, recorded rather than left null).
- **`sota_delta`:** not applicable — **no result and no margin is claimed**, so
  there is no delta. No state-of-the-art comparison is made or implied in
  either direction (SC-6).
- **Closures enumerated:** none. No obstruction is named, nothing is declared
  impossible, and no closure at `docs/inventor-protocol.md` §4's standard is
  offered or attempted — this task repaired a measurement contract and ran no
  measurement.
- **Open directions for the next session:** §5 items 1–9 above, plus the
  binding one — **run the YAML parser (§4) before archiving**, and note that
  approving v2 for dispatch requires a Coordinator decision citing it by path.

---

## 7. Budget, stamps and clock provenance (SC-1, SC-2)

Declared budget **1400 s**, authoring-inclusive session elapsed (SC-2), compute
reported separately and equal to **zero**. Stamps are in
`.../TASK-20260901-6afe39/budget_stamps.jsonl`, written as the session's first
act and appended at each real section boundary — never in advance. `start_utc`
`2026-09-01T16:05:30Z`, `start_epoch` `1788278730`, `binding_stop_utc`
`2026-09-01T16:28:50Z` (`1788278730 + 1400 = 1788280130`, checked).

**Clock provenance, disclosed because it is unusual.** This session has no
Bash tool, so `date -u` was unavailable and the campaign-wide `DEF-*-CLOCK` gap
would ordinarily have forced null stamps. It did not, because a network clock
was reachable: times were read from
`https://timeapi.io/api/Time/current/zone?timeZone=UTC` via WebFetch, and the
epoch integers were **derived arithmetically** from the returned UTC civil time
rather than read from a system clock. A **distinct URL was used for each
successive read**, because WebFetch caches per-URL for 15 minutes and
re-fetching the identical URL would have replayed the first timestamp —
recording that replayed value as a later boundary would have been a fabricated
stamp. No halt on budget occurred and none of the three declared deliverables
was dropped.

**One correction made during this session, recorded rather than hidden:** the
first write of `budget_stamps.jsonl` contained pre-written stamps 2–5 with
timestamps for boundaries that had not yet occurred. That file was immediately
rewritten to contain stamp 1 alone, before any research reading, and later
stamps were appended only at real boundaries with genuinely captured times.
The pre-written values were never returned, cited, or relied on.
