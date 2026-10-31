# Design: kernel-of-reduction lemma (LEAD-TRF-kernel-of-reduction-lemma)

Protocol: `protocol.json` (unfrozen, `validate` passes, see `validate.txt`). Nothing has been run.

## Lead and question
Candidate C2 of the family-C report. For L a finitely generated group of global points and red: L -> G a reduction or specialisation map, a short vector of K = ker(red) is a discrete log, and the F_p(t) kernel height floor is a p-independent intersection number while over Z it is 2 log p. Question: is the F_p(t) floor a property of the prescribed-fibre shortest kernel vector (what an attacker needs) or only of the minimum over fibres, and does the Z "coverage excess" vanish over F_p(t)?

## What the lead already says
LEAD-TRF-global-lift-small-height (closed_known), LEAD-STR-endo-scalar-action-generic (closed_obstructed, witness lattice, H-ENDO-001), LEAD-ICP-xedni-function-field-sections and LEAD-TRF-function-field-xedni-lift (alpha = 3, EV-XEDN-001), LEAD-EXO-global-lift-height, LEAD-TRF-cm-canonical-lift-heights. EV-CZLIFT-376eee D2: kernel points have h >= 2 log p - c_E; measured minimum lambda1 - 2 log p = +0.9129, at 234446a1 p = 103 (rt_f). DEC-20261023-26a6de weakened H-CZLIFT-9a32e9 on C2 (excess 1.0338 vs random-hom 1.0142 [1.009, 1.019]). Its KN-LIT-7593 citation is an AES paper and is not used.

Checks I made on the report that change the design:
1. The report's Z arm names 37a1 and 389a1, but their floor does not bind: minima of lambda1 - 2 log p are 92.8 (37a1) and 2.94 (389a1). The 0.91 comes from the rank-4 curve. The Z arm therefore uses the whole 7-curve ladder.
2. Over F_p(t), h = 2 chi + 2(s.O) - contr, so a section through O has h >= 4 (not 2) in Shioda normalisation; "about 2" is the pole term only.
3. The "minimum over all fibres" is 4 by the height formula, so a test of it cannot fail. The attacker-relevant quantity is lambda1 at a prescribed t0. There L is a fixed rank r <= 8 lattice and red_t0 has index m ~ p, so Gaussian scaling gives lambda1 ~ m^(2/r): it grows with p, exactly as in Z. The report's falsifier ("floor grows with p") read at a prescribed fibre will fire for r = 2, 4. The exception is a plateau at 4 for r = 8 until p is about the number of norm-4 vectors (1080 pairs in E8).
4. All sampled surfaces have p = 1 mod 3, L is a Z[omega]-module and the real map is omega-equivariant. A Z-linear random-hom control would confound ring with symmetry, so the F_p(t) control is equivariant.

## Hypotheses
- H0 (the lead's reading): F_p(t) floor is p-independent as stated and clumping is absent.
- H1 (expected): floor is a constant lower bound (4) but prescribed-fibre lambda1 scales like m^(2/r) in both rings; the closure-instrument standing survives, the sentence "p-independent" must be restricted to the minimum over fibres. Expected null for the lemma (no exponent moves); expected partial loss for the lead's new-content sentence.
- Coverage: floor-driven clumping needs 4(h_points) < floor. Over F_p(t) the floor 4 exceeds only the norm-2 differences, so I predict the real-minus-random-hom contrast is about 0 (within +-0.005) against +0.020 over Z. This is the one place the lead could be right and new.

## Instances
- Z arm (`z-real`): curves 37a1, 389a1, 5077a1, 234446a1, 19047851a1, 5187563742a1, 382623908456a1 with the MW basis and Gram data of rt_e (PARI normalisation). Primes: all good p in 101..3000 with E(F_p) cyclic. The 16 EV-CZLIFT primes are calibration; the rest are decisive.
- F_p(t) arm (`ft-real`): y^2 = x^3 + b(t), deg b = 6 squarefree non-square (the EXP-XEDN-001/002 frozen family; only type II fibres, so contr = 0), p in {7,13,19,31,37,43,61,67,73,97} (all 1 mod 3). Draw (x, y), polynomials of degree <= 2 and <= 3, uniformly; set b = y^2 - x^3; scan all p^3 quadratic x for more polynomial sections (about 1/2 expected, P_lift = (1-2/p+p^-3)/(2p^3)). L = span of all F_p(t)-rational height-2 sections; keep rank >= 2 surfaces, strata r = 2, 4, 6, 8, 30 per prime or 3000 draws. Every good t0 in P^1(F_p). Seeds: `seeds --all` from the protocol hash. Rank 6 and 8 may be unmeasurable by density (stated rule: fewer than 10 surfaces decides nothing).
- Toy group: N in {1009, 10007}, ranks 2, 3, 4, 6, planted k uniform from the seed.

## Arms and controls
Reference `z-real`; candidate `ft-real`; A/A `z-aa` (random unimodular basis, reversed order, a second enumerator: lambda1 must agree to 1e-9, so its spread is zero by construction); negative `z-randhom` and `ft-randhom` (200 same-index random homs per cell; equivariant for F_p(t)); positive `ft-planted` (surface built with a known height-4 section through O at a chosen t0; Z cells with p | den x(nP), n <= 6; the minimiser must return lambda1 <= planted height); `toy-oracle`, `toy-mitm`. Anomalous control (the p-adic channel): toy curves with #E = p (p in {1009, 10007}, found by seeded search); Smart-style Z/p^2 lift plus formal logarithm recovers k in O(1) scalar multiplications (positive), while same-size non-anomalous curves give success rate about 1/p (negative). The lemma excludes this channel by its hypothesis: access to K only through images in G, and the formal-log read needs the Z/p^2 coordinates, which are not an image-oracle value.

## Counted metrics
All primary metrics are exact (lambda1 by Fincke-Pohst, no tolerance beyond 1e-9) or counted. Coverage ratio = distinct residues of {s : h(s) <= B} over N(1-(1-1/N)^|S_B|), B least with |S_B| >= N/10 (CZLIFT convention). Toy cost: affine add = 1 inv + 2 mul + 1 sqr, double = 1 inv + 2 mul + 2 sqr, table lookups listed separately, canonicalisation absent (charged 0); oracle calls and mod-N inverses counted. Never read from a clock: nothing is timed.

## Decision rule and dispositions
- C2, C5 must hold exactly (runner correctness), else no verdict.
- C3: stratum r = 4, OLS slope of log median lambda1(t0) on log p excludes 0 and lies in [0.25, 0.75]. Supported (expected) means the lead's p-independence sentence is falsified at the prescribed fibre; disposition stays closure instrument, wording changes to "floor not inherited, scaling inherited"; next_action unchanged. Flat slope in p <= 97 would mean widen p, no conclusion.
- C4: Z contrast reproduces (+0.020) and F_p(t) contrast inside +-0.005 confirms ring-specificity and reopens a short note for the atlas; F_p(t) contrast excluding 0 falsifies "ring-specific".
- Falsifier of the lead as the report states it: F_p(t) floor growing with p. The anti-falsifier: any ring where short kernel vectors are found below MITM cost without a log would be a real lead (toy slope of MITM cost over sqrt(N) against r significantly below 0).
- Holm over 6 tests, alpha 0.05; resample N = 9999 gives 2/(N+1) = 2e-4 < 0.05/6. This is resolution only; effect-size justification is in the protocol.

## Inadmissible moves
Reading min-over-fibres as p-independence of the attacker quantity; Z-linear controls against an equivariant map; moving strata, primes, B or the N/10 rule after data; counting in-sample Z primes as decisive; any attack or exponent claim.

## Cost
Implementation about 3 to 4 person-days (Rust: polynomial group law over F_p[t], Fincke-Pohst, Z[omega] basis for the equivariant control, toy oracle/MITM, Smart control). Compute: p^3 scan 9e5 x ~100 ops per surface at p = 97 is about 1 s; estimate 1 h total on one core, 300 surfaces, under 10 min for Z and toy. Not measured.

## Implementation plan
Rust crate `kor/` for the F_p(t) runner and toy arms; reuse rt_f / rt_e (`experiments/EXP-CZLIFT-a255fc/reports/redteam-20261023/`) for the Z arm via PARI/gp 2.15.4 (present on the host; numpy and sympy are not installed here) and the frozen predicate of `experiments/EXP-XEDN-001/xedni_sections.py`. A grep found no existing Smart attack, rho or BSGS in Rust that fits; `experiments/EXP-ECDLP-84af7b/implementation/nfield/src/ecnf.rs` and the python curve code were not reviewed in depth.

## Independent checker
Python 3 + gp, no shared code. It recomputes F_p(t) Gram matrices from intersection counts ((P.Q) from gcds of x and y differences) where the runner uses group-law doubling and denominator degrees; it recomputes kernel lattices by Hermite normal form and lambda1 by qfminim, replays 20% of cells by nonce, and a tamper test (flip one specialised point, expect a mismatch) must be caught.

## Open risks
1. Probe: a gp attempt to compute 389a1 kernel minima by ellrank/ellheightmatrix timed out at 50 s twice (command `timeout 50 gp -q probe_z.gp`, no output); I did not isolate the cause (likely my loop, not PARI). The Z arm must take its MW data from rt_e, not ellrank.
2. The Z[omega]-basis for the equivariant control is the main implementation risk; fallback is to report the Z-linear control separately and mark C4 for F_p(t) inconclusive.
3. Rank 6 and 8 strata may be empty; then the E8 plateau prediction goes untested.
4. Out-of-sample curves are unavailable (no MW generators beyond the ladder); decisive Z cells differ from calibration cells only in primes.
5. The Z-arm claim ">= 0.91" is empirical; the theorem is >= -c_E.
