# S3 — Measurement block A: L-EQ, L-FIELD, L-BASE with constructed controls

**Task** TASK-20260904-90ac09 · **Slot** S3 · **Role** executor
**Goal** GOAL-SCURVE-137bd9 · **Question** RQ-SCURVE-960dbd · **Batch** BATCH-a40709
**Experiment** EXP-SCURVE-3f87f6 · **Archived by** TASK-20260904-fa10f7 (S4)

## 0. Approval pointer (condition C-2), reproduced as required

EXP-SCURVE-3f87f6 **is approved with conditions by DEC-20260904-5216dd**.

The contract file `experiments/EXP-SCURVE-3f87f6/specification.yaml` reads
`status: draft` and `approved_by: null` and **always will**: its bytes are
hash-bound by the completed TASK-20260904-850ff6 snapshot archive, so writing
`approved_by` would permanently break that archive. This is expected, not an
oversight. Both deliverable YAML documents carry
`approved_by_decision: DEC-20260904-5216dd`.

The pass condition of CTRL-CONSTRUCTED-RANDOMPOINT is governed by
**DEC-20260905-f630e4 ruling D-4**, read in full before anything was run.

**Claim ceiling, honoured here:** `analyzed` at best, never `supported`. This
report adjudicates **no criterion cell**, compares **no measured quantity
against any threshold or intake cell**, and makes **no statement about any
curve's security in either direction**. Slot S7 alone may compare. Every
quantity is scoped to the curve labelled NIST P-224, to the parameters in the
committed capsule whose sha256 is recorded below, to pure-Python integer
arithmetic, to this runtime and to the declared budget, and transfers to no
other curve without re-running.

## 1. Pre-run gates, each re-checked in this session rather than trusted

| Gate | What was checked | Expected | Computed | Match |
|---|---|---|---|---|
| C-1 | `sha256(experiments/EXP-SCURVE-3f87f6/specification.yaml)` (working tree) | `0069b16e39b5a23f1535fa214f72ea1e49deb37ebbfcd678a0d62f56ac43c3d8` | `0069b16e39b5a23f1535fa214f72ea1e49deb37ebbfcd678a0d62f56ac43c3d8` | **YES** |
| C-1 | same path via `git show b012132b2:…` | as above | identical | **YES** |
| C-5 | `sha256(…/BATCH-ef5b1e/tasks/TASK-20260824-53ecc0/parameter-capsule.yaml)` (working tree) | `5125d93cd35476075c15bec668bbef6a3021ac7c3bd23e92f7ba53307b68ecc2` | `5125d93cd35476075c15bec668bbef6a3021ac7c3bd23e92f7ba53307b68ecc2` | **YES** |
| C-5 | comparand read from `…/TASK-20260824-4af491/snapshot-receipt.json` `path_sha256` for that path | — | `5125d93c…b68ecc2` | **YES** |
| C-5 / D-1 | same path via `git show 5c3bfe273070e0537a21ae5491fb028b7e5efa1e:…` | as above | identical | **YES** |
| D-1 | archive commit `5c3bfe273070e0537a21ae5491fb028b7e5efa1e` reachable from HEAD | reachable | `git merge-base --is-ancestor` → reachable | **YES** |
| — | `sha256(…/TASK-20260824-53ecc0/audit-plan.yaml)` | `eb1b33994549cf0a8160b85dfa169d1ba053c51c1340f7bd8b7b638865d3cc80` | identical | **YES** |
| — | commit named in the dispatch instruction, `e6ca74c75`, is an ancestor of HEAD `ea308c2d49dbdba06c08febc645bae2f36ed9250` | ancestor | ancestor (HEAD adds only the S3 claim commit) | **YES** |

Working tree at start: clean except for this task's own untracked directory.

### CAP-2, re-run in **this** session (capability is per-session, never per-repository)

The driving session's pass at 2026-09-05T03:37:37Z shows the gate *can* pass
here, not that it *will* for me. Re-probed at **2026-09-05T03:46:28.843015+00:00**
with values deliberately unrelated to the audited curve:

```
python_version: 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]   implementation: CPython
probe1  7**500 * 11**450 -> 2961-bit product; exact division recovers both operands: True
probe2  pow(3, 2**400+12345, 2**521-1) -> 521-bit result; Fermat consistency on that Mersenne prime: True
probe3  math.isqrt((10**200+7)**2) exact: True
probe4  gcd at scale: True
probe5  no silent float fallback (10**40 + 1 != 10**40, type int): True
probe6  shell / command execution: True (this probe ran through a shell)
cypari2_importable: False — ModuleNotFoundError: No module named 'cypari2'
all_arithmetic_probes_pass: True
```

Arbitrary-precision integer arithmetic and command execution are **available**,
so the slot ran. PARI is absent; batch.yaml declares this slot `pari: no` and
nothing here needed it, so its absence is recorded and is **not** an impediment.
No network was used at any point. Nothing named `bedrock` was requested,
selected, probed, or present in the environment (`env | grep -i bedrock` → no
match).

## 2. Knowledge-retrieval attempt, recorded verbatim (obligation carried from batch.yaml)

The MCP `search_knowledge` tool was **not exposed to this subagent session**.
The obligation was therefore attempted through the same index's CLI,
`kb/.venv/bin/crypto-kb search`. Three queries, verbatim:

1. `NIST P-224 group order cofactor certified`
2. `P-224 base point order n Hasse interval uniqueness`
3. `EXP-SCURVE-3f87f6 L-EQ exact coefficient equality`

All three returned, verbatim and identically:

```
collection 'crypto_knowledge_v1' does not exist in this process. CRYPTO_KB_QDRANT_URL is ':memory:',
which is an embedded index that lives and dies with the process -- ingesting in one command and
searching in another cannot work. Either point at a server (`make qdrant-up`, then
CRYPTO_KB_QDRANT_URL=http://localhost:6333) or use a file-backed embedded index
(CRYPTO_KB_QDRANT_URL=./.kb-index), then re-run `crypto-kb ingest`.
```

**This is a fact about the index and this session, not about the research.**
The index is derived and is empty here. **Absence of a hit licenses no
inference**, and nothing in this report asserts that any quantity has or has
not previously been computed in this program. `kb/.env` does not exist in this
worktree, which is why `CRYPTO_KB_QDRANT_URL` is `:memory:`.

## 3. Blinding disclosure (condition C-7) — I was NOT blind, stated per quantity

C-7 discloses that `audit-plan.yaml` carries 17 `quantitative_prediction`
blocks stating the answers. **I did not read that file until every quantity
below had been computed and both deliverable YAML documents had been written
and their sha256 recorded.** I then read all 17 blocks, in one pass, after the
fact.

But C-7's enumeration is not the whole leak, and I am recording the rest:
**`batch.yaml` and the parameter capsule — both of which I was required to read
*before* running — themselves state several expected outcomes.** Per quantity:

| Quantity | Expectation read BEFORE computing? | Source of the pre-read expectation |
|---|---|---|
| `int(intake_decimal) == int(retrieved_hex,16)` for the constant coefficient | **No.** Both representations are the *inputs*; the assertion that they are equal was read only afterwards. The capsule states this reconciliation is `NOT_YET_EXACTLY_RECONCILED`. | audit-plan (after) |
| advisory `b mod 9`, `b mod 11` | **Yes** (values 4 and 7) | capsule `checks_performed_this_session`, marked advisory and "PROVES NOTHING" |
| `a == p − 3` | **Yes** | batch.yaml S3 deliverables text; capsule word-level reconciliation argument |
| `p == 2^224 − 2^96 + 1` | **Yes** (word-level argument, not an integer computation) | capsule `reconciliation.modulus_expression` |
| `p` bit length = 224 | **Yes** (implied by "56 hex digits (224 bits)") | capsule `representation_note` |
| `p mod 4 == 1` | **Yes**, explicitly | capsule `derived_quantities_to_be_certified` |
| nonsingularity witness **value** | **No** — only "≠ 0" (afterwards) | audit-plan (after) |
| j-invariant **value** | **No** — only "neither 0 nor 1728", read **before** | batch.yaml S3 deliverables text |
| probable-primality verdicts, round counts, witness lists | **No** | — |
| `G` on the curve | **No** | audit-plan (after) |
| `n·G = O`, `(n−1)·G` finite | **No** | audit-plan (after) |
| Hasse multiple count, `#E`, derived `h` | **No** for the count and `#E`; the *retrieved* `h = 1` field is an input read before, and the capsule instructs L-BASE to derive rather than trust it | capsule field `h` (input) |
| trace `t` **value** | **No** — only the defining formula | capsule `derived_quantities_to_be_certified` |

**Consequence, stated plainly: no quantity in this run may be represented as
independently derived in the sense of a blind re-derivation.** The rows marked
"Yes" are the ones where a reviewer should discount my agreement most heavily.
The backstops that remain real are the ones DEC-20260904-5216dd names: the
producing source is committed as an artifact, every number reproduces from it
(§7), and condition C-8 assigns a genuinely blind re-derivation of L-EQ's exact
equality and of the derived group order to the S9 review plan. I hold no
opinion on whether that is sufficient; it is not my judgement to make.

## 4. Controls — run FIRST, on the identical code path (contract `control_ordering_rule`)

Full record: `controls-block-a.yaml`. In the producing source all three
controls are computed inside `run()` **before any lane quantity is touched**; a
reader can verify the ordering by reading the function top to bottom. Each
control calls exactly the function the target lane calls — there is one
`is_probable_prime`, one `nonsingularity_witness` and one `on_curve` in the
program.

| Control | Construction | `must_do` | Outcome | Passed |
|---|---|---|---|---|
| CTRL-CONSTRUCTED-COMPOSITE | product of two 112-bit generated integers; **composite by construction** because both factors exceed 1, so the control's validity trusts no primality oracle. Product bit length 224, matching the field prime's, on the first rejection-sampling attempt. | primality checker MUST REJECT | **REJECTED.** All 20 Miller-Rabin bases witnessed compositeness; first witnessing base = 2. | **YES** |
| CTRL-CONSTRUCTED-SINGULAR | over the same p: `k = 7`, `a' = −3k² mod p`, `b' = 2k³ mod p`, so `4a'³ + 27b'² = 4(−27k⁶) + 27(4k⁶) = 0` identically over the integers — **singular by construction** | nonsingularity check MUST REJECT | **REJECTED.** Witness value computed as exactly `0`. | **YES** |
| CTRL-CONSTRUCTED-RANDOMPOINT | 3 uniform coordinate pairs over the same p, drawn from `random.Random(20260905)` | see D-4 below | **PASS on all 3 draws.** | **YES** |

**All three controls fired. No lane is voided by INV-1.**

### CTRL-CONSTRUCTED-RANDOMPOINT under DEC-20260905-f630e4 D-4

The pass condition implemented is the **contract's** (`specification.yaml:289`,
"MUST ACCEPT it only if it is on the curve"), not `batch.yaml:404`'s "must
reject it", which D-4 supersedes **on force, not placement**. Concretely:

> **PASS ⇔ the checker's decision on the drawn pair equals the exact
> arithmetic ground truth for that pair.**

The reason, restated because I checked it rather than took it: affine points
number exactly `p − t` with `|t| ≤ 2√p` by Hasse, so a uniform pair lies on the
curve with probability `(p − t)/p²`, within `2/p^{3/2}` of `1/p` — small but
**not zero**. "Must reject" is therefore failable by a *correct* checker on that
draw, and is passed perfectly by a constant-reject checker, which is the
degenerate instrument the control exists to exclude.

Ground truth is computed by a **different code path** from the checker:
`on_curve()` reduces modulo p at every step; `ground_truth_on_curve()` forms the
full unreduced integer `d = y² − (x³ + ax + b)` with no intermediate reduction
and asks only whether `p | d`. Recorded per draw: the pair in full, both sides
of the congruence, the unreduced difference's bit length, the ground truth, the
checker's decision, and their agreement.

- All three draws were **off the curve**, so all three exercised the reject
  path, and the checker agreed with ground truth on all three.
- **No draw was on the curve in this run, so no redraw was triggered.** Had one
  been, D-4 requires it be recorded as a **PASS**, recorded in full, noted as
  not exercising the reject path, and followed by another draw, with **no draw
  ever discarded**. The source implements exactly that and records
  `draws_discarded: 0`.
- **Two-sided exhibit**, as D-4 requires: this control's rejections are recorded
  *together with* L-BASE's **acceptance of the base point on the identical
  `on_curve()` function**. That pair is what excludes both the constant-accept
  and the constant-reject instrument; neither half alone does.
- **No false-accept rate is reported and none is claimable from these draws.**
  The field is present and explicitly `null` with that reason. A checker that
  accepts an arbitrary pair with probability q is caught by a single null draw
  with probability q, so three draws have weak power against a partially broken
  instrument. Three draws rather than one is *permitted* and was *not required*;
  I did not treat the extra draws as buying anything they do not buy.
- D-4's own stated limit is carried into the artifact: "accept **only if** on
  the curve" is a soundness condition and is *also* satisfied vacuously by a
  constant-reject checker. Completeness is carried by L-BASE's acceptance of
  the base point on that identical path, and by nothing else here.

## 5. Measurements — every quantity **as computed**

Full record with all integers, witness lists and per-base verdicts:
`measurements-block-a.yaml`. Nothing below is assumed, recalled, or transcribed
from any source; every number was produced by
`src/measure_block_a.py` in this run from the capsule whose sha256 is recorded
above. Parameters were read from the capsule only — no parameter was typed from
memory or carried in from another record.

### L-EQ (rank 2) — guarded by CTRL-CONSTRUCTED-SINGULAR, which fired

- **Constant coefficient, exact integer relation.** `int(intake_decimal)` and
  `int(retrieved_hex, 16)` were formed as exact integers and subtracted.
  **Difference = 0; the exact integer equality HOLDS.** The intake decimal has
  68 digits; the retrieved hex has 56 hex digits; the common value has bit
  length 224. INV-6 did **not** fire, so no impediment arises from this lane
  and downstream lanes were interpretable.
  Recomputed as integers, both representations reduce to `4 mod 9` and
  `7 mod 11` — the capsule recorded these as advisory hand computations that
  "prove nothing"; the exact equality above is what settles the reconciliation.
- **Linear coefficient relation.** The linear coefficient `−3` was *parsed* from
  the capsule's intake equation string, not typed. `a − (p + (−3)) = 0`
  exactly, i.e. **`a = p − 3` as exact integers**, hence `a ≡ −3 (mod p)`.
- **Nonsingularity witness, reported as the value:**
  `4a³ + 27b² mod p = 11286604486433664602000942456042078497941322427273965674759527357535`
  (nonzero). Discriminant `−16·witness mod p = 8133954887115844930654026312464158747844254983800706208418026371607`.
- **j-invariant**, `j = 1728·4a³·(4a³+27b²)^{-1} mod p`:
  `20781977079628996477063007379734849057519732242287194936686605794677`
  (hexadecimal form recorded in the YAML alongside it).
  Computed: `j == 0` is **false**; `j == 1728 mod p` is **false**.

### L-FIELD (rank 3) — guarded by CTRL-CONSTRUCTED-COMPOSITE, which fired

- **Prime as an exact identity.** The closed form was *parsed* from the
  capsule's `intake.modulus` string `2^224 - 2^96 + 1` by a parser accepting
  only integer literals and `base^exponent` terms — not typed as a literal.
  Evaluated minus the integer read from the retrieved hex = **0**; the identity
  **holds**.
- **Bit length: 224.** Retrieved hex is 28 bytes.
- **Residues later lanes consume** (computed here, consumed elsewhere; **no
  comparison is performed on them here**): `p mod 3 = 1`, `p mod 4 = 1`,
  `p mod 8 = 1`, `p mod 16 = 1`, `p mod 2^32 = 1`.
- **Probable primality — PROBABLE, never "prime".** Miller-Rabin,
  **32 rounds** = 12 fixed bases (2,3,5,7,11,13,17,19,23,29,31,37) + 20 random
  bases drawn from `random.Random(20260905)`. **The full witness list and every
  per-base verdict are in the YAML.** No base witnessed compositeness →
  verdict **PROBABLE PRIME**. A primality certificate was **not attempted** and
  is OPEN AND UNATTEMPTED (batch.yaml OOS-2). The textbook `4^-rounds` bound
  is stated in the artifact for the random bases only; the twelve fixed bases
  are not independent draws and no bound is claimed from them.

### L-BASE (rank 4) — guarded by CTRL-CONSTRUCTED-RANDOMPOINT and CTRL-CONSTRUCTED-COMPOSITE, both of which fired

- **Base point on the curve.** Two-sided residue comparison on the identical
  `on_curve()` path the null control ran on: `Gy² mod p` and
  `Gx³ + aGx + b mod p` were computed and are **equal**. The independent
  full-integer ground-truth route agrees.
- **Order of the base point, two-sided check.** `n·G =` **point at infinity O**;
  `(n−1)·G =` a **finite** affine point which was further checked to equal
  `−G = (Gx, p−Gy)` exactly. `n` has bit length 224.
  What this establishes, stated exactly: `ord(G) | n` and `ord(G) > 1`.
  `ord(G) = n` follows **only conditional on n being prime**, and n is checked
  here as **PROBABLE PRIME only** — Miller-Rabin, **32 rounds**, 12 fixed + 20
  random bases, full witness list and per-base verdicts in the YAML, on the
  identical code path the constructed composite was rejected on.
- **Hasse-interval uniqueness argument: WRITTEN OUT IN FULL** in
  `measurements-block-a.yaml` under
  `lanes[L-BASE].quantities.hasse_interval_uniqueness.argument` — seven numbered
  steps plus six named silent-failure conditions (F1–F6) and an explicit
  statement of what it does not establish. It is reproduced in the artifact
  rather than summarised here so it travels with the numbers it argues about.
  Computed endpoints:
  - `s = floor(2*sqrt(p)) = isqrt(4p) = 10384593717069655257060992658440191`,
    exact integer square root, **no floating point anywhere in this bound**;
    verified `s² ≤ 4p` and `(s+1)² > 4p`.
  - interval `[p+1−s, p+1+s]` = `[26959946667150639794667015087019620288964199190371051082517407858691,
    26959946667150639794667015087019641058151633329681565204502724739073]`,
    containing `2s+1 = 20769187434139310514121985316880383` integers.
  - sufficient (not necessary) condition `2s+1 ≤ n`: **true**.
  - `k_min = ceil(lo/n) = 1`, `k_max = floor(hi/n) = 1`,
    **count of multiples of n in the interval = 1** — the binding fact.
    INV-7 did **not** fire.
- **Derived group order and cofactor** (derived, not trusted):
  `#E = 26959946667150639794667015087019625940457807714424391721682722368061`
  (bit length 224), `h = 1`, and `n·h` reconstructs `#E`. The capsule's `h`
  field — which the capsule itself labels `retrieved_single_witness` — reads
  `01`, and the **derived** `h` equals it. That agreement is a check of a
  derived quantity against a single-witness retrieved capsule field, which the
  capsule explicitly asked L-BASE to perform; it is not a comparison against any
  criterion threshold and renders no cell.
- **Trace, with Hasse checked, both sides reported.**
  `t = p + 1 − #E = 4733100108545601916421827343930821`;
  `|t| = 4733100108545601916421827343930821`;
  `s = 10384593717069655257060992658440191`; `|t| ≤ s` is **true**.
  Recorded in the artifact as what it is: a **consistency check of the
  derivation**, since `#E` was chosen from inside the Hasse interval — not an
  independent confirmation of `#E`.

### What was NOT measured, and why (every null carries its reason)

| Not measured | Reason |
|---|---|
| false-accept rate of the on-curve checker | Not computable from this control and forbidden to claim from it (D-4). Field present, explicitly `null`. |
| any criterion-cell disposition, any threshold comparison | Out of scope for this slot. S7 alone may compare. |
| primality **certificate** for p or n | OPEN AND UNATTEMPTED (batch.yaml OOS-2). Both are reported as probable only. |
| twist order, embedding degree, CM discriminant, rigidity, ladder/complete/independence residues, rho cost | Other lanes (S5) or out of scope for this batch. |
| whether any of these quantities was previously computed in this program | The knowledge index is empty here (§2). No inference drawn. |

## 6. Comparison against the frozen preregistration (executor role contract §11)

Recorded because my role contract requires a run to be compared against the
frozen pre-registered prediction **exactly as specified, with no conclusions**.
The contract's `preregistered_prediction` is a *pointer* to the archived audit
plan's per-lane `quantitative_prediction` blocks (sha256 `eb1b3399…5c3dcc80`),
which I read **only after** everything in §5 was computed and written. **This is
not the gated comparison**: it compares computed values against a frozen
prediction, not against a criterion threshold or an intake cell, and it renders
no cell.

| Frozen prediction (audit plan) | This run |
|---|---|
| L-FIELD: `p == 2**224 - 2**96 + 1` exactly | identity holds, difference 0 |
| L-FIELD: bit length exactly 224 | 224 |
| L-FIELD: `p mod 4 == 1` | 1 |
| L-FIELD: "p is prime" | **not established.** Reported as PROBABLE PRIME, 32 rounds. The prediction's claim strength exceeds what this run may assert. |
| L-EQ: the 68-digit intake decimal equals `int(b_hex,16)` exactly | equality holds, difference 0 |
| L-EQ: `a == p - 3` exactly | holds, difference 0 |
| L-EQ: `(4a³+27b²) mod p != 0` | nonzero (value in §5) |
| L-EQ: j neither 0 nor 1728 | `j == 0` false, `j == 1728 mod p` false |
| L-BASE: `Gy² ≡ Gx³+aGx+b (mod p)` | holds |
| L-BASE: "n is prime (**certificate**), bit length 224" | bit length 224. **No certificate was produced** — OOS-2. PROBABLE PRIME, 32 rounds. |
| L-BASE: `n·G == O`, and `G != O` | `n·G = O`; `(n−1)·G` finite and `= −G`, so `G != O` |
| L-BASE: Hasse interval contains exactly one multiple of n, giving `#E = n`, `h = 1` | count = 1, `#E = n`, `h = 1` |
| L-BASE: derived h agrees with the single retrieved witness `h = 1` | agrees |
| L-BASE: `t = p + 1 − n`, `|t| ≤ 2*sqrt(p)`, reported exactly | `t = 4733100108545601916421827343930821`, `|t| ≤ s` |

Two prediction elements are **not met by this run and are recorded as such**:
the audit plan asserts primality of `p` and a **certificate** of primality for
`n`; this run produces probable primality only, with round counts and witness
lists, and no certificate. That is a scope limit of this slot, not a
disagreement about a value. **I draw no conclusion from any row above; the
prediction is frozen and I neither adjust nor re-score it.**

## 7. Reproduction, parse-check and independent cross-check

- **Parse-check.** Both emitted YAML documents were loaded with
  `yaml.safe_load` and traversed. Both parse.
- **Round-trip fidelity.** Every `*_as_read` string was re-parsed and asserted
  to reconstruct its recorded integer (`int(hex,16)`, `int(decimal)`). All pass.
- **Clean-start reproduction (contract INV-3).** Both documents were regenerated
  from a fresh process with a **stripped environment** (`env -i`) and from a
  **different working directory** (`/` and `/tmp`), and compared with `cmp`:
  **byte-identical**.
  `sha256(controls-block-a.yaml) = 9ece40348d80deb983bb22a90d272d33e0f6fd38bc8f21bb96ff9d3afe0c53cf`
  `sha256(measurements-block-a.yaml) = b23dc73e4e045f9bdbe0a99d4623118f3e58d078b62baefdf8c20ba883e1aaf0`
  The documents carry no timestamp and no host-dependent field precisely so that
  this equality is meaningful; session facts live in this report instead.
- **Independent cross-check** (not a deliverable; run in scratch, outside the
  write scope, and reported for what it is). Every load-bearing quantity was
  recomputed by a separately written program sharing **no code** with
  `measure_block_a.py`: **Jacobian** coordinates instead of affine, an
  **MSB-first** ladder instead of LSB-first, and a **disjoint** Miller-Rabin
  base set (41…113, 18 bases). It agreed on: the constant-coefficient equality,
  `a = p−3`, the closed-form identity for p, the bit length, `G` on curve,
  `n·G = O`, `(n−1)·G = −G`, `s`, the multiple count = 1, `#E`, `h = 1`, `t`,
  the nonsingularity witness value, the j-invariant, and probable primality of
  both `p` and `n`. **This is replication of my own reasoning, not a blind
  re-derivation** — I wrote both programs and had read the pre-read
  expectations in §3. Its value is bounded accordingly; the blind re-derivation
  is C-8's, at S9/S11/S12.

## 8. Runs, budget and environment

| # | Command | Purpose | Exit | Wall |
|---|---|---|---|---|
| 1 | `python3 src/measure_block_a.py --emit both` (to scratch) | first full execution | 0 | 0.186 s |
| 2 | `… --emit controls > controls-block-a.yaml` | emit control document | 0 | <1 s |
| 3 | `… --emit measurements > measurements-block-a.yaml` | emit measurement document | 0 | <1 s |
| 4 | `… --emit controls > controls-block-a.yaml` | re-emit after the emitter fix in §9 | 0 | <1 s |
| 5 | `… --emit measurements > measurements-block-a.yaml` | re-emit after the emitter fix | 0 | <1 s |
| 6 | `cd / && env -i /usr/bin/python3 … --emit controls` | clean-start reproduction | 0 | <1 s |
| 7 | `cd /tmp && env -i /usr/bin/python3 … --emit measurements` | clean-start reproduction | 0 | <1 s |

**7 runs of the measurement source against a ceiling of 20.** Runs 1–3 are
retained and reported although their output was superseded by the emitter fix;
none was discarded and none was rerun in search of a different result — the
arithmetic is identical across all seven, and only the YAML quoting of two
string fields changed. Peak memory was far below the 2 GB ceiling (the largest
integers are a few thousand bits). Total wall clock for the whole slot,
including reading and writing, was a small fraction of the 1200 s ceiling; no
stopping rule fired. STOP-3's single-deterministic-pass-per-lane rule was
honoured: no lane was retried.

- Host: `Linux-6.18.44-fc-v24-x86_64-with-glibc2.39`; CPython 3.11.15.
- Repository commit at execution: `ea308c2d49dbdba06c08febc645bae2f36ed9250`
  (`e6ca74c75`, the commit named in the dispatch, is its ancestor).
  Dirty-tree state: clean apart from this task's own untracked directory.
- Dependencies used: Python standard library only (`hashlib`, `math`, `random`,
  `re`, `os`, `sys`, `argparse`), plus **PyYAML for reading the capsule**. The
  source carries a stdlib-only regex fallback for that read; the fallback was
  **not** exercised in these runs (`capsule_parser: PyYAML safe_load` is
  recorded in both documents) and so is **untested code** — noted in §10.
- No network. No PARI/gp/cypari/cypari2/Sage. Nothing named `bedrock`.

### Inference provenance

| Field | Value |
|---|---|
| `requested_policy` | `executor-implementation` (from the handoff; `fallback_allowed: false`, `degraded_allowed: false`) |
| adapter resolution, run here | `python3 -m orchestration.adapter resolve --role executor` → `executor-implementation -> anthropic:claude-sonnet-5 (effort=medium)` |
| model that actually answered | `claude-opus-5`, as self-reported by the runtime to this session |
| `model_verified` | **false** — no `doctor --probe` was run (it would have made a provider request, and none was needed for this slot) |
| `reasoning_effort` | policy default `medium`; `.claude/agents/executor.md` carries `effort: medium`. The effort this session actually ran at was **not verifiable from inside it**. |
| `fallback_used` | **false** — no fallback was requested or taken |
| `degraded_requirements` | **none.** The policy requires `reasoning_effort: medium`, tool use, structured output, ≥120k context, ≥24k output; nothing was missing. |

**The resolved-binding mismatch is recorded, not smoothed over** — see D-2 in
§10. I did not refuse on it, because refusal is owed to a *downgrade* and no
policy requirement went unmet; that judgement is the Coordinator's to confirm or
overturn.

## 9. Protocol deviations

**One, and it is an implementation defect I found and repaired before
finalising, with every run retained.**

- **DEV-1 — YAML emitter did not round-trip two string fields.** The first
  emitted pair of documents (runs 2–3) wrote the capsule's `h` field as
  `capsule_h_field_as_read: 01`, which `yaml.safe_load` reads back as the
  **integer 1**, and the intake decimal as a bare digit string, which reads back
  as an **integer**. Both destroy the "as read" fidelity these records exist to
  carry. Found by my own parse-check, not by inspection. Repaired by quoting any
  string a YAML resolver would resolve to a non-string, and both documents were
  regenerated (runs 4–5) and re-verified. **No computed quantity changed**; the
  defect was in serialisation only. The defective outputs were overwritten in
  the working tree before any commit and were never archived; runs 2 and 3 are
  reported here rather than omitted.

No other deviation from the approved protocol. In particular: the controls ran
first and on the identical code paths; no lane was retried; no comparison
against a threshold or an intake cell was performed; no parameter was typed from
memory; nothing outside the declared `write_scope` was written; nothing was
committed or staged.

## 10. Unresolved defects and observations for the Coordinator, Validator and Red Team

Reported as defects with their exact repairs rather than guessed at. Four slots
in this batch have reported real defects and every one was right; these are
offered in that spirit and none of them blocked this slot.

- **D-1 — A FIFTH PREDICTION LEAK, beyond the one C-7 discloses.**
  `batch.yaml`'s own S3 deliverables text states two expected outcomes outright:
  that the linear coefficient "a equals p − 3" and that the "j-invariant
  [is] neither 0 nor 1728". The parameter capsule adds the word-level argument
  that `p` equals its closed form, the advisory `mod 9` / `mod 11` residues for
  the constant coefficient, and "p = 1 mod 4" under
  `derived_quantities_to_be_certified`. **These are in files the slot is
  required to read before running, so unlike `audit-plan.yaml` they cannot be
  removed from the producer's inputs.** C-7 addresses only the audit plan and
  DEC-20260905-f630e4 rules only its D-1 through D-4, so this is unruled.
  *Exact repair:* a new record ruling whether the C-8 blind re-derivation's
  `blind_from` must additionally list `batch.yaml` and `parameter-capsule.yaml`
  for the four quantities named above. It cannot list the capsule wholesale —
  the re-deriver needs the parameters — so the repair is per-field, and a
  reviewer should treat that as the interesting part. **This is a disclosure
  about instruments and texts, not about any curve.**
- **D-2 — Requested policy and resolved binding disagree.**
  `orchestration/model-bindings.yaml`, via the adapter, binds
  `executor-implementation` on this runtime to `anthropic:claude-sonnet-5`,
  while the model that answered this session self-reports as `claude-opus-5`,
  with `fallback_allowed: false` in the handoff. No policy *requirement* went
  unmet, so this is not the silent downgrade AGENTS.md forbids; but it is an
  undeclared substitution and `model_verified` is `false`.
  *Exact repair:* a Coordinator ruling on whether an upward substitution
  requires an `inference_amendment`, and a `doctor --probe` in a session that
  is permitted to make one. **It is not mine to rule on and I did not.**
- **D-3 — The knowledge index is empty in this worktree**, so the retrieval
  obligation was attempted and answered with nothing (§2). *Exact repair:*
  `make -C kb qdrant-up`, set `CRYPTO_KB_QDRANT_URL` in `kb/.env`, then
  `crypto-kb stage-repo . && crypto-kb ingest`. Until then every producer in
  this batch discharges the obligation by recording an empty index. **Absence of
  a hit licenses no inference**, here or in any successor slot.
- **D-4 — `search_knowledge` was not exposed to this subagent session.** The
  obligation names an MCP tool this session did not hold; it was discharged
  through the same index's CLI instead. *Exact repair:* either bind the MCP
  server into executor subagent sessions or amend the obligation's wording to
  name the capability rather than the tool.
- **OBS-1 — The stdlib fallback capsule reader is untested code.**
  `read_capsule()` falls back to regex parsing if PyYAML is unavailable; PyYAML
  was available, so the fallback never ran. A later reproducer without PyYAML
  would exercise an unexercised path. *Exact repair:* either exercise it under a
  successor task, or delete it in a successor implementation so the dependency
  is honest. I did not change it here because the source is a deliverable of an
  approved protocol and I am not the party who may enlarge it.
- **OBS-2 — The stale record C-5 warned about is still stale.**
  `…/BATCH-ef5b1e/tasks/TASK-20260824-4af491/task.yaml` still reads
  `state: queued` with an empty archive block beside a completed receipt. I
  re-verified the digest against the receipt *and* against the committed blob at
  `5c3bfe273070…` rather than trusting either (§1), so it did not block. It is
  named again so it is not rediscovered as a surprise. Not mine to edit.

## 11. What this slot did not and may not say

- It adjudicates **no criterion cell** and compares **no measured quantity
  against any threshold or intake cell**. That is S7's, behind a gate this slot
  does not open.
- It states **nothing about any curve's security, in either direction**.
  Arithmetic verification of a published parameter set is a transcription check.
- It calls **nothing** proven prime. Both primality verdicts are **probable**,
  with round counts and full witness lists, and no certificate was attempted.
- It declares **no hypothesis** supported, rejected or closed, and **no**
  heuristic validated or refuted. This goal has no hypothesis and this record
  creates none.
- The derived `#E`, `h` and `t` hold **conditional on F1–F6** of the written-out
  uniqueness argument, chiefly on the probable primality of `p` and `n`, and
  transfer to **no other curve** without re-running: the uniqueness route
  depends on a regime condition (`2s+1 ≤ n`, count = 1) that must be recomputed
  anywhere else.
- Nothing here is durable research state until the S4 snapshot archive
  (TASK-20260904-fa10f7) commits and pushes it and the post-commit verifier
  accepts it. **I committed and staged nothing.**
- **On the four forbidden words.** batch.yaml forbids writing "safe", "unsafe",
  "vulnerable" or "secure" about any curve, and in the same breath requires the
  claim ceiling to be carried **verbatim**, which itself contains "SAFE OR
  UNSAFE". The two obligations are satisfied together in exactly one way and
  that is what was done: every occurrence of any of those words anywhere in
  these four deliverables is either inside the verbatim claim ceiling or inside
  an explicit statement that no such claim is being made. **No occurrence
  asserts anything about any curve.** A reviewer can confirm this with one
  `grep -rniE '\b(safe|unsafe|vulnerable|secure|security)\b'` over the task
  directory; there are twelve hits and all twelve are of those two kinds.

## 12. Postscript — housekeeping observations, recorded rather than dropped

- **A `__pycache__` directory was created inside `src/` by my own
  `python3 -m py_compile` syntax check and was deleted before this report was
  finalised.** It is named here because an undeclared file inside the task
  directory would fail the S4 archive's declared-path-equality check, and a
  reviewer should be able to see that it existed and was removed rather than
  wonder. The final artifact set is **exactly the four declared paths and
  nothing else**, verified with `find`.
- **Final digests of the four deliverables**, recomputed after every edit:
  - `controls-block-a.yaml` `9ece40348d80deb983bb22a90d272d33e0f6fd38bc8f21bb96ff9d3afe0c53cf`
  - `measurements-block-a.yaml` `b23dc73e4e045f9bdbe0a99d4623118f3e58d078b62baefdf8c20ba883e1aaf0`
  - `src/measure_block_a.py` `23fb2ff68a6010aa1376afc418083a7b3f93ba9044226a7e9e9905214d0383be`
  - `report.md` — self-referential, so not stated here; S4 recomputes it from
    the committed blob, which is the only value that binds anything.
- **Nothing was committed, staged, pushed, merged, or opened as a pull request
  by this slot**, and no identifier was minted. The task directory is untracked
  in the working tree, exactly as handed over. S4 (TASK-20260904-fa10f7) is the
  slot that commits.
