# What a memory-charged baseline at Classic McEliece's parameters still needs

**Task:** `TASK-20260803-cb44ab` · **Goal:** `GOAL-MCE-001` · **Batch:** BATCH-002
**Companions:** `cost_table_transcription.md`, `convention_as_stated.md`,
`source_access_log.yaml`

**This document names gaps. It does not fill any of them.** No convention is
adopted or proposed here, no cost is computed, and nothing is asserted about
whether any Classic McEliece parameter set is secure or threatened.

---

## 1. The criterion this is measured against, quoted exactly

`GOAL-MCE-001.completion_criteria`, second item, verbatim:

> *"A memory-charged concrete ISD cost at Classic McEliece's parameter sets,
> computed under a stated costing convention -- NOT ISD-FC-2026 unless and
> until it is adopted (see objective_correction) -- with hidden overhead,
> memory access, and time-memory tradeoffs accounted, and an
> affected-vs-safe scope statement."*

Five requirements are load-bearing in that sentence: **computed**, **under a
stated costing convention**, **hidden overhead accounted**, **memory access
accounted**, **time-memory tradeoffs accounted**, and an **affected-vs-safe
scope statement**.

## 2. What this task delivered, stated at its own size

A **transcription** of one published table — SEC Table 1, 150 cells, 5
parameter sets × 3 `mem` values × 8 algorithm columns — plus the sentences the
publishing document uses to describe it, from a copy this task fetched and
hashed, with the extraction checked three ways.

That is a **third party's published figure set and the words that party uses
about it**. It is not this program's computation, and it is not a convention
this program has stated. `BATCH-002-OPENING` §4 calls it *"the baseline half"*
of the criterion above; whether that framing holds is for the reviewers, and
this document's job is to say precisely what is still absent either way.

---

## 3. The gaps, named

### G1. "Computed" is not satisfied by a citation

The criterion says **computed**. Nothing in this package was computed. No
member of this program has run any estimator, at any parameters, under any
convention. A transcribed table establishes *what someone else published*; it
does not establish that this program can reproduce it, and it carries no
certificate of any kind (`docs/claims-and-verification.md`; this task's
certificate kind is **none**, as a pure transcription).

**Not filled here.** Filling it requires an approved experiment specification,
which `RQ-MCE-e65b3c`'s first constraint currently forbids designing until the
primary text condition is met.

### G2. The convention is *named* in SEC, not *stated* in SEC

`convention_as_stated.md` §1.3 reproduces the whole of SEC's specification of
its memory charge. It is three phrases — *"free access to arbitrarily large
amounts of memory"*, *"cube-root costs to memory access"*, *"plausible
square-root costs to memory access"* — and **no formula, no unit, no
definition of the quantity being charged, and no exponent convention**. SEC
attributes the models to the estimator and cites `[33]`.

So a baseline that said "SEC Table 1's convention" would be pointing at a
label, not at a stated convention. **The cost model itself lives in
Esser–Bellini, *"Syndrome Decoding Estimator"*, PKC 2022,
`https://eprint.iacr.org/2021/1243` — which this task did NOT read.** Only its
abstract page was fetched, only for bibliographic identity.

**Not filled here.** Naming the document is not reading it, and this package
must not be cited as if it had.

### G3. Hidden overhead is explicitly *incomplete in the source itself*

SEC's caption says, of all three models: *"Some cost components are ignored in
all estimates."* SEC **does not enumerate them**. The single component it names
is the vector-length exclusion — *"counts each vector operation as just 1
operation… no matter what the vector length is"* — and SEC draws the
consequence itself: *"Consequently, the 140.8 actually counts more than 2 143
bit operations."* `[EXTRACTION-DAMAGED: flattened superscript — printed form
2^143; see convention_as_stated.md §3.3 for the measurement]` and *"The exact
numbers in Table 1 should be expected to be
superseded by larger numbers from future estimators that count bit
operations."*

A baseline requiring *hidden overhead accounted* therefore cannot get that from
this table: the publishing party states that unaccounted components remain and
does not list them.

**Not filled here.** No component is enumerated, estimated or bounded by this
task.

### G4. Memory access is charged, but only as three unformalized fixed points

Three `mem` values, described in words. There is no formula, no architecture
model, no energy/area/latency model, and **no memory column in the table**. The
only memory quantity SEC attaches to any entry is a single prose figure for a
single attack: *"More importantly, the 140 .8 is for an attack using memory
2 86.6, according to the same estimator."* `[EXTRACTION-DAMAGED: flattened
superscript — printed form 2^86.6; see convention_as_stated.md §3.4]` — one of
120 cost cells.

**Not filled here.** Memory usage for the other 119 cost cells is **not
obtained**.

### G5. Time–memory tradeoffs are absent outright

Three fixed `mem` values are three points, not a tradeoff. SEC publishes no
tradeoff curve, no per-algorithm memory/time frontier, and no way to read one
off the table (see G4: there is no memory column).

**Not filled here.**

### G6. There is no affected-vs-safe scope statement available, because the left-hand side does not exist

`EV-MCE-332f99`'s boundaries record it plainly: *"No distance between the 2026
attack regime and Classic McEliece was computed, and none may be inferred from
this record: there is no transcribed left-hand side."* `iacr:2026/1232`'s body
remains unobtained (O-2, O-3; PDF endpoint 403, path-scoped, not circumvented,
and this batch is forbidden to re-attempt it).

A second scoping problem sits underneath that one: `EV-MCE-332f99` O-8 records
that the ISO parameter-set list contains **no mceliece348864 variant**, so
*"standardized parameter sets"* excludes the set that carries the table's
smallest entry. Any affected-vs-safe statement must say which set list it
means.

**Not filled here.**

### G7. No costing convention is currently bindable, and the RQ still instructs otherwise

`DEC-20260802-344883` D-6: *"ISD-FC-2026 IS NOT ADOPTED… a usable draft, not a
binding convention"*, with its declared binding scope naming HQC and SDITH.
`DEC-20260803-a5b9b1` D-3 retracted this goal's claim to bind to it.

**Observation, recorded and not resolved:** `RQ-MCE-e65b3c.constraints` as
committed still reads *"Bind to the costing convention produced under
GOAL-HQC-001 TASK-20260802-0100a5; do NOT derive a competing one"*, and
`RQ-MCE-e65b3c.scope.targets` still reads *"under the same costing convention
GOAL-HQC-001 and GOAL-SDITH-001 bind to"*. Per D-3 those instruct an act that
cannot currently be performed. `TASK-20260803-a53f73` is drafting a correction
to that constraint concurrently; **this task neither edits the RQ nor relies on
it**, and records the contradiction rather than resolving it.

The practical consequence for a baseline: there is at present **no adopted
convention to compute under and none this task may supply**, so the criterion's
*"under a stated costing convention"* is blocked upstream of any measurement.

### G8. The table is not independently reproducible from what SEC prints

To re-run SEC's numbers a later task would need, at minimum: the estimator's
identity **and version or commit** (SEC gives the citation `[33]` but **no
version, release date or commit**); the exact inputs used per row (see G9); and
the semantics of the `mem` parameter as the tool implements it (G2).

SEC connects a `param` label to a concrete pair exactly **once**, and in a
different context — PDF page 13: *"run the estimator for (4608 , 96) and
(8192, 96)"*, in a tightness discussion about 460896. That is one label of
five, stated in passing.

**Not filled here.** No input mapping is inferred for any row, including that
one.

### G9. The column labels are undefined in the source

`BC`, `BJMM`, `pdw`, `MO`, `BM` appear nowhere in SEC outside the table header
(`cost_table_transcription.md` O-1). A baseline that cited "the `MO` column"
could not say, from this source, which algorithm that is.

**Not filled here.** Supplying expansions from memory would be a fabrication
under AGENTS.md rule 9; inferring them from SEC §3.3 would be a derivation this
task is forbidden to make.

### G10. A second, differently-accounted published figure set exists and is unreconciled

`TASK-20260803-f3aece`'s access log (O2) records that
`classic.mceliece.org/comparison.html` carries **CryptAttackTester
bit-operation estimates** for overlapping problem sizes, published by the same
designers. This task did not fetch that page and transcribes none of those
figures.

Whether the two sets are consistent, comparable, or produced under the same
convention is **unknown to this task**. A baseline that quoted one without
addressing the other would be selecting among a source's own published numbers
without saying why.

**Not filled here.**

### G11. Quantum costs are not in this table

Table 1 has no quantum column. SEC discusses quantum attacks in prose only
(PDF page 9). Any baseline scoped to include quantum cost needs a different
source.

**Not filled here.**

### G12. The source's own numbers are dated, and the source says so

SEC is printed *"23 October 2022"*, and its own statement about its own table
is: *"The exact numbers in Table 1 should be expected to be superseded by
larger numbers from future estimators that count bit operations."* A baseline
built on this table inherits both the date and that expectation.

**Not filled here.** This task did not look for a later estimator, a later
edition of SEC, or any updated figure set.

---

## 4. What the transcription *does* remove from the gap

Stated so the gap list is not read as "nothing was gained":

- The published memory-charged figures at Classic McEliece's five parameter
  sets are now **in this repository, cell by cell, from a hashed retrieval**,
  instead of being read and set aside as they were in BATCH-001.
- The convention those figures were produced under is now recorded **in the
  publishing party's own words, with its twelve hedges collected** — which is
  what makes them comparable to anything later, and what a bare number would
  not have been.
- What the source does **not** state about its own cost model is now
  enumerated (G2–G5, G8, G9, G11), so a later task can see the shape of the
  missing model rather than rediscovering it.

None of that is a computed cost, a stated convention of this program's, or a
scope statement. Those remain open, and this task does not claim otherwise.

---

## 5. Certificate and claim discipline

- `certificate.kind: none`. This is a pure transcription: no discrete-log
  solve, no factor-base relation, no solver run, no measurement of this
  program's own. Stated explicitly per `docs/claims-and-verification.md`.
- Claim tier stays **toy** (`RQ-MCE-e65b3c.claim_tier_ceiling`); nothing here
  is a statement about Classic McEliece's standardized parameter sets.
- Runs authorized by the task card: **0**. Runs executed: **0**.
