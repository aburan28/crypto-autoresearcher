# TASK-20260926-b3c93a — generator report, seam G3

Lane: representation and relation-collection objects specific to ECC2K-130's
own structure. Agent: idea-generator (research-deep). Date: 2026-09-26.
No run, no status change, no existing record edited. Three proposals filed;
the fourth pre-minted id is returned unused (reason below).

## Proposals filed

| id | class | question | claim (25 words) | representation / Sigma | target m | novelty | cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IDEA-20260926-b48c9d | mechanism | RQ-BINSTD-b6f698 | The tau-adic factor base over an orbit-union base is a Gamma-orbit quotient; free-oracle attempts 2^131/#patterns reach rho only at w >= 13; enumerated form is a 2^{131-l'/2} walk. | R3 (representative, tau-adic scalar); Sigma = {tau, negation, +tau^j(P) same P}; Class I partial-action | w >= 13 (free oracle), closure predicted at every w | unverified | impl medium, compute low (pure Python, n = 19) |
| IDEA-20260926-b6cc43 | representation | RQ-CERTBIN-836ce2 | Hamming ball B_w in a normal basis is a Frobenius-stable factor base at n = 131 with no shift variables; the DP predicate is B_34; priced by cardinality-constrained descent. | R1 (normal basis); Sigma = {sigma rotation, negation} + partial translation; Class I | m = 4, w = 6, |F| about 2^32.7 | unverified | impl medium, compute low (CERTBIN impl, n = 17/19) |
| IDEA-20260926-cafcf1 | control | RQ-BINSTD-b6f698 | Abscissa density of a subspace base is Weil-uncontrolled for l <= n/2 + 1 (all l <= 66 at n = 131); Tr(x) = Tr(1/x) reads b = 1; ceiling 2^m. | R1; Sigma = {sigma, x -> 1/x}; Class III coordinate-dependent | any m; yield factor <= 2^m | unverified | impl low, compute low (exact counting) |

Unused id: IDEA-20260926-d128eb. The two remaining seam items — the E/2E,
E/4E cofactor chain and the descent-basis confound — were filed the same day
by the G2 lane as IDEA-20260926-ae8f0a (E/4E two-bit leg label) and
IDEA-20260926-917981 (Proposition B: Macaulay and mutant closures are
basis-invariant, depend only on the set V). I had derived both independently
(the E/4E class map by one point halving; the GL(l, F_2) ring-automorphism
invariance of M_D and W_D) before grepping and finding them filed; writing
them again would be a duplicate, so the id is returned. The 2-torsion
translation x -> 1/x and the u-line base were already IDEA-20260922-29b1c5.

## Which to test first, and why

**IDEA-20260926-b6cc43** (the Hamming ball). It is the only genuinely new
tracked-object description in the seam: it passes the lossy-projection test
against a named Sigma, it exists at n = 131 where every linear
Frobenius-stable base does not (IDEA-20260918-9abf42), it answers the open
direction KN-FIND-47da4e names explicitly ("changes the coordinate blocks
rather than the index over shifts"), and it is measurable in minutes on the
installed CERTBIN instruments with three matched controls (size-matched
subspace, random set of equal cardinality, ordinary curve of the same n).
Its minimal test is the cheapest valid discriminator because RC-1 is already
a supported cell (DEC-20260926-cb4487): Stage 1 reproduces RC-1 unchanged,
and the ball arm differs from it in one declared component (the constraint
rows), so any difference is attributable. The two outcome bands
(closure-work ratio in [0.5, 2] with equal refutation rate, versus above 2
or lower refutation) do not overlap and are fixed before any run.

IDEA-20260926-b48c9d second: its predicted outcome is a closure with a
mechanism and a number for the tau-adic column of the reachability table,
which the brief asked for by name; the surprise branch (a coupled-shift
solve cheaper than enumeration) would be the first such gain in the program.
IDEA-20260926-cafcf1 third: zero-compute correction now, cheap measurement
later, ceiling 2^m.

## Ranking rationale (information gain versus cost)

All three are constant-factor or closure-shaped and say so; none moves an
exponent, and the honest reason is structural (see closures). b6cc43 has the
highest information gain per CPU-hour because either outcome is a measured
number for RQ-CERTBIN-836ce2's decision target (2) on a base no earlier
record could build at n = 131. b48c9d's gain is a table cell with a named
mechanism, plus a low-probability surprise. cafcf1's gain is a correction to
the reviewed HOLD-B cluster at zero compute.

## Inventor-protocol section 5 block

**Objects considered.**
1. The pair (representative in an orbit-union base, short tau-adic scalar),
   Sigma = {tau, negation, same-representative translation} — b48c9d.
2. The necklace class of the normal-basis coordinate vector and the weight
   ball B_w as a rotation-closed factor base, Sigma = {sigma, negation} —
   b6cc43.
3. The twist-selector bit phi(x) = Tr(x) + Tr(1/x), Sigma = {sigma, x -> 1/x}
   — cafcf1.
4. The E/4E class map c(P) = (Tr(x_P), Tr(x_{P/2})) with x_{P/2} a root of
   X^2 + sqrt(x_P) X + 1 (both roots have equal trace on E_0, since
   Tr(1/x) = Tr(x) on abscissae) — derived, then found filed as
   IDEA-20260926-ae8f0a; not proposed.
5. Basis invariance of M_D and W_D under GL(l, F_2) (squaring is additive,
   so the Boolean-ring degree filtration is preserved) — derived, then found
   filed as IDEA-20260926-917981; not proposed.
6. The separable degree-2 endomorphism tau-bar = -1 - tau with
   x(tau-bar P) = x + 1/x and kernel {O, T}; the tau-bar-preimage factor base
   {x : x + 1/x in W} — found to be IDEA-20260922-29b1c5's u-line base, and
   its decomposition system is the system for the target tau-bar R
   (equivariance, IDEA-20260906-a77711); not proposed.
7. Mixed-twist solutions of S_{m+1} over V (x_i on E_1 rather than E_0):
   they split into an arity-k relation on E_0 and an arity-(m-k) zero-sum
   on E_1 by applying the 131-Frobenius, so their expected count is the
   product of two smaller-arity counts, negligible at balanced |F|; not
   proposed.
8. Circulant structure of the descended system in a normal basis (the j-th
   equation is the rotation of the 0-th with the target rotated too):
   equivariance between conjugate targets, not a symmetry of one instance;
   not proposed.

**Depth of verified structure.** All derivations are this session's hand
arithmetic at proposal tier: the abscissa condition, x(P + T) = 1/x,
x(tau-bar P) = x + 1/x, the Kloosterman Fourier bound, the ball sizes,
|Gamma_13| about 2^71, and the n = 19 Koblitz order 4 * 130873 (trial
division to 361, primality unchecked by machine). Nothing is measured.

**dominated_by.** For every filed proposal: matched Pollard rho with negation
and 131-fold Frobenius classes at 2^60.8 iterations (KN-FIND-aa2efc,
KN-LIT-661e97) dominates on time and memory; the orbit-union m = 4 row of
analysis/frobenius-orbit-ecc2k130 (per-solve budget 2^30.6, unmeasured at
n = 131) is the sibling row b6cc43 must beat on per-attempt cost by more than
KN-FIND-47da4e's 1.0-1.5x; QSP rows void (IDEA-20260916-3f7a1c); BSGS and
van Oorschot-Wiener dominate the time-memory curve; MOV, SSSA, GHS
inapplicable. No proposal claims a row of its own.

**sota_delta.** Zero on time, memory and data for all three. Conceptual
deltas: (b48c9d) the coverage law 2^131 / (C(131,w) 2^w), the w >= 13
threshold, and the 2^{131 - l'/2} collision cost; (b6cc43) a Frobenius-stable
factor base of index-calculus size at n = 131 with O(1) description and no
shift encoding, and the DP predicate as its radius-34 member; (cafcf1) the
vacuity threshold l <= n/2 + 1 for the Weil control of abscissa density and
the correction to HB1-2 / H1's stated support.

**Enumerated closures, with mechanism (section 4 standard).**
- C1. Every endomorphism alpha in Z[tau] acts on the prime-order subgroup G
  as a scalar (Z[tau]/(rho) = F_l, rho = Phi_131(tau) the prime of norm l with
  G = E[rho]). Hence any object built from End-images of FACTOR-BASE points
  is a table of known multiples (IDEA-20260807-45a69f's incidence oracle;
  b48c9d's Gamma_w quotient is the orbit-union instance, generic by the
  relabelled control), and any object built from End-images of TARGETS is an
  equivariance between conjugate instances (IDEA-20260906-a77711; objects
  6 and 8 above). Scope: objects that use End on the GROUP. Forward guidance:
  what remains is End acting on COORDINATES — rotation in a normal basis,
  x -> x + 1/x on the x-line — which defines invariant SETS with non-linear
  membership (b6cc43) and coordinate statistics (cafcf1), both constant-
  factor by the GGMP accounting unless a per-attempt solve cost moves.
- C2. The tau-adic factor base in enumerated form is a walk-collision at
  about 2^{131 - l'/2} >= 2^66 scalar multiplications, generic; the escape
  (coupled one-hot solve) is priced, not closed (b48c9d).
- C3. Mixed-twist solutions of the summation system are products of
  smaller-arity relations and contribute negligibly (object 7); zero-compute
  argument, unmeasured.
- Not closed: the per-attempt cost of a cardinality-constrained decomposition
  (b6cc43's open number); the maximum abscissa density of a constructible
  subspace family at l <= n/2 (cafcf1's open number).

**Open directions for the next session.**
1. A native-cardinality SAT arm for b6cc43 (WDSat with pseudo-Boolean
   constraints, or CaDiCaL with a cardinality encoding) — needs an engine
   that is not installed.
2. The coupled Frobenius-twisted summation polynomial
   S_{w+1}(x^{2^{j_1}}, ..., x^{2^{j_w}}, x_Q) as a one-variable object in its
   own right: its degree structure over F_{2^131} (each x^{2^j} is a
   linearised polynomial) may admit a root-finding route that is not a
   Weil descent at all; unexamined.
3. Whether subspaces of ker Tr avoiding the Kloosterman zero set
   {x : Tr(1/x) = 1} have a coding-theoretic characterisation (cafcf1 F3).
4. The E/4E label (ae8f0a, G2) composed with the ball: even weight is the
   E/2E bit on G; the second bit's distribution over B_w is unmeasured.

## Novelty and provenance

No web search was run. Every external ingredient is `recalled` and marked
so (tau-adic NAF density, Weil bound for Kloosterman sums, type-II ONB
existence, Fourier inversion over a subspace); every internal record cited
was read in full unless its citation says otherwise. Greps run: "tau-adic",
"Z[tau]", "TNAF", "normal basis", "Gaussian normal", "Kummer", "x-only",
"distinguished point", "orbit union", "target-dependent", "Tr(1/x)",
"trace-parity", "Hamming ball", "cardinality constraint",
"rotation-invariant", "E/4E", "basis-invariant", "Kloosterman". All three
records are `novelty_status: unverified`.

## Files written

- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-b48c9d.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-b6cc43.yaml
- /home/user/crypto-autoresearcher/ledger/proposals/IDEA-20260926-cafcf1.yaml
- /home/user/crypto-autoresearcher/analysis/binstd-idea-review-20260926/reviews/TASK-20260926-b3c93a-generator-report.md

Not written: ledger/proposals/IDEA-20260926-d128eb.yaml (id returned unused,
see above). No other path was touched.
