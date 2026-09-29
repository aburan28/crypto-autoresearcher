# J3 cost, liveness, and proves-too-much red-team report

```yaml
red_team_report:
  id: TASK-20260824-a19a05
  task_id: TASK-20260824-a19a05
  claim_under_review: J3 concrete decomposition, scalable liveness, hidden storage, and proves-too-much controls only
  joint: J3-concrete-decomposition-scalable-liveness-and-proves-too-much
  joint_verdict: breaks
  whole_claim_verdict: null
  objections:
    - The symbolic record and peak-extra widths are inconsistent with the registers that the source actually allocates; the toy width is the unique collision point for the two formula pairs.
    - The selected point payload is not loaded into circuit wires. It is read from a host-side table while the exhaustive gate list is generated, so payload traffic is replaced by compiled circuit-description cost.
    - Equality routing and affine translation are exhaustive basis-permutation tables, not scalable equality and field-arithmetic primitives.
    - High-control MCX decomposition, its ancilla tradeoff, and its uncomputation schedule are absent.
    - The payload-row runner expected the wrong failure-marker cardinality and stopped before serializing its mirror-negative result.
  required_controls:
    - Derive widths from register objects at a non-colliding window width rather than asserting symbolic strings.
    - Require every host-selected point value used after logical qROM load either to inhabit declared live wires or to be charged as compiled table and gate traffic.
    - Replace self-declared structural markers with an IR-level check for run-time classical label branching.
    - Mutate generic and exceptional arithmetic separately rather than deleting an entire label block.
  counterexample_or_mutation: A width-four construction has an actual record width of nine and actual extra-clean width of sixteen, contradicting the archived symbolic values of ten and seventeen; the same check also exposes that the point payload is absent from the wire set.
  baseline_comparison: The finite materialized permutation is fully enumerable at the toy instance, but its operation count grows with the label count and valid-point count and therefore is not a scalable arithmetic cost model.
  heuristic_challenges: []
  cost_model_challenges:
    - The recorded finite totals are reproducible, but their scalable transfer is not.
    - Logical qROM use is an interval label rather than a payload-bearing gate operation.
    - Host compilation, circuit description, high-control MCX realization, and scalable arithmetic workspace are uncharged.
  reduction_and_scope_challenges:
    - The archived producer run is terminal failed_implementation; its finite observations are not scientific evidence.
    - The leading 3n+O(log n) preservation is withheld because the end-to-end scalable decomposition is missing.
  proof_architecture_challenges:
    - The non-colliding width control breaks the symbolic liveness statement.
    - The payload-provenance control breaks the inference from no allocated payload register to no payload cost.
  narrowest_supported_statement: Static source inspection and one deterministic J3 control reproduce the finite toy IR counts and expose a fully closed cleanup schedule for the wires that are actually declared; they do not complete the failed producer package or establish scalable composition.
  next_concrete_action: Open a Coordinator-approved successor that computes symbolic widths from register definitions, gives a payload-bearing qROM or explicitly charges compiled-table traffic, supplies scalable generic and exceptional arithmetic plus MCX ancilla schedules, and reruns corrected known-false controls under a fresh budget.
  artifact_paths:
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-a19a05/cost-liveness-red-team.md
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-a19a05/controls-results.json
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-a19a05/review-attestation.yaml
    - coordination/goals/GOAL-ECDLP-001/proposals/QEC-LABEL-BLOCK-QROM-CORRECTION-20260824-1e8b78/tasks/TASK-20260824-a19a05/receipt.json
```

## Scope and evidence boundary

This report owns J3 only. It does not decide the full review round. The producer package is an immutable, Coordinator-snapshotted `failed_implementation` package: five tests passed and the payload-row known-false test stopped on a marker-cardinality assertion. A failed implementation is not evidence for or against a mathematical hypothesis. The one J3 execution was a deterministic count/width/control check with zero scientific experiments and no file output.

All source references below have `internal` provenance. The source bytes, producer records, and snapshot receipt match the reachable snapshot commit declared by the queue.

## Concrete finite decomposition

For the toy parameters, the accumulator has seven bits, the label has three bits, and the loaded handle has eight bits. An arithmetic adjacent swap therefore has

\[
1\;\text{route}+3\;\text{label}+8\;\text{handle}+6\;\text{non-target accumulator}=18
\]

controls. An input or cleanup comparison has

\[
1\;\text{enable}+3\;\text{label}+7\;\text{handle excluding valid}+7\;\text{accumulator}=18
\]

controls. Every zero-valued control is opened and closed by an adjacent pair of X operations around its MCX; there is no persistent negative-control workspace.

| Phase | Explicit finite decomposition | Count |
| --- | --- | ---: |
| derive effective enable | negative-open X, two-control MCX, negative-close X | 2 X + 1 MCX(2) |
| qROM load | copy address/sign, then set valid plus four check bits | 3 CX + 5 X |
| input equality routing | eight labels times seven valid points | 56 MCX(18) + 880 X |
| route selection | XOR five one-hot flags into route | 5 CX |
| translation permutation | eight label blocks, 34 adjacent-swap MCXs per block | 272 MCX(18) + 3808 X |
| route unselection | reverse the five route toggles | 5 CX |
| output equality cleanup | eight labels times seven translated valid points | 56 MCX(18) + 880 X |
| qROM unload | exact reverse of load | 3 CX + 5 X |
| uncompute effective enable | reverse the first pattern gate | 2 X + 1 MCX(2) |
| **total** | | **5582 X + 16 CX + 384 MCX(18) + 2 MCX(2) = 5984** |

The 272 translation count has an independent closed-form reconstruction. Every nonzero selected addend acts as one seven-cycle on the seven valid points. The Hamming-distance multiset from the chosen cycle origin to the six other encoded points is `{2,2,3,4,4,5}`. A transposition at distance `d` uses `2d-1` adjacent Gray swaps, hence

\[
(3+3+5+7+7+9)=34
\]

MCXs per label block, and `8*34=272`. The J3 deterministic check also counted 34 arithmetic MCXs for each of the eight label keys.

The route comparisons split, per direction, into eight O, eight A, eight -A, eight -2A, and twenty-four generic MCXs. All five flags are combined into one route bit and then drive the same exhaustive translation permutation. There is no distinct generic field-arithmetic core or exceptional arithmetic mux to cost: the branch names classify the input, but the emitted arithmetic is one materialized truth-table permutation.

Source basis: `src/label_block_qrom_backend.py` lines 175-200, 203-218, 238-246, 281-304, and 306-367; producer count records: `resource-accounting.json` and `run/results.json`.

## qROM and hidden work

The load does not select point coordinates. It copies the `w` label bits into `qrom_address` and `qrom_sign`, then sets one valid bit and four constant check bits. Thus the implemented handle width is

\[
(w-1)+1+1+4=w+5,
\]

not `2w+2`. The reported logical use has no separate gate operation. Instead, the host generator reads `table[key]` to construct comparisons, cycles, and every controlled adjacent swap. The point payload is therefore embedded in the gate list rather than present in a live circuit register.

That embedding is valid for a finite semantic oracle, but it creates omitted scalable costs. With `L=2^w` labels and `N` valid points, the equality layer emits `2LN` MCXs, each with `2n+2w+6` controls. The translation layer emits a table-dependent sum of Gray swaps and is at most order `L*N*n` high-control MCXs for this construction. Circuit-description generation and repeated use of host-selected payload bits are not qROM traffic and are not charged by the reported one-load/one-use/one-unload labels.

The source also treats every `2n+2w+6`-control MCX as atomic. No clean/dirty-ancilla realization, gate-depth tradeoff, or cleanup schedule for those decompositions is supplied. Hence `arithmetic_work: 0` describes only the finite IR abstraction.

Source basis: `src/label_block_qrom_backend.py` lines 203-246, 315-365, and 481-517.

## Scalable peak-live schedule

The wires actually declared by the source give this schedule:

| Interval | Live non-data registers | Cleanup event |
| --- | --- | --- |
| effective-enable derivation | effective enable | final inverse pattern gate |
| qROM load through unload | handle of `w+5` bits | exact reversed load |
| input comparisons through output cleanup | five comparison flags | output-state comparisons |
| route selection through unselection | one route bit | reverse five CXs before flag cleanup |
| arithmetic | no declared arithmetic-work wire | none needed in the finite IR abstraction |

At the arithmetic peak, all of the first four groups coexist. Actual extra clean width is therefore

\[
1+(w+5)+5+1=w+12.
\]

Including the label, zero/enable inputs, and `2n+1` accumulator, the module has `2n+2w+15` declared wires. There are no declared dirty ancillae.

The archived strings instead state handle `2w+2` and extra clean `2w+9`. At `w=3`, both pairs evaluate to eight and fifteen, masking the mismatch. J3's single deterministic check produced:

| w | actual handle | archived handle formula | actual extra | archived extra formula | actual total wires |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 7 | 6 | 14 | 13 | 25 |
| 3 | 8 | 8 | 15 | 15 | 27 |
| 4 | 9 | 10 | 16 | 17 | 29 |

The same check found nontrivial MCX arities 16, 18, and 20 at those widths, exactly matching `2n+2w+6` for the fixed `n=3` curve.

No n-bit payload register is explicitly allocated in this IR. That narrow fact holds. It does not prove that a scalable payload-bearing lookup and complete arithmetic avoid such storage, because both are externalized into the host-generated gate list. The required end-to-end decomposition is therefore absent, and leading `3n+O(log n)` preservation is withheld.

## Proves-too-much controls

1. **Payload-row iteration:** the mutation sets `copies` to the payload multiplicity. Each aliased label block therefore applies `T_A` twice. J3 directly checked both alias pairs: each returned four helper markers, two per branch (wrong translation and dirty comparison cleanup). The labels themselves remain controlled by the original label prefix; the helper's `labels_unchanged: false` is merely `not failures`, not a direct label-mutation measurement. The producer runner expected two aggregate markers and stopped before serializing its mirror-negative record. The known-false object is rejected, but the frozen runner is still failed.
2. **No-op backend:** empty operations leave 56 enabled valid cases untranslated. The semantic domain check and empty-operation structural check reject it.
3. **Run-time classical label loop:** the mutation changes only a metadata Boolean and leaves the correct coherent operations intact. The method rejects it solely because the mutation self-identifies. This is a marker check, not an adversarial IR test; an undeclared classical branch would evade this check.
4. **Missing unload:** removing the unload leaves the handle dirty for all 4096 basis inputs. Structural and cleanup checks reject it.
5. **Irreversible label canonicalization:** an appended X on an address wire changes every tested label. Label/domain checks reject it in all 4096 cases.
6. **Partial arithmetic:** the mutation deletes the entire arithmetic block for key `(0,0)` and the exhaustive domain check records seven failures. This rejects the coarse mutation, but it does not separately test deletion of only a generic path or only an exceptional path.

The acceptance method rejects all six declared objects, but two limitations remain load-bearing: the classical-loop control is metadata-tautological, and the partial-arithmetic control is coarser than the named generic/exceptional distinction. The payload-row behavior was directly observed by J3, while the producer's frozen serialization remains incomplete.

## Cheapest next falsification control

Add one parameterized source-level test at `w=4` that derives handle and peak widths from the register objects and enforces a payload-provenance invariant: after logical load, any selected point value that influences arithmetic must either occur in declared live wires or be charged as compiled-table gate traffic. This single test fails the present symbolic formulas and the present payload-free logical-use model before any exhaustive domain run. A successor can then add separate one-gate deletions for generic and exceptional paths and an IR-level classical-branch detector.

The measured obstruction can still be useful: the fully compiled permutation is a compact finite semantic oracle and regression fixture. It is not a scalable cost witness.

