# TASK-20260926-12a355 — generator report, seam S1 (round 2)

Lane: algebraic oracles with Koblitz structure at arity m >= 5, index calculus
on ECC2K-130. Agent: idea-generator (research-deep). Date: 2026-09-26 (lane
resumed after an API-rate-limit termination; nothing had been written before
the resume). No run, no status change, no existing record edited. Four
proposals filed; one pre-minted id returned unused (reason below).

Budget convention used in every record: the validator's re-derived per-attempt
oracle budget under the producer's model N = 4r (BRIEF-ROUND2 section 1):
2^5.73 (m = 4), 2^13.96 (m = 5), 2^19.77 (m = 6), 2^27.37 (m = 8); the
cap-locus column of IDEA-20260926-4b65e3 (2^32.4, 2^37, 2^42; a proposal,
unreviewed) is quoted beside it as the alternative model. No record quotes the
floor-to-rho gap as a budget.

## Proposals filed

| id | class | question | claim (25 words) | target m and budget | novelty | cost |
| --- | --- | --- | --- | --- | --- | --- |
| IDEA-20260926-197ecf | mechanism | RQ-FROB-7d8dd4 | Tau-Horner chain R = sum tau^{m-k} P_k over one subspace has the plain chain's descended shape (squaring is a rotation) and m! more distinct relations per solve. | m >= 5; +2.1 to 2.7 bits on the budget column after re-balancing; no exponent | unverified (GGMP 2020/1315 abstract is the nearest, unread) | impl low, compute low (minutes plus 1-3 CPU-h W_4) |
| IDEA-20260926-0d1d74 | algorithm | RQ-CERTBIN-836ce2 | gcd(h, L_V) by modular squaring costs O(l deg h^2), |V|-independent, 131x for the orbit union; Nagao/RR at m = 5, 6 is the loop with a constant. | m = 5, 6; every priced encoding 50-80 bits above both budgets | unverified | impl medium, compute low |
| IDEA-20260926-1ddce2 | control | RQ-ICPERF-94c86e | Chained-S_3 oracle materialises in about 2^31 monomials at m = 5 on ECC2K-130, escaping EV-ICPERF-784b25's +40.8-bit unchained deficit; S1 is a solver question with a 2^55-2^73 gap. | m = 5, 6, 8; 17 bits above the producer budget, 1.5 bits below the cap budget at m = 5 | unverified | impl medium, compute low |
| IDEA-20260926-120d6a | control | RQ-BINSTD-b6f698 | S_m symmetrisation on a subspace base saturates the product spaces (dim V^(k) = 131 at k >= 5) and needs the Vieta lift; Frobenius part acts freely. | m >= 5; certificate, moves no column | unverified (HPST 2013 recalled) | impl medium, compute low-medium |

Unused id: IDEA-20260926-009cb9. The fifth candidate (the Frobenius-twisted
one-variable summation polynomial of G3's open direction 2) was drafted but its
record was not filed in this session; the direction stays open below and the
id is returned for `allocate_id.py`.

## Which to test first, and why

**IDEA-20260926-197ecf** (the tau-Horner chain). It is the only record in the
lane whose positive outcome changes a number every m >= 5 proposal prices
against (the attempts column loses its m! at zero descended-degree cost on a
Koblitz curve), and its decisive test is solver-free: exact enumeration of
ordered tuples at n = 17 and 19 (2^{ml} <= 2^18) counting distinct verified
relations for the tau-Horner map against the plain sum, predicted ratio m!
within [0.8, 1.2] m!, with the ordinary CERTBIN curve's [2]-chain as the null
(symmetry broken at a degree cost) and a relabelled Z/NZ replica for the
counting claim. Minutes of pure Python on the installed CERTBIN modules, two
non-overlapping outcome bands fixed in advance, and a closure-work comparison
(W_4 on matched targets) as the second, cheap stage. It is the cheapest valid
discriminator because the plain arm is RC-1's archived regression and the tau
arm differs in one declared component (a rotation of the node block).

Second: IDEA-20260926-1ddce2 (zero-compute column plus the S_4/S_5 builders
the lane needs anyway). Third: IDEA-20260926-120d6a (dimension tables now,
spurious-lift measurement later). Fourth: IDEA-20260926-0d1d74 (an instrument
whose predicted outcome is a priced closure of the Nagao/RR row).

## Ranking rationale (expected information gain versus cost)

None of the four moves an exponent, and each says so. 197ecf has the highest
gain per CPU-hour: a free multiplicative correction to the budget column
decided by exact counting. 1ddce2 corrects which encodings are even writable
at m >= 5 and restates the seam as a solver gap (2^55 under the cap model,
2^73 under the producer's model at m = 5), which is the honest target. 120d6a
and 0d1d74 each close one of the seam's named candidates with a mechanism
(product-space saturation plus a free action; residual degree 2^{l+1}) and
carry a cheap toy validation with a surprise branch.

## Inventor-protocol section 5 block

**Objects considered.**
1. The ordered relation vector with coefficients lambda^{m-k} (tau-Horner
   chain), Sigma = {Horner step u -> tau(u) + P, tau, negation} — 197ecf.
2. The factor base described implicitly by its 2-polynomial L_V (or the 131
   conjugate 2-polynomials of an orbit union), used as a membership oracle
   inside a decomposition; Sigma = translation by base elements — 0d1d74.
3. The chained presentation as a materialised object (size, not solve);
   Sigma = translation along the chain — 1ddce2.
4. The elementary-symmetric coordinates e_k in the product spaces V^(k),
   Sigma = S_m, negation, diagonal Frobenius — 120d6a.
5. The Frobenius-twisted univariate polynomial of b48c9d's coupled object,
   Sigma = {tau, same-representative translation} — considered, not filed.
6. Two-representative coupled shapes Q = f(tau)P_1 + g(tau)P_2 — considered;
   reduces to b48c9d's accounting with two scalars and was not filed.

**Depth of verified structure.** All derivations are this session's hand
arithmetic at proposal tier: the rotation identity for squared nodes, the
m! ordered-versus-multiset count, the re-balanced budget shifts (2.1-2.7
bits), the 2-polynomial reduction cost, the degree 2^{l+1} of the
last-two-summands residual, the chained dense bound (C(285, 3) = 3,818,090;
2^30.9 at m = 5), and the product-space dimensions k(l-1) + 1. Nothing is
measured; every number is flagged for Python recomputation.

**dominated_by.** For every filed proposal: matched Pollard rho with negation
and 131-fold Frobenius classes at 2^60.81 (KN-FIND-aa2efc, KR-RHO-18cc42,
KR-RHO-037e22) dominates on time and memory; the (m-1)-loop
(IDEA-20260904-96c4f3) and the two-list MITM (IDEA-20260922-845a77) dominate
or tie every priced per-attempt row; the orbit-union decomposition
(KN-FIND-47da4e, KR-IC-b0fcda) contains 197ecf's pattern as one of 131^{m-1};
the subfield symmetrisation and gcd rows (KR-IC-955fd6, KR-IC-081a58,
KR-IC-a4dd54) do not apply at prime n and are not improved. No proposal claims
a row of its own; 1ddce2 and 120d6a are `n/a (no result claimed)` after the
row-by-row check.

**sota_delta.** Zero on time, memory and data for all four. Conceptual
deltas: (197ecf) the m! of the product law is removable at identical descended
shape on a Koblitz curve, worth about 2.3 bits on the m = 5 budget; (0d1d74)
the O(l D^2) membership law for subspace and orbit-union bases and the
residual-count criterion; (1ddce2) the chained materialisation column
(2^30.9, 2^31.2, 2^31.7 at m = 5, 6, 8) against the unchained +40.8-bit
deficit; (120d6a) the saturation table at ECC2K-130's balanced l.

**Enumerated closures, with mechanism (section 4 standard).**
- C1. S_m symmetrisation on a subspace base at m >= 5, n = 131: the
  symmetrised unknown count sum_k min(k(l-1) + 1, 131) exceeds ml at every
  balanced l (335 versus 115 at m = 5, l = 23), so the m! is relocated into
  the Vieta lift; Frobenius extension acts freely (a77711 A2/A3). Scope:
  polynomial-basis and random subspaces; not subfield bases. Forward
  guidance: what remains is a factor base whose product spaces do not grow,
  which at prime n means a non-linear base (b6cc43's ball, a17f43's successor
  object) whose symmetrised coordinates are unstudied.
- C2. Nagao / Riemann-Roch encodings on a subspace or orbit-union base at
  m = 5, 6 are the (m-1)-loop with a constant: the last-two-summands residual
  has degree 2^{l+1} and the parameter scan has success fraction
  |F_V|^m / (m! 2^{131 m}). Scope: the two named encodings. Forward guidance:
  the escape is a residual of degree poly(m) with residual count below
  |F_V|^{m-2}, which the subfield case has and the subspace case does not;
  any Koblitz-specific polynomial identity collapsing several summands into
  one small residual over the union would reopen it.
- C3. Materialisation: the unchained S_{m+1} is not writable on ECC2K-130 at
  m <= 8 (EV-ICPERF-784b25), the chained form is (about 2^31 at m = 5); under
  the producer's model even the chain exceeds the budget at m <= 8, under the
  cap model it fits and the solver gap is 2^55 at m = 5. Scope: subspace
  bases, chained topology of KN-TECH-b18366.
- Not closed: the twisted one-variable object (id returned; direction open);
  the coupled two-representative shape; whether GGMP's symmetry-breaking
  construction already is the tau-Horner chain (a reading task).

**Open directions for the next session.**
1. Read GGMP eprint 2020/1315 section on symmetry breaking against 197ecf;
   if identical, re-file 197ecf's pricing as `known` with the paper as `same`.
2. The twisted univariate object of G3's open direction 2 (id 009cb9
   returned): its degree structure with the shift window bounded, and whether
   any pattern-free form has sub-field-size degree; not filed here.
3. A solver-side record for the chained oracle at m = 5 on cap-locus cells
   (4b65e3's ladder) now that 1ddce2 states the gap it must close.
4. Non-linear bases (b6cc43's Hamming ball) under symmetrisation, where C1's
   saturation argument does not apply as stated.

## Novelty and provenance

No web search was run. External ingredients are `recalled` (HPST 2013,
von zur Gathen-Gerhard root finding, Solinas TNAF) or `kb` (KN-LIT-0d9d28's
abstract sentence on Frobenius and symmetry breaking) and are marked so. Every
internal record cited was read in full unless its citation says otherwise.
Greps run: "symmetris", "symmetriz", "Nagao", "Riemann-Roch", "twisted",
"S_5", "S_6", "arity", "orbit union", "coupled", "Horner", "tau-chain",
"symmetry breaking", "modular composition", "gcd against", "subspace
polynomial", "linearized polynomial", "ANF", "materialis", "chained",
"elementary symmetric", "product space", "Vieta", "invariant ring". All four
records carry a `prior_art` block against the rendered frontier map and are
`novelty_status: unverified`.

## Files written

- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-197ecf.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-0d1d74.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-1ddce2.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-120d6a.yaml
- /home/user/crypto-autoresearcher/analysis/binstd-idea-review-20260926/reviews/TASK-20260926-12a355-generator-report.md

Not written: ledger/proposals/IDEA-20260926-009cb9.yaml (id returned unused).
No other path was touched.
