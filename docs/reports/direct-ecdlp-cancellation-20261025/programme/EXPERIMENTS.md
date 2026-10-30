# Classical ECDLP experiment programme

25 October 2026. Prospective designs, mathematical controls and implementation checks; **no admitted scientific trials or attack advantage**. This follows [the research plan](../PLAN.md). Classical CPU/GPU algorithms only. Factor-base relation collection, index calculus, quantum algorithms and quantum simulation are outside this programme.

## Coverage and purpose

Cover the direct tagged-response proposal and all nine classical lead families named in the plan. [LEADS.md](LEADS.md) gives a separate card for each family. This is exhaustive coverage of that named list, not of the literature, every repository branch, or all possible algorithms. An experiment can exhaust a finite, frozen search grammar; it cannot exhaust an unspecified mathematical idea.

The desired research outcome remains a constructive, previously untested EC-specific algorithm. Its novelty and complexity are unverified. Collecting reproducible ordinary, unusual, negative or inconclusive observations is also a valid study outcome. Correct execution, mathematical falsification and competitive performance are separate questions.

Several originals, including IDEA-050, IDEA-111, IDEA-156 and IDEA-379, were formulated for factor-base/index-calculus pipelines. Their original pipelines are excluded. Their cards describe explicitly different direct-inversion successors whose missing constructions remain visible. A proved obstruction is a control to reproduce and respect; it is not a reason to rerun the same algorithm under a new name.

## Outcome vocabulary

Each trial reports one execution outcome: `complete_valid`, `wrong_output`, `timeout`, `memory_limit`, `invalid_input`, `infrastructure_error`, or `not_executable`. Preserve every attempt, including failed searches and constructor failures. A counterexample falsifies its exact universal identity; a timeout does not. No outcome automatically changes an official lead or hypothesis status.

Distinguish five research milestones:

1. **Encoding correctness:** exact agreement with an independent reference, including exceptional cases and unique witnesses. This qualifies the instrument only.
2. **Observation:** a frozen statistic with its inputs, reference, uncertainty and all outcomes. An anomaly is unnecessary.
3. **Mechanism correctness:** an explicit public constructor, an identity or invariant with exact domain, and closure under composition. One counterexample rejects that version.
4. **Scoped performance:** measured complete costs against matched baselines. A local reduction is labeled local; it is not a solver gain.
5. **Novel algorithm or asymptotic claim:** additionally requires prior-art collision review, independent reconstruction, a uniform algorithm and a justified time/memory analysis. A short size ladder cannot establish an exponent.

## Shared input and blinding contract

**Development fixtures already implemented** are listed in [CHECKS.md](CHECKS.md). They are tiny synthetic unit-test inputs, not the registered scientific cohort below.

**Prospective discovery cohort:** subgroup bit lengths 8, 10 and 12; four curves per length; exhaustive canonical scalars. **Prospective confirmation cohort:** six fresh curves at each of 12, 14, 16 and 18 bits, eight independently drawn uniform scalars per curve: 24 curves and 192 random targets. Keep the forced scalars 0, 1 and r−1 and exceptional arithmetic cases in a separate correctness suite; do not replace random performance targets with them. The two cohorts have disjoint curve IDs and generator domains. These exact scientific inputs have not yet been generated or registered.

Before admission, register each (p,a,b,#E,r,h,P), canonical point encoding, subgroup and field certificates, curve-family stratum, generation seed/algorithm, rejection history and content digest. For these sizes, exact point enumeration can certify #E, trial division can certify primality, and [r]P=O with P≠O certifies the prime subgroup order. Check nonsingularity, odd p, r prime, r≠p, #E≠p and exact cofactor h=#E/r. Specify the public registry authority; do not silently invent canonical IDs.

Freeze a deterministic hash-stream rejection sampler and its accepted/rejected records, rather than choosing curves after inspecting results. The main stratum is ordinary non-anomalous curves with j different from 0 and 1728; special-j, special-prime, supersingular or extension-field families require separately registered strata and matched baselines. Describe the induced sampling distribution; it is not uniform over all elliptic curves. Include a nontrivial-cofactor fixture and targets outside the subgroup as rejection/zero-response controls.

Freeze and publish the constructor, compiler options, grammar, elimination schedule policy, stopping rule and input-manifest hashes before opening confirmation targets. An input custodian generates synthetic public Q values and keeps k, scalar-derived filenames and reverse lookup tables outside the candidate process. An output checker alone uses the truth. Record custody and process access. A public seed that reconstructs k is not a blind target. If isolation is unavailable, call the test non-blind. A new method version gets a fresh confirmation cohort; do not retune on its held-out results.

Curves are the replication units. Eight targets on one curve share setup and arithmetic and are not eight independent curves. Report per-curve summaries and every target. Use a curve-cluster bootstrap for descriptive uncertainty in paired cost ratios; with six curves per size, call uncertainty coarse. These counts are an initial diagnostic allocation, not a power calculation for a particular conjecture. Rare-event hypotheses require a separately frozen sample-size calculation from their predicted probability.

## Direct response: an executable specification and four tests

For canonical 0≤b<r, total scalar multiplication C(b) and target Q, use

$$R=\mathbb F_2[\varepsilon_0,\ldots,\varepsilon_{\ell-1}]/(\varepsilon_i\varepsilon_j\text{ for all }i,j),\qquad
Z_Q=\sum_b [C(b)=Q]\left(1+\sum_j b_j\varepsilon_j\right).$$

For Q=[k]P there is one accepted scalar and Z_Q=(1,k). A square-zero ring element is an ordinary pair (constant bit, tag bit-vector); addition is XOR and (a,u)(b,v)=(ab,av+bu). This is known algebraic model counting. Enumerating all b costs O(r) scalar evaluations and is a reference, never the proposed speedup.

**D0 — instrument checks.** Enumerate all bit inputs, including b≥r, all subgroup targets and selected outside targets on fixed tiny fixtures. Compare independently coded affine and Jacobian arithmetic, enumerate exceptional additions, and count satisfying transition witnesses. Inject one unconstrained Boolean auxiliary variable and verify that two identical witnesses cancel in characteristic two. Inject an intentionally wrong rewrite and ensure the checker returns a boundary counterexample. Check tagged coefficients, not just ordinary parity. Pass: zero mismatches in the declared finite suite and successful detection of each injected defect. Failure: a concrete mismatch invalidates that encoding/checker version. Limits: point-level deterministic arithmetic is not a gate-level Boolean circuit or a carry/wire proof.

**D1 — exact micro-block discovery.** First construct total, gate-level one- and two-step double-and-add blocks, b<r and canonical-output constraints. Fix wire layout, finite rewrite grammar, coefficient domain and an exact boundary enumeration before search. Candidate output must name the original block, replacement, target pins, every retained boundary bit and construction cost. Compare reference contraction to replacement for every boundary assignment on registered tiny instances, then overlapping two-block compositions. Require equality of all coefficients or a proved narrower invariant closed under composition. Generic XOR elimination, Boolean simplification and ordinary fixed-window merging are controls. Preserve every rejected candidate and its first counterexample. A finite grammar can be exhausted only after its file and bounds are frozen; that file and a gate compiler are currently missing.

For a compiled-counting adapter, test decomposable conjunctions, deterministic disjunctions and smoothing explicitly. Positive and negative scalar-literal weights sum to epsilon_j, not to 1. Omitting an unused scalar variable therefore changes the tagged count unless its actual weight sum is included. Verify the chosen compiler's theorem and coefficient-domain assumptions rather than substituting ring operations into an arbitrary Boolean DAG.

**D2 — structure and construction measurement.** For each surviving rule measure constraints eliminated, maximum participating-index union, peak live entries, encoded coefficient bits, constructor operations, rule applications and total checking/recovery work. Run the same generic simplifier on the EC block, an injective affine-bit-map control and a tiny explicit random-permutation control. Charge permutation table generation/storage. Arithmetic-mutated controls must retain total unique-extension semantics and disclose their encoding differences. An invertible basis change alone preserves the original function and is not a destroyed-structure null. Record whether any difference is specifically attributable to the EC identity. A small answer, separator, numerical rank or expression is insufficient if its construction is expensive.

The fixed-window matrix control in [window-control.md](window-control.md) has scalar rank r−1 over F₂. It explains why a dense global point-state low-rank replacement cannot be presumed. It does not prohibit a different bit-level, nonlinear or target-conditioned algorithm. No gate-level discovery or D2 comparison has run.

**D3 — frozen complete solver.** Admit only after there is an actual constructor and composition argument. Run every random confirmation target and the separate correctness suite. Recover k using public inputs alone and verify [k]P=Q independently. Charge failed branches, compilation, schedule search, target specialization, contraction, candidate extraction and verification. Compare a cold first-target run with matched rho, relevant automorphisms, BSGS where memory permits, and the strongest available exact compiler on the identical problem. If a comparator is unavailable, state that limitation and do not claim superiority to it. A generic integer #SAT result is not automatically a characteristic-two tagged count; bind and verify the adapter.

For an exploratory local-gain screen, a twofold reduction in the declared dominant local operation on two registered sizes warrants a fresh composition/cost test. That threshold is an engineering choice, not a theorem or a publication rule. For a complete-solver performance study, freeze its minimum effect and paired estimator only after baseline calibration; include A/A repeatability first. No performance threshold is retrofitted to results.

## Baselines, costs and statistics

Use identical public Q values, curve strata, arithmetic backend, threads, compiler, hardware placement and stopping/correctness policy. Freeze baseline tuning on development inputs. Rho uses negation and applicable automorphisms with cycle handling; credit known endomorphism speedups to both sides where applicable. A BSGS comparator gets its actual storage budget. Record baseline seeds and stochastic spread; do not compare a lucky candidate run with a single unlucky walk.

Use A/A repetitions to expose slot/host drift, randomize candidate/baseline execution order and record process placement and frequency/thermal conditions when available. Wall time, CPU time, field additions/multiplications/inversions, bit operations and allocation/storage bytes have distinct units. Raw XOR counts are not directly comparable to group additions. A full-cost elapsed-time claim needs controlled calibration and placement. Preserve compilation cost and circuit-size/width counters even when timing noise dominates.

Primary per-target cost is cold setup + preprocessing + target work + failed attempts + recovery + verification; record peak live and persistent memory separately. Secondary many-target costs must name the reuse count m and report (setup+sum target costs)/m. Compare with preprocessing baselines for the same m. Do not hide an O(r) truth table in setup. Preserve censored/time-limited targets, success fraction and resources consumed; successful-only averages are prohibited.

Report descriptive distributions and paired per-curve ratios. Any exploratory size fit states its model, range, confidence and dependence assumptions; it cannot establish an asymptotic exponent. Confirmation of a new speed/attack-cost claim requires repository progress-fidelity records and an independent session, neither supplied by this design document or its assisting agents.

## Frozen receipt and machine protection

Every scientific run needs immutable code/commit and dirty state, input and protocol hashes, exact argv, compiler/build identity, host/resource identity, UTC times, seeds, outcome, raw counters with units, output/certificate hashes, checker identity and all stdout/stderr. Record requested/completed/failed/censored counts by arm. Archive a failure before retrying; link the new attempt. Large artifacts follow the shared object-store policy, with hashes and readback; do not silently drop data to fit Git limits.

Use one worker initially and an explicit RAM limit below the host allocation. Set a process watchdog from the declared worst-case input and a resource estimate during admission. These protect the host and classify censoring; they are not lifetime research budgets or evidence of impossibility. The programme has no arbitrary campaign spending cap. Fixed cohorts end their registered test; subsequent work uses an additive new protocol.

## Readiness and next actions

The repository requires a prospective runnable specification, launcher, committed input/source hashes, executor handoff/queue and lawful lane before approval. Its read-only `experiment_preapproval.py` must return `approvable: true`; after the committed approval/archive, the selector must return `execution_state: ready` before scientific dispatch. No such receipt is fabricated here. Development self-tests below exercise code, not those admission gates.

Immediate work completed: per-lead designs, a point-level C++ reference, finite correctness checks and a scoped window-control derivation. Immediate implementation debt: registered scientific cohorts; a bit-level total circuit and unique-wire checker; exact finite grammar; lead-specific constructors and adapters; complete launch/admission/custody records. See [READINESS.json](READINESS.json) and the [named obstruction](../../../../problems/direct-ecdlp-cancellation-construction.md).

Prioritize D0 instrument completion and D1 exact blocks. In parallel, reproduce the lossy-panel finite references and deterministic rigidity proof as controls, and test only explicitly supplied EDS/endomorphism/automaton constructions. Do not run undefined coefficient, inverse-state or Pfaffian oracles. New direct successors of blocked originals get fresh identities rather than rewriting frozen evidence. Revisit a scoped negative only when its stated assumption changes or a specific missing constructor appears.

This programme changes no canonical frontier or official scientific disposition. It provides a concrete path to distinguish a correct instrument, informative observation, failed construction, resource limit, local identity and complete classical algorithm.
