# RT4 DERIVATION, WRITTEN BEFORE ANY FILE UNDER THE PRODUCER'S TASK DIRECTORY WAS OPENED

TASK-20260826-a9d51e, Red Team, BATCH-171407 round 4, joints R4-J4 / R4-J5 / R4-J6.

This file is written at the moment stated in its title. At the time of writing,
`coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/tasks/TASK-20260826-82c660`
had not been opened, listed or grepped by this session, and an audit hook in
`rt4_rederive.py` raises on any `open` naming that prefix (0 blocked attempts,
because none was made). `harness/diffpath/readmit.py` and
`tests/test_diffpath_readmit.py` were never read and are absent from
`sys.modules` at the end of both construction runs.

EVERYTHING BELOW IS MY OWN, FROM THE FROZEN CONTRACT'S WRITTEN STATEMENT AND THE
COMMITTED SUBSTRATE. Mechanism: my own re-implementation, `rt4_rederive.py` and
`rt4_armb.py`, in this directory.

---

## 1. THE READING QUESTION (R4-J4), DECIDED FROM COMMITTED TEXT BEFORE MEASURING

The contract's statement:

> the cell (F, r) IS FORCED FOR I if and only if, in the key pi_I(K) with c(r)
> additionally deleted, THERE REMAINS a component d such that the graph carries
> a DERIVATION-BACKED edge d -> c(r) on the primitive under consideration.

with `r` defined two sentences earlier as "a depth-1 row, i.e. the deletion of
exactly one component c(r) from K", and `K` as "THE STRICT MEMBERSHIP KEY,
DERIVED AT RUN TIME FROM THE COMMITTED SERIALISER".

I DECLARE THREE READINGS BEFORE MEASURING ANYTHING. Two are the ones a reader of
the clause alone would reach; the third is mine.

* **A `edge_only`** — the literal biconditional. `in_linearized_code` on md5 has
  no derivation-backed in-edge, so no `d` remains, so the cell is NOT forced and
  is ADJUDICATED.
* **B `edge_or_vacuous`** — the committed predecessor's own disjunct
  (`depgraph.forced_rows`, and `depgraph.ASSIGNING_RULE` R1 verbatim: "...or the
  deleted component is not in that primitive's key at all"). Vacuous deletion =>
  FORCED.
* **C `out_of_domain` — MINE.** `r` is defined as the deletion of *exactly one
  component from K*. On md5 the derived key has FIVE components and
  `in_linearized_code` is not one of them, so *there is no such row on md5*.
  The predicate has no instance there. The cell is neither forced nor
  adjudicated: it is OUT OF DOMAIN and must be emitted as `null` under H-8,
  which forbids emitting 0 for an unmeasured cell.

**MY RULING, MADE BEFORE MEASURING: reading C is what the contract's own text
says, reading B is what the committed rule does, and reading A is what the
forcing clause says when read in isolation from the definition of `r` two
sentences above it.** The clause and the definition are in the same block and
must be read together; read together they yield C.

## 2. A SECOND, INDEPENDENT UNDER-DETERMINATION THE TWO-READING FRAME DOES NOT COVER

The predecessor's six excluded cells are recorded as `(family, row_deletes)`
pairs with NO PRIMITIVE INDEX (`depgraph.select_cells`), and a row enters
`depgraph.forced_rows` only when it is forced on EVERY primitive. The new rule
is explicitly per-primitive ("on the primitive under consideration"), so its
forced set is a set of `(family, row, primitive)` triples. CTL-FORCE-PI orders
these compared "cell by cell", and the contract never says at which granularity.

**Two mappings are available and they disagree**: UNION (a cell is forced if
forced on some primitive) and UNIFORM/INTERSECTION (forced iff forced on every
primitive, which is what the committed rule means).

**This is a THIRD READING IN THE SENSE THAT MATTERS — an unstated choice on
which the stopping rule turns — and it is orthogonal to A/B/C.**

## 3. NUMBERS I DERIVED (rt4_rederive.py; rt4_rederivation.json)

Substrate facts, all re-derived, nothing quoted:

* Strict generator set `frozenset({E1,E3,E4,E5})`. Key components: **md5 5**
  (`primitive, length, message_difference, step_delta, block_index`), **sha1 6**
  (those plus `in_linearized_code`). Union = the contract's six names.
* Derivation-backed (`derived_and_witnessed`) edges: **md5** `step_delta ->
  length`; **sha1** `step_delta -> length`, `message_difference -> length`,
  `message_difference -> in_linearized_code`. Four in total.
* Transitive closure over derivation-backed edges adds NOTHING: every target has
  depth-1 in-edges only. **The "path of edges" candidate reading is
  extensionally identical to the single-edge reading here.** Bounded negative,
  measured, not assumed.
* Declared population sizes: md5 2624, sha1 3208. Constructible families:
  `d_block_index`, `d_message_difference`, `d_step_delta` (3 of 6).
* Committed predecessor forced rows: `{length, in_linearized_code}`,
  primitive-uniform. 3 families x 2 rows = the committed SIX cells.

### 3a. Per-instrument forced ROW sets. BOTH COMPOSITION ORDERS AGREE EVERYWHERE.

`project_then_delete` and `delete_then_project` gave IDENTICAL forced sets for
every instrument, reading and primitive I ran. The order ambiguity the contract
flags is real in the text and **empty in this instance**.

| instrument | reading | md5 forced | sha1 forced |
|---|---|---|---|
| honest | edge_only | `length` | `length, in_linearized_code` |
| honest | edge_or_vacuous | `length, in_linearized_code` | `length, in_linearized_code` |
| honest | out_of_domain | `length` (+`in_linearized_code` OUT OF DOMAIN) | `length, in_linearized_code` |
| O-E | edge_only | `length` | `length` |
| O-E | edge_or_vacuous | `length, in_linearized_code` | `length` |
| O-E | out_of_domain | `length` (+ood) | `length` |

CTL-FORCE-PI side 2 (the rule must move): `forced_set_is_invariant_honest_vs_O_E`
is **false under every reading and both orders**. Side 2 holds.

CTL-FORCE-PI side 1 (identity vs the committed six):

* at **UNION** granularity: **equal under ALL THREE readings and both orders**.
* at **UNIFORM/per-primitive** granularity: equal under `edge_or_vacuous` only;
  under `edge_only` and `out_of_domain` the md5 side is `{length}` and the
  committed exclusion is `{length, in_linearized_code}`.

### 3b. THE BLINDED QUANTITY. Adjudicated/excluded partition and differing count.

Per primitive; cells are `(family, row)` over the 3 constructible families and
the 6 rows, minus the family's own diagonal row.

**MY EXCLUDED-CELL LIST, honest instrument, edge_or_vacuous:** md5 and sha1 each
exclude 3 diagonal cells and 6 forced cells — `(d_block_index, length)`,
`(d_message_difference, length)`, `(d_step_delta, length)` forced by
`step_delta -> length` (md5, sha1) and by `message_difference -> length` (sha1);
and `(d_*, in_linearized_code)` forced by `message_difference ->
in_linearized_code` on sha1 and vacuously on md5.

| reading | primitive | domain = honest's adjudicated | domain = O-E's adjudicated | domain = intersection | domain = union |
|---|---|---|---|---|---|
| edge_only | md5 | 12 cells, **0** differing | 12, **0** | 12, **0** | 12, **0** |
| edge_only | sha1 | 9 cells, **0** differing | 12, **1** | 9, **0** | 12, **1** |
| edge_or_vacuous | md5 | 9, **0** | 9, **0** | 9, **0** | 9, **0** |
| edge_or_vacuous | sha1 | 9, **0** | 12, **1** | 9, **0** | 12, **1** |
| out_of_domain | md5 | 9 (+3 null), **0** | 9 (+3 null), **0** | 9, **0** | 9, **0** |
| out_of_domain | sha1 | 9, **0** | 12, **1** | 9, **0** | 12, **1** |

Aggregate, NAMED AS AN AGGREGATE (H-9), reading `edge_or_vacuous`, domain =
O-E's adjudicated set: **1 differing cell of 21 adjudicated.** Under `edge_only`,
same domain: **1 of 24.** Under domain = honest's adjudicated set, every reading:
**0 differing.**

**THE SINGLE DIFFERING CELL, IDENTIFIED:** `(d_message_difference, row deleting
in_linearized_code)` on **sha1**, honest = NOT DETECTED, O-E = DETECTED.

### 3c. Facts that decide two controls, derived not quoted

* **honest DETECTED count on the re-admitted set = 0**, under every reading and
  both orders. Therefore `always_non_member` IS ARITHMETICALLY PINNED AT 0
  again, exactly as D-10 / RT-J8-2 recorded, and **P-D's re-admitted half is
  REFUTED**: no adjudicated cell of arm (a) has the honest instrument at
  DETECTED.
* **O-E is the IDENTITY on md5** (`proj_drop_on_primitive([...], 'sha1')`
  returns the key unchanged when `prim != 'sha1'`). Honest and O-E are THE SAME
  FUNCTION on md5, so **every md5 differing count is 0 by construction, on every
  cell, under every reading, forever.** The md5 arm cannot fail.

### 3d. Adversarial instruments (O-Q4 and two of mine), adjudicated ROWS per primitive

| instrument | reading | md5 adj rows | sha1 adj rows |
|---|---|---|---|
| honest | edge_only | 5 | 4 |
| O-E | edge_only | 5 | 5 |
| O-Q4 flag-blind on sha1 | edge_only | 5 | 4 |
| **O-Q7b step_delta-blind** | edge_only | **6** | 4 |
| **O-Q7a totally blind** | edge_only | **6** | **6** |

`O-Q7a` projects away every component but `primitive`. It identifies literally
nothing and it receives the LARGEST adjudication surface of any instrument
tested, on both primitives, under every reading.

## 4. ARM (b), DERIVED INDEPENDENTLY (rt4_armb.py; rt4_armb.json)

Family built exactly as the contract declares it: perturb the message difference
and SET the flag False. Draw plan mirroring the committed new-family plan
(`K_VALUES` with 1 deterministic draw per k plus 8 seeded at k>=1): 368 draws per
primitive.

* **md5: 0 accepted / 368 constructed**, every rejection at check id
  `W3_...`. **But the md5 branch of W3 is a DIFFERENT PREDICATE from the sha1
  branch of the same id**: md5 W3 tests `in_linearized_code is not None`, sha1
  W3 tests `flag == sha1_in_linearized_code(dv)`. Probe: an unmodified md5 entry
  passes; the SAME entry with the flag merely set to False — message difference
  untouched — already violates W3. **The md5 refusal is the schema forbidding
  md5 objects to carry the flag at all, not a consistency test failing.**
* **sha1: 360 accepted / 368**, 8 rejected at W3 — the 8 `k = 0` draws, where the
  dv is unperturbed, is therefore still a codeword, and the declared flag False
  contradicts it. **The family is NOT constructible at k = 0 on sha1.**
* Inconsistent side of CTL-PAIR-WF as I built it: 368/368 rejected on md5;
  **360/368 rejected on sha1 with 8 WRONGLY ACCEPTED**, again the `k = 0` draws,
  where the "inconsistent" object is not in fact inconsistent.
* **Measured moved-component set on all 360 accepted sha1 draws =
  `{in_linearized_code, message_difference}` = the DECLARED set.** The
  declaration is TRUE.
* **AND IT IS NOT THE RIGHT DESCRIPTION.** 320 of 320 gate-accepted
  consistent-pair draws have a serialised key IDENTICAL to
  `controlpower.perturb_message_difference` on the same bit positions; 0 of the
  perturbed sha1 dvs remained codewords. This is not only measured, it is
  derived: W3 rejects every draw whose declared flag differs from
  `sha1_in_linearized_code(perturbed dv)`, so the gate-accepted image of the
  consistent-pair constructor is CONTAINED IN the image of the committed
  `perturb_message_difference` constructor. **On sha1 the family is the
  committed `d_message_difference` family under a new name, restricted to
  k >= 1; on md5 it is not expressible. Its declaration does no work on either
  primitive.**

## 5. WHAT I PREDICT I WILL FIND IN THE PRODUCER'S PACKAGE, RECORDED SO IT CAN BE SCORED

Written before reading, so that a match is corroboration and a mismatch is a finding.

1. A differing count of **1**, with the cell `(d_message_difference,
   in_linearized_code)` on sha1, honest NOT DETECTED / O-E DETECTED.
2. Both composition orders reported as AGREEING.
3. `honest_detected_cell_count = 0` on arm (a) and `always_non_member`
   `arm_was_arithmetically_pinned: true`.
4. Arm (b) constructible on sha1 and not on md5, rejected at W3.
5. **A DENOMINATOR I EXPECT TO DISAGREE WITH.** I get 360/368 accepted on sha1
   and I expect the package to report a clean 368 if its plan drops `k = 0`.

END OF PRE-READING DERIVATION.
