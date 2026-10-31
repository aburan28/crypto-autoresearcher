# Design: LEAD-STR-level-structure-torsor (derivation check, not a race)

## Lead and question
Reading an ECDLP instance as (E,Q)=<k>(E,P) in a (Z/N)^*/+-1 torsor over one point of X_0(N) has no algorithmic content. Question: on toy instances, do the diamond action, Hecke T_ell and Eichler-Shimura behave as the closure derivation forces, does a single fibre coordinate look like a random map, and does the degree of separating functions grow like N^2 (above N^(1/2))? Planted logs on toy curves only.

## What the lead already says
Proposed atlas row `closed_obstructed` (family-B-module.md, finding (a), dropped list). Obstructions: IDEA-20260806-0c9de1 F1 (rational torsor with a rational point is trivial), F2 (free action, so single-point invariants are constant or are P itself), F3 (Eichler-Shimura pins only <p mod N>); rejected ECDLP-IDEA-112 (diamond-eigenspace units: gonality/degree), -023, -026. Neighbours: LEAD-STR-torsion-module-leak (curve-only statistics are k-independent), LEAD-EXO-torsor-deck-period (deck invariants factor through the quotient), LEAD-STR-jmv-random-self-reduction, LEAD-STR-class-group-ecdlp-bridge. The T_ell "forced zero" is a derivation never run; 0c9de1 (D) queued it.

## Hypotheses
H0 (expected, the lead's own prediction): zero diamond and Hecke discrepancies; collision counts of b(E,aP) match the random-map null; deg(b), deg(c) on X_1(N) ~ N^2/16 (probe: 1,3,7,10,18,22 at N=5,7,11,13,17,19), above N^(1/2) for N>=19 and above the Kim-Sarnak/Abramovich bound 0.004959(N^2-1) for N>=37 (rigorous crossover with N^(1/2) at N=37). Expected outcome: null, closure confirmed. H1 (reopen): any discrepancy, collision p <= 0.05/6, or a separating function of degree < N^(1/2) at N>=37.

## Instances
Primes N in {101,251,509,1009,2003,4001}; per N, 6 curves y^2=x^3+Ax+B over F_p, p prime with |p+1-N|<=2sqrt(p), #E=N exactly, distinct j; 3 planted k in [2,N-2] per curve (108 pairs, 36 curves). Seeds: SHA256(protocol_sha256 || N || curve || k index). Probe: at N=2003 fourteen primes p in [N-80,N+80] give curves with #E=N within a<=400 (0.1 s in PARI). Degree check: primes N=5..47, two large primes p0 (1000003 and a second), two parameter values each.

## Arms and controls
Reference `bsgs-ref` (negation BSGS, sets the sqrt N scale). Baseline `orbit-tate` (orbit table of Tate forms (b,c)(E,aP), a=1..(N-1)/2). Candidate `orbit-tate-hecke` (same lookup after one F_p-split 2- or 3-isogeny hop). A/A `orbit-tate-rev` (scan reversed). Positive `pos-x-collision`: collision detector on x(aP), a=1..N-1, with exactly planted structure; orbit-tate recovers k up to sign at every enumerable N<=4001 (the coordinate IS cheaply computable); degree detector fires at N=5,7 (genus 0, Hauptmodul d degree 1). Negative `neg-nonmatch`: (E,P) against (E2,Q2), different j, same N, 108 pairs; all checks must report no relation and the orbit scan must exhaust (N-1)/2 forms. A failed control gives invalid_measurement, never closure.

Checks. (a) Tate normal form of (E,kP): certificate (u,r,s,t) with (E,kP)->(b,c); orbit size (N-1)/2, distinct, rational. (b) For ell in {2,3} (kernel x-coordinates by exhaustive root search of psi_ell over F_p, Velu): log of phi(Q) base phi(P) equals k, T_ell(E,Q)=<k>T_ell(E,P) as Tate-pair sets, V(P)=(t-1)P=[p mod N]P. (c) degree of b (c) = number of c (b) roots of the order-N condition at fixed b0 (c0), discriminant factors removed.

## Counted metrics
Group ops by kind (add, dbl, neg), Tate conversions, isogeny evaluations, and the field tuple (mul, sqr, inv). Primary cost_m: mul=1, sqr=1, inv=10 (sensitivity 5 and 20), setup and canonicalisation included; canonicalisations and table lookups listed as uncharged counters. Exact metrics: failure counts, degrees. Derived: collision p-value (20,000 null resamples, minimum p 2/20001 < alpha/m=0.0083, Bonferroni over 6 N; resolution only, not power). No clock is read.

## Decision rule and dispositions
Confirm closure (disposition stays `closed_obstructed`, `best_measured` records this check, F1-F3 and the degree growth cited): all exact checks zero failures with >=30 neighbours, controls pass, collision p > 0.0083, degrees meet P4, C-hecke cost ratio CI in [0.97,1.10]. REOPEN: a separating function of degree < N^(1/2) at N>=37; nonzero Hecke discrepancy; collision p <= 0.0083 (structure in one coordinate, which also contradicts F2). Derivation errors (orbit size != (N-1)/2, V(P) != pP) send F2/F3 back to review, not the attack.

## Inadmissible moves
Changing N, ell list, seeds, null law or weights after data; reading orbit-tate vs bsgs-ref as a scaling claim (it is (N-1)/4 steps by construction, a unit calibration only); counting cheap evaluation of b,c as progress (evaluation is not inversion; reading k from two Tate pairs is the DLP); curve-only statistics; extrapolating toy recovery.

## Cost
About 4 to 5 days to implement (Rust ~1,200 lines, checker ~600). Compute: seconds to minutes; under 10 min on one core of a 4-core host.

## Implementation plan
New Rust crate (path PLANNED, not created): F_p, short-Weierstrass group law with op counters, Tate normal form with certificate, Velu for ell=2,3, negation BSGS, numeric order-N chain with interpolation for degrees, JSONL records. Python only orchestrates and exports (`tools/experiment_protocol.py` seeds, from-rows, check-export). Reuse: `tools/experiment_protocol.py`; PARI usage patterns in `research/isogeny_volcano_m51_deep_scan_20261013/classify_recover.gp`; `tools/isogeny_class_screen.py` for ordinarity data; `src/crypto_autoresearcher/index_calculus/rho.py` only as a cross-check of the BSGS count. No existing Tate-form, Velu or modular-curve code found by grep.

## Independent checker
Shares no code with the runner: pure-Python re-implementation of the group law plus PARI `gp` (`ellcard`, `ellisogeny`, `elldivpol`). It replays recorded (p,A,B,P,Q,k): verifies each isomorphism certificate by substituting into the curve equation at random points, recounts #E, recomputes isogenies with `ellisogeny`, and recomputes psi_N(0;c) by division polynomials (a different method from the runner's order-N chain) with squarefree-degree comparison. Tamper test: flip k, one (b,c) entry or one degree in the record; the checker must fail each, and a deliberately wrong diamond (k+1) must be flagged.

## Open risks and unresolved
1. PO-1 (not discharged): Kim-Sarnak is characteristic 0, and specialisation can lower gonality, so gon_{F_p}(X_1(N)) >= N^(1/2) at N ~ p is unproven; Ihara point counting is vacuous (#X_1(N)(F_q) ~ q) and the supersingular argument needs N | p+1. The toy check shows degrees of explicit functions only. This is the live `revisit_when`. 2. Injectivity on F_p points differs from separating: a map from (N-1)/2 points into F_p (N~p) collides by pigeonhole, which the collision test exploits. 3. F_p-split Hecke neighbours only (ell=2,3; ell=5,7 missed unless kernel x in F_p). 4. Gonality table and lambda_1 constant are recalled, not retrieved; verify before freezing. 5. Design probes (PARI elldivpol, curve existence) are probes, not results.
