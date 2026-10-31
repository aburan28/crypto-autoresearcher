# Design: volcano transport cost against matched rho

## Lead and question
LEAD-STR-isogeny-class-generic-invariance, LEAD-STR-isogeny-transport-preprocessing, LEAD-TRF-prime-field-isogeny-to-weak (all closed_obstructed). With transport charged in field multiplications, does rho on the best class member plus the transport ever cost less than matched rho on the original curve at q = 2^20..2^40, and how does transport cost scale?

## What the lead already says
- KR-RHO-817bf8 and EV-IT-511f3d: order, trace, embedding degree, anomalousness are functions of (#E, p) (Tate), so no prime-field class has a member weak by those. Rho/BSGS depend only on the group and Aut. 26-bit census, TOST +-5%: no level effect (EV-VOLC lane; rho floor/crater 1.004 [0.990, 1.016]).
- The only generic-model variation inside a class is Aut: j=0 (6) and j=1728 (4) sit at the crater of their volcano. Negation rho already uses 2, so the ceiling gain is sqrt(3) (j=0) or sqrt(2) (j=1728). Field-op constants (a=0 models) belong to LEAD-STR-class-representative-ic-selection and LEAD-ICE-curve-presentation-invariance; recorded here as secondary only.
- LEAD-STR-koblitz-volcano-descendants and LEAD-STR-isogeny-walk-weak-neighbour: floors never beat the crater; neighbours carry no class-variant weakness.
- Not stated in the leads: the paper below. The leads' obstruction reads "transport costs at most 1.3% of a solve" for small known degrees; the cost of climbing with a large conductor prime is not in them.

## The paper (verified myself)
Read: ePrint 2024/924 abstract page (Galbraith, "Climbing and descending tall isogeny volcanos", received 2024-06-10, revised 2025-07-24, Research in Number Theory 11:7, 2025). It says: heuristic O~(q^0.4) to relate ECDLP between ordinary curves of equal order, improving O~(q^1.5) of Galbraith 1999; a RIGOROUS O~(q^(1/4)) algorithm to compute an isogeny between any two curves in the class (flat and tall volcanoes); uses the Kani construction. NOT read: the PDF (HTTP 403) and the Springer page (login redirect). So theorem numbers, the cost unit (field ops vs bit ops), hidden polylog factors, and whether q^0.4 covers evaluating the ECDLP images (not just finding the isogeny) are unverified. Do not cite more than the abstract.

## Consequence the brief's expectation misses
q^0.4 < q^0.5 asymptotically, so "transport exceeds sqrt(N)" is not guaranteed by exponent. Break-even (my arithmetic, rho = 0.886 sqrt(q) x 10 M per step, gain budget 0.423 of rho): the largest constant c with c q^0.4 below budget is 15 M at 2^20, 26 at 2^28, 45 at 2^36, 60 at 2^40, growing as q^0.1. Any polylog factor (log^2 q is about 1600) exceeds this through 2^40, so toy sizes cannot show a win; at cryptographic sizes the model line would cross, but only for classes containing a j=0/1728 member (disc -3f^2 or -4f^2), and the win is at most 1.73x. This is analysis, not measurement.

## Hypotheses
- H0 (lead's prediction, expected): transport + Aut-rho >= rho-orig at every size (expected loss).
- H1 (falsifier): some size has a positive-class ratio interval wholly below 1, beyond the A/A half-width, surviving the 2x transport-charge band.
- H2 positive control: free-transport ratio 0.58 [0.52, 0.68].
- H3 exploratory: classical transport exponent about 1.5 (worst-case tall family, large prime l | f, kernel over F_{q^d}), below that for d-small.

## Instances
Primes p nearest below 2^20, 2^24, 2^28, 2^32, 2^36, 2^40. Positive classes: choose f and t with 4p = t^2 + 3f^2 (j=0) or t^2 + 4f^2 (j=1728), p prime; destination = y^2 = x^3 + b (resp. x^3 + ax) with b chosen so #E = p+1-t. Family F1: f smooth, every l | f with ord(t/2 mod l) <= 4 (kernel rational or in a tiny extension, so executable with PARI ellisogeny/Velu). Family F2: f has a prime l of size 0.3..0.5 of the maximum (worst-case tall); d computed exactly, kernel construction priced from exact structure counts because F_{q^d} is infeasible. Negative classes: random t with squarefree part of t^2-4p not in {-3,-4}; destination = fastest-constant model. 12 classes per size and family, 4 planted scalars per class, N = 576 instances per arm. Seeds: SHA256(protocol_sha256 | size | family | class | target | stream) per protocol `randomization`.

## Arms and controls
Reference rho-orig (negation rho on source). A/A rho-orig-aa (own stream). Candidate transport-rho (classical transport, every event charged, then Aut-orbit rho; the log carries back unchanged since the isogeny degree is prime to N). Positive control rho-dest-free (transport charged 0: the ceiling of any transport; also proves the detector sees a real 1.73x). Negative control transport-rho-noweak (144 classes without a weak member; ratio must exceed 1). kani-model: not implemented, reports only the break-even constant c*(q). Kani at toy scale needs higher-dimensional isogeny chains (theta-model arithmetic); no such code exists in the repo and PARI has none: weeks of work, declined. The model line is the smallest falsifiable substitute: c* must be inverted against a measured number.

## Counted metrics
Primary: total field multiplications (1 M mul, 0.8 M sqr, 20 M inv, 3 M batched), rho steps x exact per-step charge including Aut canonicalisation, plus transport. Transport charge table frozen (kernel search scalar mults in F_{q^d} at d^2 M per extension mult, Velu 12 l M per point, two points); run at 0.5x/1x/2x. Exponent: log-log fit of transport_fm vs q over 6 sizes, bootstrap over classes. No clock is read.

## Decision rule and dispositions
Per `protocol.json`. Controls invalid -> invalid_measurement. Closure confirmed if no size passes H1: update the lead's cost model with the fitted classical exponent, the q^0.4 and q^(1/4) figures flagged "abstract only", and c*(q). Reopen (scoped: j=0/1728-containing classes, constant factor <= sqrt(3)) if H1 passes. Falsifies the current disposition: a positive-class ratio interval below 1.

## Inadmissible moves
Free transport or free canonicalisation in the candidate; presenting the model line as measured; dropping F2 or a size; choosing classes by rho cost; any wall time; extrapolating to a deployed curve.

## Cost estimate
Effort: 4 to 6 days (Rust runner; PARI scripts for class construction and Velu; Python checker). Compute: 576 instances x 4 arms x 3 replicates, 2^40 rho about 1e6 steps; about 1.5 h on one 4-core host. Not probed.

## Implementation plan
Rust runner `voltransport` (rho with Aut-orbit canonicalisation, charge counters) plus PARI (C library or gp subprocess) for class construction, polmodular roots, ellisogeny. Searched for reuse: no rho/BSGS Rust in-tree beyond ecbench (sibling repo); the nearest in-repo prior is `research/isogeny_stratified_ml_blueprint_triage_20261010/transport_cost_table.py` (charge formulas, binary Koblitz) and `research/isogeny_volcano_m51_deep_scan_20261013/*.gp`; reuse their charge formulas and Velu verification. Prefer ecbench as the counting backend when the sibling repo is present.

## Independent checker
Python with `-I`, no shared code: re-derives #E, checks every recorded chain by recomputing Velu images from recorded kernels and testing phi(Q) = k phi(P), recomputes total_fm from recorded counts and the frozen table, replays a nonce sample of rho runs from recorded seeds. Tamper test: alter one chain step, one count, one planted scalar; each must be flagged.

## Open risks
Biggest: F2 transport at 2^28 and above is priced from structure counts, not executed, so its exponent is a model of PARI-free arithmetic. The charge table is my choice (band covers it). Aut-orbit rho overhead is uncertain; the positive control calibrates it. Paper theorems unverified (PDF 403).
