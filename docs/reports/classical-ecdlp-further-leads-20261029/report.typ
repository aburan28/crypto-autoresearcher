#set page(paper: "a4", margin: (x: 19mm, y: 17mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false, leading: 0.52em)
#set heading(numbering: none)
= Further classical ECDLP leads
Controlled next steps · 2026-10-29 · BATCH-07e7ab

This round produced derivations, an incremental prototype, eleven disclosed known-answer software tests and two independent technical reviews. It ran no new cohort, decoder panel or old-cohort reanalysis. The goal remains active and the hypothesis specified. No broad algorithmic conclusion follows.

#image("research-map.svg", width: 100%)

The prior fixed-circuit study remains a finite working baseline. Its successes and failures concern its declared circuits and sampled curves. This follow-up separates arithmetic reuse, bounded-error recovery and mechanism-sensitive controls before collecting new data.

Source publication: `1190b8a541e4`; source custody: `ca8020d048f1`.
Independent review publication: `4a8d9494b0f5`.
Full hashes and read-depth limits are in `sources.json`; complete details and linked lane reports are in `report.md`.

#pagebreak()
== What is derived and what was checked

The independent blind reviewer gave a separate divisor/Laurent proof of the slope cocycle, primitive existence and uniqueness, and public seed construction. With complete identity, inverse, vertical and tangent conventions and subgroup order r coprime to p:

`Z(2R) = 2Z(R) + lambda(R,R)`.

The incremental prototype seeds Z once and shares the slope from the existing query doubling. Eleven producer tests passed on the already disclosed F11 and F23/order17 fixtures, retaining every fixed-L call after undefined values and every non-counter trace/witness field. A deliberately wrong-sign recurrence is detected. The tests share original arithmetic helpers; they are not independent execution-counter replay or fresh recovery-rate observations.

For b = bit_length(r), L = b+1 and C = b+popcount(r)-2, source-level reuse removes (L-1)C group-add calls from repeated Miller reconstruction. Initial normalization, each state update, field/character work, setup, blinding, scalar conversion, public checks and memory still count. No total speed ratio or asymptotic exponent was measured.

Under the forward chart `(x',y')=(u²x,u³y)`, slopes and Z scale by u, while c scales by u⁻². The same fixed coefficients give g'=ug and anchor'=u anchor, so normalized values and holes transport. A prior inverse-weight/beta-change suggestion was caught before trials. Its wrong-beta F11 control changes the normalized value while preserving the bit: bit-only checks miss this error. Charts are paired views, not independent curves.

== A constructive decoder question

The exact half-bit word is V = floor(2^L s/r). A complete list with e erased positions and at most t wrong defined bits contains at most `2^e sum binom(L-e,j)` words for j through min(t,L-e). Retain k = ceil(rV/2^L) only within the strict half-open interval and canonical range, then check both public equations. All words, empty intervals, caps, failed branches and conversions remain charged.

For a fixed deterministic prepared predicate, complete enumeration and independent uniform nonzero blinding give a per-target success fraction equal to the nonzero-scalar fraction whose trace meets those error/erasure bounds. This conditional statement needs no within-trace independent errors. An anchored odd abstract Z/7 control has marginal accuracy 2/3 yet zero exact-word success; a Z/31 control has perfectly correlated trace errors. Marginal bias alone cannot supply a decoder guarantee.

#pagebreak()
== One selected next study, still awaiting implementation and admission

Implement bounded-radius decoding and pair original/incremental evaluation for fixed circuit2.a1. The primary comparison is t1.e2 versus exact t0.e0; all six radius/cap cells isolate flips and erasures. Prior F23-informed choices are disclosed and cannot be fitted on confirmation.

Proposed population: 48 fresh curves, with 24 calibration curves and two independent 12-curve confirmation panels, spanning 10/13/16-bit subgroup orders. Calibration characterizes eight frozen arms with the original evaluator. Confirmation uses 1,536 public targets and eight blindings each: 12,288 traces, 73,728 paired decoder-cell outcomes and 172,032 point-query slots. Running both evaluators means 344,064 physical predicate evaluations. Calibration adds 345,600 single-point arm evaluations and 344,064 original trace-query evaluations. The selected proposal totals 1,033,728 physical evaluations before additional controls/references; none has been executed here.

The six decoder outcomes share each incremental trace and are not six independent query samples. Standalone algorithm costs still include that algorithm's full query work. Curve is the population unit; targets, restarts, cells, nulls and charts are nested or paired. Fixed-curve precision and planning q=0.02 event detection do not imply population-of-curves power. Sparse events or heterogeneous panels may remain inconclusive. There is no exponent fit.

The existing sampler draws unlabelled public coordinates; its public nonce does not reveal a known secret k. The old full compute program later performs BSGS/diagnostics inside the VM. The proposed worker excludes those host-only operations. A candidate-only public worker must seal results and stop; after full readback and quiescence/termination acknowledgement, the trusted host may build scalar labels and BSGS references. No truth returns to a live candidate. A future Q=[k]P sampler would instead require private generation seeds/labels. Exact source closure and isolation probes remain mandatory. Cross-backend counters disclose their boundary; matched timing is not claimed.

#pagebreak()
== Controls and unresolved leads

The synthetic single-arm reference preserves oddness, anchor and an exact symmetric undefined mask, then transports the same sign assignment across charts. Its support may be tiny or degenerate. Matching the identical full cocycle leaves no primitive freedom by uniqueness. Neither control attributes scalar-ordering structure by itself. Constrained shuffles remain descriptive without an exchangeability null; a plus-one rank does not create that null.

Two Fourier/conversion directions remain open for implementation. The same prepared-base identity can turn matching nonzero frequencies into x = beta/alpha; it does not establish a useful heavy component or a cheap learner. AGS Theorem 5's bounded-complex excerpt defers the general construction. The Boolean explicit `tau^-5.5` dependence uses squared amplitude; it is not an unsourced ternary amplitude⁻² discovery bound. Erasure encoding, numerical error, nonzero-frequency thresholds, both learner failure probabilities and `O(tau^-2)` cross-list candidates remain priced obligations. Constant, punctured-constant and identity-delta controls are distinct. No decoder was evaluated here.

Before new data: implement complete enumeration and null support, independently inspect negative mutants and exact t0 embedding, bind the public worker and post-seal host verifier, establish counter replay or retain its qualification gap, freeze all source/input/runtime/count/analysis decisions, pass exact admission and save the required checkpoint. This zero-run batch grants no trial authority; the next implementation phase is a separate batch.

The dated atlas “hash/closure” and “no measured bias” language is retained as scoped historical context, not a present universal verdict. Hypothesis and goal statuses remain unchanged. Repository-wide validation retains 64 pre-existing ledger failures; scoped checks do not imply global green.

== Sources and scope

Primary passages were read by the named producer/reviewer sessions at their stated depth, not independently reverified in full by this synthesis:

- #link("https://www.math.canterbury.ac.nz/~f.voloch/Pdfs/zeta3.pdf")[Voloch, 1997: characteristic-p zeta addition law.]
- #link("https://www.cs.tau.ac.il/~safra/PapersAndTalks/hardcore.pdf")[Akavia–Goldwasser–Safra, 2003: multiplication codes and Fourier learning.]
- #link("https://arxiv.org/pdf/1411.7565")[Hemerik–Goeman: exact/random permutation-test conditions.]
- #link("https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf")[Phipson–Smyth: Monte Carlo ranks and sampling conditions.]

The complete report, design, hashes, independent reviews and qualification gaps accompany this PDF. Bounded search absence is not a novelty certificate. Final ledger custody is an administrative step separate from these scientific limits.
