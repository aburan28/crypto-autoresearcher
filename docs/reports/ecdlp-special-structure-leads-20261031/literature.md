# ECDLP literature scan (2026-10-31). Toy/public parameters only.
Method: WebSearch (standard; extended once) + WebFetch of abstract pages. Search index is thin for 2023-26 ePrint; only abstract pages were read, not full texts. "Atlas" = knowledge/leads/ecdlp + knowledge/frontiers/ecdlp (grep by author/title/mechanism).
Overall: no credible sub-sqrt(N) classical result for generic prime-order ECDLP found. Closest-to-structure items are negative/barrier or conditional.

## A. Structure / algorithmic claims
1. Mahalanobis, "A Guess and Determine Attack on the ECDLP", arXiv:2607.09814 (cs.CR, Jul 2026, v2 Aug 2026). https://arxiv.org/abs/2607.09814
   Structure: Riemann-Roch / linear algebra reduction of ECDLP to finding a zero minor of a matrix; hyperplane-arrangement intersection poset to find the minor. Claim: algorithm, complexity and success probability "discussed"; abstract gives no bound and no sqrt(N) comparison; author states it poses no security risk. Success probability depends on group structure and a defect parameter.
   Judgement: not credible as a speedup; unreviewed, no stated exponent. Only abstract read.
   Atlas: NOT in atlas (grep Mahalanobis, minors: nothing).
2. Mahalanobis & Mallick, "A Las Vegas algorithm to solve the ECDLP", arXiv:1703.07544 / ePrint 2018/134 / INDOCRYPT 2018. https://arxiv.org/abs/1703.07544
   Structure: Riemann-Roch spaces, reduction to linear-algebra "Problem L". Claim: Las Vegas, non-generic; no proven sub-sqrt cost (bottleneck is Problem L).
   Judgement: low; never shown to beat rho. Atlas: NOT in atlas (only an unrelated "Las Vegas F4" in KR-IC-0d2021).
3. Abdullah, Mahalanobis, Mallick, "A new method for solving the ECDLP", arXiv:2005.05039, Groups Complex. Cryptol. 12(2), 2021; and Abdullah & Mahalanobis, "Minors solve the ECDLP", arXiv:2310.04132. Structure: "initial minors" conjecture via Schur complements. Claim: solved groups up to order 2^50 (computational); no complexity bound; conjecture unproven.
   Judgement: low credibility as asymptotic; but cheap to test at toy sizes (determinant/minor cost likely worse than rho). Atlas: NOT in atlas.
4. Galbraith, "Climbing and descending tall isogeny volcanos", ePrint 2024/924; Research in Number Theory 11:7 (2025). https://eprint.iacr.org/2024/924
   Structure: isogeny volcanoes + Kani construction. Claim: heuristic O~(q^0.4) (was q^1.5) to transfer ECDLP between ordinary curves with same point count (rigorous O~(q^1/4) to find isogeny in class). Speedup over rho: none directly; it makes transport to a weaker class member cheaper (relevant only if a weak member exists). Credible (peer-reviewed).
   Atlas: PARTIAL. LEAD-STR-isogeny-class-generic-invariance (volcano census, no level effect), LEAD-TRF-prime-field-isogeny-to-weak, LEAD-STR-isogeny-transport-preprocessing cover the mechanism; the paper itself and its q^0.4 / q^1/4 transport costs are not cited.
5. Macula & Stange, "Extending class group action attacks via pairings", ePrint 2024/880 / arXiv:2406.10440. Structure: sesquilinear pairings on CM/oriented curves. Claim: breaks/limits some class-group-action problems (DDH-type), not ECDLP on a single curve. Credible; adjacent.
   Atlas: PARTIAL (LEAD-EXO-elliptic-net-eds mentions pairings; LEAD-STR-class-group-ecdlp-bridge is the nearest; paper not cited).
6. Galbraith, Lai, Montgomery, simpler quantum DLog->CDH reduction for group actions, ePrint 2024/191 (PKC 2024). Group-action not ECDLP; negative/relative. Atlas: NOT in atlas (low relevance).
7. Koshelev & Sanso, GLV-style endomorphisms for moderate CM discriminants, ePrint 2025/196. Scalar-multiplication speed only, no DLog. Atlas: ALREADY (LEAD-STR-glv-gls-isogeny-loop-scalar-mult cites Koshelev-Sanso).

## B. Barrier / negative results
8. Corrigan-Gibbs, Henzinger, Wu, "The Structured Generic-Group Model", ePrint 2026/384, EUROCRYPT 2026. https://eprint.iacr.org/2026/384
   Claim: an algorithm exploiting structure on at most a delta fraction of group elements needs Omega(min(sqrt q, 1/delta)); tight subexponential lower bound for generic smooth-integer index calculus; similar for small integers, smooth polynomials, elliptic-curve points. Negative/barrier; credible (Eurocrypt).
   Atlas: PARTIAL. Grep hit "Corrigan" only for Corrigan-Gibbs-Kogan preprocessing (KR-RHO-ea34b8); this 2026 structured-GGM paper is NOT cited. Directly relevant to LEAD-ICE-generic-oracle-arity-cost-floor and index-calculus-on-prime-curves closure.
9. "Non-Adaptive Cryptanalytic Time-Space Lower Bounds via a Shearer-like Inequality for Permutations", arXiv:2505.00894 (2025). Negative; abstract not read. Atlas: NOT in atlas (verify).
10. Petit/Kosters/Messeng PKC 2016 (special structure, prime-field algebraic) and Semaev 2015 line: old; atlas ALREADY (LEAD-ICE-first-fall-degree-assumptions). No 2024-26 improvement found by search.

## C. Leakage / hints (HNP)
11. Gao, Wang, Hu, He, "Attacking ECDSA with Nonce Leakage by Lattice Sieving: Bridging the Gap with Fourier Analysis-based Attacks", ePrint 2024/296, ASIACRYPT 2024. Structure: HNP lattice + sieving, leakage <= 1 bit on 160-bit curve. Conditional on signatures with nonce leakage; not a pure ECDLP result. Credible.
    Atlas: PARTIAL (LEAD-EXO-hnp-advice-leakage covers HNP/advice; this paper not cited).
12. Sun-Espitau-Tibouchi-Abe "Guessing Bits" (TCHES 2022), Albrecht-Heninger (EUROCRYPT 2021), LadderLeak (2020): older HNP baselines. Atlas: PARTIAL as above.
13. Kudelski "Half-Half" ECDSA single-signature attack (2025): only a blog summary seen; UNVERIFIED, likely implementation-flaw specific.

## D. Quantum resource (does not change classical cost)
14. Babbush et al. (Google Quantum AI, Boneh, Drake), arXiv:2603.28846 v2 (Mar-Apr 2026): 256-bit ECDLP in <1200 logical qubits & <90M Toffoli, or <1450 & <70M; <500k physical qubits. Circuits validated by ZK proof, details withheld; v2 patched a ZKP soundness bug. Not independently verifiable. Credibility: authors strong, claim unverifiable.
15. Chevignard, Fouque, Schrottenloher, "Reducing the Number of Qubits in Quantum Discrete Logarithms on Elliptic Curves", ePrint 2026/280, EUROCRYPT 2026: 3.12n+o(n) qubits (P-256 ~1,193 per secondary source, a swap correction noted), at ~1000x more gates. Credible.
16. arXiv:2606.02235 (point-addition circuits, 1208-1462 logical qubits, ~10% Toffoli drop) and IonQ trapped-ion estimate (Sep 2026): seen only via secondary coverage; UNVERIFIED.
17. Dallaire-Demers, Doyle, Foo, "Brace for impact: ECDLP challenges for quantum cryptanalysis", arXiv:2508.14011 (v3 Oct 2026): graded toy challenge ladder on y^2=x^3+7, 6..256 bits; resource mapping; 2027-2033 window claim is speculative. Useful as a toy-parameter benchmark. 
18. Garn & Kan arXiv:2503.02984 (binary-curve Shor estimates); Gu et al. arXiv:2510.23212 (2D nearest-neighbour layout; 4300 logical qubits figure unverified); Roetteler et al. 2017 baseline.
    Atlas for 14-18: PARTIAL. LEAD-EXO-quantum-ecdlp-resources (secp256k1 point-add circuit optimization, 1,434-qubit peak) exists; none of these papers is cited.

## E. Multi-target / auxiliary-input
19. Cheon 2006/JoC 2010; Cheon-Kim LMS JCM 2016; Weng-Dou-Ma 2016 (special ECDLP): all in atlas (LEAD-RHO-cheon-*). ALREADY. No 2024-26 improvement found.
20. Kuhn-Struik; Hitchcock et al.; Bernstein-Lange precomputation: ALREADY (LEAD-RHO-dp-multitarget-precomputation, KR-RHO-ea34b8).
21. Records: 129-bit secp256k1 interval (GPU kangaroo) per arXiv:2508.14011; no new generic algorithm. ALREADY-ish (LEAD-RHO-kangaroo-interval).

## F. Searches that returned nothing new for 2023-26
Weil descent/GHS/cover (only Chi-Dominguez et al. 2021, atlas KR-IC-ae532f), Joux-Vitse (atlas), summation polynomials/IC prime (atlas), CM/endomorphism speedups, negation/automorphism rho (atlas), twists, lifting. Search engine coverage of recent ePrint is poor; a direct ePrint listing sweep is recommended before declaring these areas empty.

## Candidates deserving an experiment
- Item 3/1/2 (minors / zero-minor): toy test only, to measure cost of the minor search vs matched rho at 20-40 bit orders; expect it to be worse. Cheapest closure of an unexamined lead.
- Item 4 (Galbraith q^0.4 transport): cost-account transport to the weakest class member, tie to LEAD-TRF-prime-field-isogeny-to-weak.
- Item 8: use the structured-GGM delta-fraction bound as a cost-floor citation for IC closures.
