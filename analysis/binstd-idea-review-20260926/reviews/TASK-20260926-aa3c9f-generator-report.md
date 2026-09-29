# TASK-20260926-aa3c9f generator report (seam G2, idea-generator)

Lane G2: the solver-side asymmetry at the measured CERTBIN cells. Four
schema-complete proposals filed under `RQ-CERTBIN-836ce2` (R2 rule: measured
decomposition mechanisms on prime-degree siblings). Every record is
`status: proposed`, `approved_by: null`, `novelty_status: unverified`, and
prices itself against the product-law floor of BRIEF section 2 and the two
supported cells (DEC-20260926-cb4487, DEC-20260926-901ea1). No runs, no status
changes, no imagined outcomes; every number is copied from a named internal
record or re-derived and labelled here.

## One line per idea

- **IDEA-20260926-89886c** (algorithm, RQ-CERTBIN-836ce2). A sound early-abort
  mutant-closure filter (W_3 then W_4) on the chained S_3 descent at m=3, priced
  per attempt as ops-to-first-1 on UNSAT versus ops-to-fixpoint on SAT and
  against 2^{(m-1)l} enumeration, with the miss rate and diagonal crossover l*
  stated first. Bears on m=3 (and the m>=4/m>=5 product-law rows as a building
  block); does NOT move the m<=3 ECC2K-130 closure. novelty unverified. Cost:
  impl medium, compute ~10^1-10^2 CPU-h (estimate).
- **IDEA-20260926-917981** (control, RQ-CERTBIN-836ce2). Two exact propositions:
  Macaulay/mutant closure outcomes are invariant under change of field basis and
  of the basis of V (so normal-vs-polynomial descent is a change of coordinates
  for the closure, not a confound), and squaring transfers a W_D certificate
  across a Frobenius orbit of targets (the known 1/n, not a new gain); the live
  object is the SET V, tested on RC-1 with polynomial, normal-coordinate and
  Frobenius-stable V. Bears on every arity by removing a confound; no cost claim.
  novelty unverified. Cost: impl low, compute ~1 CPU-h.
- **IDEA-20260926-a79052** (representation, RQ-CERTBIN-836ce2). Trace-conditioned
  factor base V_T = {x in V : Tr(x)=Tr(1/x)+Tr(a)} on Koblitz siblings
  (identity re-derived), removing unsatisfiable-by-non-membership attempts as a
  free precompute filter; measured as a by-non-membership share against the
  ordinary RC-1 curve. Bears on the m=2 attempt mix (free at any m); honest prior
  is E-NULL (oracle A already root-finds on the curve). novelty unverified.
  Cost: impl low, compute ~1 CPU-h.
- **IDEA-20260926-ae8f0a** (mechanism, RQ-CERTBIN-836ce2). HOLD-O's corrected
  reading of e3048d made constructive: enumerate the cyclic-Z/4 2-Sylow chain
  E->E/2E->E/4E as a two-bit Z/4 leg label pi_4 (trivial on the prime-order
  targets by Lagrange, live on legs), turning the search into four Z/4-sum parity
  cells; measured as a by-coset unsatisfiable share on the h=4 RC-1 curve against
  a cofactor-1 null and a relabelled Z/4 x Z/l generic-group control, answering
  IDEA-20260922-153a90 part C's depth-2 open number. At most a 2-bit attempt-mix
  constant, immaterial against rho; honest prior E-SUBSUMED (pi_2 carries most of
  it). novelty unverified. Cost: impl medium, compute ~1-2 CPU-h.

## Test first, and why

**IDEA-20260926-89886c**, with its **W_3 rung as the cheapest valid
discriminator**. It is the only seam-G2 proposal whose positive outcome supplies
a number the program does not have — a sub-enumeration per-attempt cost law at
m>=3, the one arity where the product law leaves any lever — and whose negative
outcome closes the W-type filter at m=3 with a measured obstruction. The W_3
rung alone (seconds per attempt on the existing closure.py) decides E-W3 and
lower-bounds r_4 before any expensive W_4 pass, and it sits exactly where
DEC-20260926-901ea1 n19_dr9_ruling already made an m=3 W_4-type pricing design
eligible for ranking. It inherits that decision's ordering: behind the
which-algebra successor (NA-2), whose outcome says whether the refuting structure
is stable enough to price. 917981 is the cheapest overall and is a prerequisite
building block (it retires the descent-basis confound by proof for every
closure-based cost law, including 89886c's), so it should run alongside as a
zero-to-one-hour instrument regression, but it moves no number by itself.

## Honest-accounting block (inventor-protocol section 5)

- **Objects considered.** (1) The degree-D mutant closure W_D of the descended
  ideal as an early-abort refutation filter, with the two-quantity per-attempt
  cost law (89886c). (2) The pair (set V, x_R) that a closure actually depends
  on, with change-of-basis quotiented out (917981). (3) The Koblitz
  trace-membership set V_T as a leg filter (a79052). (4) The 2-Sylow Z/4 coset
  chain pi_2 -> pi_4 as a leg label (ae8f0a). Objects 2-4 are lossy projections
  passing the lossy-projection test against a named operation set; object 1 is a
  solver-side truncation, coordinate-independent by object 2's Proposition B.
- **dominated_by.** All four: **n/a (no attack claimed)** at the measured cells,
  after checking the frontier rows named in each record — parallel Pollard rho
  with negation and the 131-fold Frobenius class at 2^60.81 on ECC2K-130
  (KN-FIND-aa2efc / CORR-20260922-81aeab), oracle A (2^l root-findings per
  attempt) and the enumeration oracle (2^{(m-1)l}) at the toy cells, and the
  product-law floors (m=3: 2^68.58; m=4: 2^56.40; m>=5 the only rows below rho).
  Every proposal is per-attempt or attempt-mix and cannot move a total-cost row;
  each says so.
- **sota_delta.** Zero on every ECDLP cost axis (time, memory, data) for all
  four. Quantitatively: 89886c changes a per-attempt exponent from 2^{(m-1)l}
  (enumeration) to polynomial-in-N at fixed D on the refuted fraction, but only
  at toy m=3 and never past the product law on ECC2K-130; 917981 changes no
  number (it removes a confound by proof and re-derives the known 1/n); a79052
  removes at most a ~1/2 attempt-mix constant on the Koblitz sibling (likely 0,
  E-NULL); ae8f0a removes at most 2 bits of attempt mix (likely subsumed by the
  1 bit of pi_2). The program-relative delta is the new measurements: the first
  W-type refutation rate and ops asymmetry at m>=3 (89886c); the closure-basis
  invariance and Frobenius-orbit certificate transfer as exact propositions
  (917981); the first by-non-membership share at the CERTBIN cells (a79052); the
  enumerated 2-Sylow chain with a measured level-2 by-coset share, answering
  153a90 part C at depth 2 (ae8f0a).
- **Enumerated closures (with mechanism, at the section-4 standard where met).**
  None asserted by this session; each proposal instead names the closure its
  NEGATIVE outcome would establish, with the obstruction to be MEASURED, not
  declared: 89886c's E-FAIL-3 (W-type filter void at m=3 because the chain node's
  products reduce modulo f and destroy the convolution structure of
  KN-FIND-c3a917 — mechanism named, share to be measured); a79052's E-NULL (the
  builders already sample on-curve, so V_T=effective V — mechanism is oracle A's
  root-finding, to be confirmed by code inspection); ae8f0a's E-SUBSUMED (the
  level-1 bit pi_2 captures the removable coset structure, so the point-halving
  cost of pi_4 is not repaid — the depth-2 answer to 153a90 part C). Each meets
  the section-4 standard only after its measurement; filed as unverified, as
  required.
- **Open directions for the next session.** (i) If 89886c returns E-PERSIST-3,
  the m>=4 pricing design the product law's 2^4.4-per-attempt budget makes live
  — the one route that could touch ECC2K-130 — with the crossover l* under H2 as
  its input. (ii) The which-algebra successor (DEC-20260926-901ea1 NA-2, W_3
  across all arms plus a perturbation ladder), which 89886c is ranked behind and
  which decides whether the refuting structure is stable enough to price at all.
  (iii) The KN-OPEN-3c8f51 item (A) mechanism question (what separates S_3 from
  its tensor neighbourhood, seen only at D=3), on which 917981's set-versus-basis
  separation bears. (iv) Deeper 2-power leg levers on the high-2-adic ANSI curves
  (c2tnb431r1, valuation 5), the depth-i>2 continuation of ae8f0a and 153a90
  part C.

## Files written

- `ledger/proposals/IDEA-20260926-89886c.yaml`
- `ledger/proposals/IDEA-20260926-917981.yaml`
- `ledger/proposals/IDEA-20260926-a79052.yaml`
- `ledger/proposals/IDEA-20260926-ae8f0a.yaml`
- `analysis/binstd-idea-review-20260926/reviews/TASK-20260926-aa3c9f-generator-report.md` (this file)

All IDs pre-minted by the dispatching session; not minted by this agent. No
existing record was edited; nothing outside the declared write scope was
written.
