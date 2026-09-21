# BATCH-aeeb17 — exotic-axis ideation for GOAL-ENDO-001

- Goal: `GOAL-ENDO-001`
- Batch: `BATCH-aeeb17`
- Opened: 2026-08-11
- Authority: Coordinator. **This batch creates no evidence and moves no hypothesis status.**
- Kind: ideation only. Five `idea-generator` producers, no execution, no compute.
- Predecessor batches: `BATCH-cb71b5`, `BATCH-523510`, `BATCH-aa267f`, `BATCH-de621d` (closed), `BATCH-d7e255` (open, separate branch / PR #331)

## 0. Relationship to BATCH-d7e255 — NEITHER SUPERSEDES THE OTHER

`BATCH-d7e255` is **open on a different branch** (`feat/ecdlp-isogeny-experiments-f2eeb3`,
PR #331) and is an **execution** batch: EXP-INSTR-36c8cf amendment v3, the SR3
ladder, EXP-ICINV-e0cd8f's infrastructure block. `BATCH-aeeb17` is an
**ideation** batch and touches none of those objects. It:

- executes nothing, runs no experiment, and consumes no run identifier;
- adjudicates nothing that `BATCH-d7e255` has open;
- resolves neither blocker B1 nor B2, and unpauses no lane;
- files proposals only, which are official solely after a Coordinator ledger
  archive and post-commit verification.

`current_batch_id` on the goal head is **not** claimed by this batch. The two
batches run concurrently by design, exactly as `BATCH-d7e255` and `BATCH-de621d`
did on 2026-08-10; the sharded checkpoint layout is what makes that safe.

## 1. Why this batch exists

The user asked for novel, exotic, publication-grade directions for the
endomorphism campaign. The campaign's honest state as of this opening:

- 14 lanes are fixed in `analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md`.
- **146 committed proposals** already reference this goal or its lanes.
- The gating lane `RQ-ICINV-475b5e` is **paused**, and the campaign's recent
  batches have been consumed by instrument calibration at toy scale
  (`p` = 4001 / 6007) rather than by mechanism search.
- `DECOMPOSITION.md` §5 records, pre-registered, that the campaign's *most
  likely genuine deliverable is a negative* in L1.

A campaign converging on a negative is a legitimate outcome and this batch does
not exist to overturn that by wishing. It exists because of a **structural**
observation about the decomposition itself, which is this batch's own
pre-registered hypothesis about where generation has been thin:

> **The fourteen lanes are indexed by RESOURCE (R1–R8) applied to a single
> curve's ECDLP instance.** Generation has therefore been dense in
> "resource × one curve's point group" and sparse in objects that the indexing
> cannot express.

That is a claim about *coverage of the idea space*, not about mathematics, and
it is falsifiable in review: if the novelty screens show these axes were already
covered, the batch's finding is that the space is saturated — which is itself
worth knowing and is an accepted deliverable under
`docs/inventor-protocol.md`'s closure standard.

## 2. The five axes, pre-registered before any generation

| Axis | Task | Central object (NOT "lane") | Lane of record |
|---|---|---|---|
| **A1** | `TASK-20260811-5ff234` | The quadratic-twist **pair** `(E, E^d)`, the shared x-line `P^1 = E/±`, the Kummer line, `E(F_p)` as a possibly-non-cyclic group, cosets — plus an audit of the **scope boundary of the admissibility filter itself** | `RQ-ICINV-475b5e` |
| **A2** | `TASK-20260811-6ca12c` | The **reduction** as deliverable: ECDLP ↔ `Cl(O)`-vectorization in *both* directions with quantifier order explicit; or a black-box **barrier theorem** | `RQ-CLGP-b99df5` |
| **A3** | `TASK-20260811-f58f22` | The **whole isogeny class** (`h(O) ~ p^{1/2+o(1)}` curves sharing one `N`) as one algorithmic object: advice/preprocessing charged against Corrigan-Gibbs–Kogan, Bernstein–Lange, AT² | `RQ-MTGT-2cabee` |
| **A4** | `TASK-20260811-c439c2` | The **simulator** as a mathematical object: constructively locate the weakest non-simulable oracle; is the x-coordinate-as-field-element oracle (R1) provably non-simulable, and where is the crossover? | `RQ-GGMB-6eaabc` |
| **A5** | `TASK-20260811-6d56a7` | **Imported machinery**: `Φ_ℓ(j,j')` / modular curves as the index-calculus *surface*; function-field and Drinfeld analogues that already work; the ordinary shadow of the quaternion method behind the `p^{1/3+o(1)}` exemplar | `RQ-JINV-8fc13a` |

Axes are assigned to an existing lane **of record** for filing purposes only.
No axis reopens, readjudicates, or unpauses its lane.

## 3. Standing constraints inherited, all in force

Transcribed into every one of the five handoffs, verbatim:

1. **`H-ENDO-001` is the admissibility filter and is NOT retested.** Every
   endomorphism acts on `G` as a scalar; a proposal whose only use of `φ` is to
   apply it to points of `G` is inadmissible on its face.
2. **`KN-FIND-b7e091` is BINDING and is extended, never revisited.**
3. **`H-STR-002` is `weakened`; `DEFER-BATCH009-001` is OPEN.** Goal pause
   condition **P2** fires on any result bearing on it in either direction.
   φ-stable-factor-base proposals must be flagged P2-adjacent.
4. **Pause condition P3.** A candidate appearing to exceed the
   automorphism-discounted rho baseline is flagged and stopped, never stated.
   `sqrt(6)` (`KN-TECH-018`) is baseline calibration, never an exponent.
5. **Core rule 5** — no fabricated commands, outputs, timings, statistics,
   citations or runs. These are proposals, not evidence.
6. `claim_tier: toy`; `sota_delta: 0`; `dominated_by` populated honestly against
   parallel Pollard rho at `0.886·sqrt(N)` with `O(1)` memory.
7. Mandatory novelty screen against the 146-proposal corpus, checked in review.

## 4. What this batch may and may not conclude

**May:** that an axis is live and worth a contract; that an axis is closed with a
named obstruction, argument, and forward guidance; that the idea space is
saturated.

**May not:** any statement of attack, speedup, or exponent; any hypothesis
status change; any completion criterion; any attestation or quorum. Criterion
C1 is explicitly **not** met by ideation — C1 requires an executed, independently
reviewed run or an archived closure decision per lane.

## 5. Review plan, declared before producers run

Producer output is snapshot-archived, then read by **independent** sessions that
did not originate it (`review-adversarial`, xhigh):

- **Validator** (`TASK-20260811-845cc4`): novelty screens actually performed and
  correct against the 146-record corpus; admissibility-filter compliance;
  schema conformance; null objects present; `sota_delta`/`dominated_by` honesty.
- **Red Team** (`TASK-20260811-029a6c`): hidden assumptions, omitted end-to-end
  costs, quantifier slippage in A2/A3, and the cheapest falsification of the
  most attractive proposal in the batch.

A proposal that survives neither review is filed as `proposed` and not
recommended; nothing in this batch is promoted to a hypothesis without a
subsequent Coordinator decision.

## 6. Honesty statement

Nothing in this batch is an attack on any deployed curve. No lane here has
produced any speedup and none is claimed. `sota_delta`: zero. The batch's
plausible outcomes are ranked, before generation, as: (a) most likely — several
axes return well-argued closures with named obstructions, adding citable
negatives; (b) plausible — one axis (A3 or A4) yields a compute-free theory
target worth a contract; (c) least likely and not assumed — a live mechanism.
Ranking these in advance is what keeps (c) from being read into whatever comes
back.
