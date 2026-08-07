# SEARCH_RECORD.md — DELIVERABLE ZERO

**Task:** TASK-20260803-a0a7b9 · **Batch:** BATCH-009 · **Goal:** GOAL-AES-003
**Date of search:** 2026-08-05 (UTC)
**Search window:** 2026-08-05T15:02Z – 2026-08-05T15:16Z
**Repository revision searched:** `16bbb893b0a345d3c66cfacd1e179bb2d456b21b`, clean tree
**Written BEFORE any measurement was taken.** No arm of this task had been
compiled or run at the time this file was written.

---

## The absence claim under test

BATCH-009's `objective` asserts, verbatim:

> "The campaign has never run an inventor-protocol section 3 NULL OBJECT for it
> [the r=5 yoyo statistic]. ... THE OBJECT THAT HAS NEVER BEEN SUBSTITUTED IS
> THE CIPHER ITSELF."

Per DEC-20260803-f6f113, that assertion is an unrun measurement until this
document records the search that tests it. This is that record.

**Operational definition used.** A *section 3 null object for the r=5 yoyo
statistic* is a run that (a) computes the same statistic — count of trials with
W ≥ 1, where W is the number of forward-ShiftRows plaintext diagonals on which
`d = D(c0') ⊕ D(c1')` vanishes — with (b) the same probe geometry (PW/CW
diagonals, amask, smask, swap rule, trivial-swap exclusion), while (c) the
**cipher object itself** is replaced by an object drawn from a distribution
with no round structure — a random bijection / ideal permutation on the block —
rather than by another member of the same deterministic SPN family (a different
round count, a different key, a different S-box, or a different active-word
mask).

Under that definition, an arm that only changes `rounds`, `amask`, `smask`,
`seed` or `sbox_spec` is **not** a null object: it is another point of the same
family. This is the batch objective's own criterion and I adopt it unchanged.

---

## Searches executed

All commands run from the repository root. Counts are the counts the commands
returned.

### S1 — file-space enumeration (what was in scope)

| Command | Result |
|---|---|
| `find coordination/goals/GOAL-AES-003 -type f \| wc -l` | **1040** files |
| `find coordination/goals/GOAL-AES-003 -name '*.json' \| wc -l` | **444** JSON files |
| `find coordination/goals/GOAL-AES-003 experiments -name '*.c' -o -name '*.py' -o -name '*.h' \| wc -l` | **608** source files |
| `find ledger -type f \| wc -l` | **1452** files |
| `find experiments -type f \| wc -l` | **13444** files |
| `ls coordination/goals/GOAL-AES-003/batches/` | BATCH-001 … BATCH-009 (9 batches, all searched) |

### S2 — keyword grep over the whole campaign, ledger, docs and knowledge

`grep -ril -- "<pat>" coordination/goals/GOAL-AES-003 experiments ledger docs knowledge`

| pattern | files matched |
|---|---|
| `random permutation` | 132 |
| `random_permutation` | 9 |
| `randperm` | 9 |
| `ideal cipher` | 30 |
| `ideal_cipher` | 0 |
| `ideal permutation` | 8 |
| `ideal_perm` | 0 |
| `null object` | 102 |
| `null_object` | 62 |
| `nullobject` | 0 |
| `PRP` | 143 |
| `lazy sampl` | 7 |
| `random bijection` | 19 |
| `random function` | 205 |
| `surrogate` | 48 |
| `shuffle` | 154 |

Prose matches dominate. To find an *implementation* rather than a mention, the
same patterns were re-run restricted to source:

`grep -ril -e 'random permutation' -e 'randperm' -e 'ideal permutation' -e 'ideal cipher' -e 'lazy sampl' -e 'random bijection' --include='*.c' --include='*.py' --include='*.h' coordination/goals/GOAL-AES-003 experiments`

→ **8 files**, every one of which was opened and read:

1. `BATCH-001/tasks/attack/step1_distinguisher.py`
2. `BATCH-001/tasks/count5/driver.py`
3. `BATCH-002/tasks/TASK-20260802-142a4b/build_results.py`
4. `BATCH-004/tasks/TASK-20260803-367b1b/src/yoyo_sbox.c`
5. `BATCH-004/tasks/TASK-20260803-367b1b/src/yoyo_sbox_v2.c`
6. `BATCH-005/tasks/TASK-20260803-48a239/finalize.py`
7. `BATCH-008/tasks/TASK-20260803-05e072/src/yoyo_sbox_v3.c`
8. `experiments/EXP-DEP-001/implementation/dep001_driver.py`

### S3 — exhaustive enumeration of every yoyo arm ever recorded

Rather than trust keywords, every JSON under the campaign was parsed and every
object carrying a `whist` or `W_ge1*` key was extracted with its
`arm` / `rounds` / `sbox_spec` / `instrument` fields:

```
python3 -  # glob 'coordination/goals/GOAL-AES-003/**/*.json', recursive
```
→ **440 JSON files parsed successfully** (of 444 globbed; the remainder are not
JSON-parseable objects of this shape and were separately covered by S4).

A companion text scan
(`glob coordination/**/*.json + experiments/**/*.json + ledger/**/*.yaml`,
substring test) found the yoyo statistic named in:

- `W_ge1` → **151** files
- `whist` → **153** files
- `yoyo`  → **61** files

### S4 — the distinct-arm inventory (the decisive search)

The extraction in S3 yielded the complete list of distinct yoyo arm
configurations in campaign history. Every arm falls into exactly one of two
`sbox_spec` values:

- `aes` — the AES S-box; and
- `rand:<seed>` — a uniformly drawn bijective S-box (seeds `20260803001`,
  `...002`, and `...701`–`...727`).

Round counts observed: r ∈ {1,2,3,4,5,6,10}. Arm families observed:
`A1–A4/PC` (BATCH-002 AES-NI probe), `Y-*` (BATCH-004), `CAL/TIE/TIE2`,
`D-*`/`SD31-*` (BATCH-005), `A0–A5`/`B0`/`B01–B27` (BATCH-006, BATCH-007),
`S1-*/S2-*/S3-*/S4-*/B1/B2` (BATCH-007), `ANCHOR-N24`,
`R9-*`/`K-*` (BATCH-008).

**There is no `sbox_spec`, `cipher`, or `family` field anywhere in the campaign
naming a random permutation, an ideal permutation, or any non-SPN object.**
Every yoyo arm ever run evaluates the same T-table / AES-NI SPN
`E_K^r = ARK_r · SR · SB · [ARK_i · MC · SR · SB] · ARK_0`, differing only in
`rounds`, `amask`, `smask`, `seed`, key, and S-box table.

### S5 — the four near-misses, examined individually

These are the only artifacts in the campaign that could plausibly be mistaken
for the missing control. Each was read in full and each fails the operational
definition for a stated reason.

| # | Artifact | What it actually is | Why it is not the null object |
|---|---|---|---|
| N1 | `BATCH-001/tasks/attack/step1_distinguisher.py`, section "B. control: matched random permutation" | Control for the **4-round integral (Square)** statistic, not the yoyo statistic. Its comment reads "a 128-bit permutation that is not 3-round AES". | Different statistic; and its surrogate `prp_aes10` is **full 10-round AES under an independent key** — a member of the same SPN family. Its other two controls (`random_sbox_3r`, `identity_mixcolumns_3r`) substitute a *component*, which the batch objective explicitly excludes. |
| N2 | `BATCH-001/tasks/count5/driver.py` arm `null_randperm_aes10`, tabulated in `BATCH-002/.../build_results.py` as `"family":"PRP surrogate (10-round AES-128)","r":10` | Control for the **count5 / multiset** statistic. | Different statistic; and the "randperm" is literally 10-round AES-128, self-labelled "PRP surrogate". Same SPN family. |
| N3 | `BATCH-005/.../finalize.py` RC-4: "Null-object control for the mod-8 statistic: the identical projection and statistic applied to a uniformly random bijection and to a uniformly random function, 400 trials each (OBJ-4)." | The *only* genuine random-bijection null object ever specified in this campaign. | (a) It is for the **mod-8 statistic on the GF(2^4) nibble instrument**, not the r=5 yoyo statistic on the 128-bit SPN; and (b) its recorded `"status"` is **`"NOT REACHED."`** — it was specified and never run. |
| N4 | `BATCH-005/.../finalize.py` RC-6 | "Structure-destroyed controls at 2^32, plus **the measured-PRP null that was declared and skipped**". | Recorded `"status": "PARTIALLY REACHED ... WITHOUT the measured-PRP null"`. Its own text states the missing half "would replace the ANALYTIC null of 4*2^-32 with a MEASURED one, settling whether the null expectation the ALIVE/DEAD rule divides by is itself correct for this probe — **which no arm run in this campaign has ever checked**." |

N4 is the campaign's own prior, independent statement of the same absence,
written on 2026-08-03 by a different task. It corroborates rather than
contradicts the BATCH-009 objective.

### S6 — the r=10 arm specifically

`K-R10-NULL-P30` (BATCH-008) is the arm the task card warns about: matched
seed 531001, armid 1, threads 2, amask 1, smask 1, 2^30 trials, 1 hit. It is
recorded in EV-AES-8b8dcf as "the matched-seed r=10 arm". Its `sbox_spec` is
`aes` and its `rounds` is 10 — i.e. it is the **r = 10 point of the same
one-parameter family** whose r = 5 point is under test. It is a
parameter-increase decay check, not a cipher substitution.

---

## VERDICT

**THE BATCH'S ABSENCE CLAIM IS TRUE. I could not falsify it.**

Across 1040 campaign files, 444 campaign JSONs (440 parsed as JSON objects and
walked), 608 source files, 1452 ledger files and 13444 experiment files, in 9
batches, using 16 keyword patterns and an exhaustive enumeration of every
recorded yoyo arm, **no run exists in which the cipher object itself was
replaced by a random bijection / ideal permutation while the r = 5 yoyo probe
geometry was held fixed.** Every yoyo arm ever run is the same SPN under a
varied round count, key, S-box or mask.

Two independent prior statements in the campaign's own artifacts agree
(BATCH-005 RC-4 `NOT REACHED`, BATCH-005 RC-6 "the measured-PRP null that was
declared and skipped ... which no arm run in this campaign has ever checked").

**Consequence for this task:** the batch premise stands, rank 1 is not
displaced, and the control described in PREREGISTRATION.md is genuinely new.

## Limits of this search — stated so a reviewer can attack it

1. The search is over the repository at revision `16bbb893b0a3…` only. A run
   performed and never committed would not be found. I make no claim about
   uncommitted work.
2. The search keys on the yoyo statistic's field names (`whist`, `W_ge1*`) and
   on 16 keyword patterns. An arm that measured the same statistic under
   entirely different field names *and* avoided all 16 keywords would be
   missed. I judge this unlikely because S4's arm inventory was built from the
   field names the shared instrument emits, and all five known instrument
   generations (`probe.c`, `yoyo_sbox.c`, `_v2`, `_v3`, `count5.c`) emit them.
3. `experiments/` was included in the source and keyword scans but its 13444
   files are dominated by unrelated ECDLP work; only
   `experiments/EXP-DEP-001/implementation/dep001_driver.py` matched, and it is
   not an AES artifact.
4. I searched for the *control*. I did not audit whether every recorded arm's
   numbers are correct; that is the validator's job and BATCH-008's validator
   already scanned 4858 JSON files for a related premise.

---

## Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  requested_policy_source: >-
    AGENTS.md default for the executor role. The handoff block of
    TASK-20260803-a0a7b9 in BATCH-009/dispatch_queue.json carries NO
    inference key; this is recorded rather than invented.
  resolved_model_id: claude-opus-5
  resolved_model_display_name: Opus 5
  fallback_used: true
  fallback_reason: >-
    orchestration/model-policies.yaml routes executor-implementation to a
    GPT-5.6-family alias. Per CLAUDE.md, Claude Code cannot resolve those
    identifiers; subagent frontmatter supports only Claude models. Recorded,
    not silently substituted.
  model_verified: false
  model_verified_reason: >-
    No `python3 -m orchestration.adapter doctor --probe` was run in this task.
  reasoning_effort: null
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
  independent_session: false
```

**Parse statement:** this file is Markdown, not a machine-parsed format. Its
one embedded YAML block above was parsed whole with `yaml.safe_load` before
this task finished; the result is recorded in `RESULTS.json` under
`artifact_parse_checks`.
