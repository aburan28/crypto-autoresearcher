# ECDLP-IDEA-107 — Finite-field witness transport

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_membership_no_go`
- Evidence scale: no run; any transport diagnostic is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: algebraic continuation can leave a frozen factor base and later
  return to it, but no new operation raises the endpoint-return density, finds a returning
  specialization, or avoids full monodromy-orbit and branch-switching cost.
- Breakthrough claim: **none**; a tracked branch, monodromy orbit, valid relation, or toy
  scalar is not an ECDLP break.

## Falsifiable hypothesis

Start with one known factor-base decomposition in a parameterized family of Semaev
systems and transport it along public parameter loops to a new output `R`. The proposed
claim is that finite-field Frobenius/étale monodromy acts transitively enough that a
sub-rho number of tracked paths produces exact factor-base witnesses for random known
outputs and masked targets. Repeating the process would collect `B+sigma` full-rank rows,
solve all factor logs, and perform blind descent below rho and BSGS. The claim is rejected:
the proposal supplies no source-blind bias toward returning endpoints, no cheaper search
for a returning specialization, and no compact rule for choosing the correct returning
branch from the full monodromy orbit.

## Mechanism-new operation

The screened operation is **transport a source-labelled solution branch through an
algebraic parameter family using finite-field monodromy/Frobenius loops, then specialize
the transported branch to an exact frozen-factor-base witness**. Generic numerical
homotopy, solving each new fiber, transporting unrestricted curve points, or filtering a
transported point into `F` afterward are controls. A branch may leave `F^m` and return at
a later specialization; the rejection does not deny that possibility. It charges the
density and search cost of those returning specializations, every branch switch, and the
complete monodromy/Frobenius orbit needed when no public selector exists. Without a new
return-density or source-selection operation, this proposal semantically merges with
IDEA-043's monodromy full-fiber output, IDEA-074's Frobenius-orbit lift, and IDEA-087's
degeneration-plus-source-lift obligation.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target
   `Q=[x]P`, fixed arity `m`, and target-independent factor base
   `F={F_1,...,F_B}` with `B=N^beta`.
2. A parameterized polynomial family contains the complete signed relation fibers and has
   an exact finite-field analogue of path continuation with source labels preserved.
3. A public seed fiber and witness are available without using hidden target information
   or precomputing a source table.
4. A transported branch may leave `F^m`; accepted endpoints must return to exact points
   of `F`, including signs and multiplicities, at arbitrary known and masked targets.
5. Family construction, extension fields, loops, path/branch count, failures, endpoint
   membership, source output, relation density, rank, descent, verification, and memory
   are charged.
6. Any diagnostic remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`parameterized_Semaev_family | finite_field_etale_monodromy | unrestricted_branch_transport | returning_factor_base_specialization | full_orbit_or_branch_switch_output | blind_descent`

The no-go key is `unrestricted transport + rare frozen-base endpoint return + no public
returning-branch selector`. Continuous membership would force local constancy, but a
leave-and-return path is logically possible; it receives credit only after its endpoint
density, specialization search, full orbit output, and source verification are charged.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H644`, the closest batched non-Gröbner
   point-decomposition lane with full relation and descent accounting.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1051`, where public-coordinate and
   row-coefficient identities do not create a source-producing relation operation.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1400`, where quotient certificates
   preserve relation counts but do not selectively recover sources.
4. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-044`, which blocks credit for
   ordinary cover smoothness without a new source operation.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H642`, the structured-coordinate and
   source-inversion barrier that path tracking does not remove.

## Closest primary literature

- Duff, Hill, Jensen, Lee, Leykin, and Sommars,
  [Solving polynomial systems via homotopy continuation and monodromy](https://arxiv.org/abs/1609.08722),
  study numerical continuation in a generic parametric family and show expected path
  counts roughly linear in the number of solutions under a uniform-monodromy assumption;
  they do not preserve finite factor-base membership over finite fields.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the comparison polynomial fibers and requires bounded/factor-base solutions.
- Duff et al.,
  [published monodromy-solver description](https://doi.org/10.1093/imanum/dry017),
  is the journal version of the parametric solution-set method, not a finite-field source
  transport theorem.

No checked source supplies a finite-field returning-specialization theorem that improves
frozen-factor-base endpoint density or selects a source branch without traversing the full
monodromy orbit. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, parameter family, seed fiber, loop graph, extension fields,
   exact continuation rule, membership test, and exhaustive tiny source truth.
2. Construct a seed output `R_0=[r_0]P` and a known signed tuple in `F` without target
   advice; independently verify the family and every exceptional branch.
3. For random known outputs `R_j=[r_j]P`, track the source-labelled branch along frozen
   loops, specialize it, require every endpoint point to lie in `F`, and verify the sum.
4. Retain every escaped point, failed lift, branch collision, duplicate tuple, miss, and
   dependency; collect `B+sigma` verified rows of rank `B`.
5. Solve and independently verify every factor-base logarithm modulo `N`.
6. Freeze the transport graph and apply it unchanged to masked blind targets `Q+[t]P`,
   retaining all monodromy branches and endpoint ambiguities.
7. Substitute factor logs, unmask all candidates, and accept only after verifying
   `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`. Let family, seed, and loop construction
take `N^(a+o(1))` time and `N^(a_m+o(1))` memory. Let the number of monodromy/Frobenius
branches that must be traversed or switched among be `N^(g+o(1))`; let extension-field
arithmetic per branch take `N^(e+o(1))` time and `N^(e_m+o(1))` memory; and let exact
transport per branch take `N^(q+o(1))` time. Let `t_m` be the peak-memory exponent for
the complete scheduled transport state, including all simultaneously retained branches,
path coordinates, loop data, and extension elements. Let `N^r` and `N^r_t` be the
reciprocal probabilities, and hence unbiased search exponents, for a transported known or
masked-target specialization respectively to return with every source coordinate in
`F`. Let accepted endpoint/source output have exponent `o`, and let residual scalar
ambiguity per emitted target source have exponent `u`; writing these lists costs their
full time and storage. Let sparse linear algebra take `N^(ell+o(1))` time and
`N^(ell_m+o(1))` memory, with `ell>=2beta` absent proved structure. Let verification of
one endpoint tuple or scalar candidate take `N^(v+o(1))` time and `N^(v_m+o(1))`
working memory.

The complete time exponent is

`lambda=max(a,beta+r+g+e+q+o+v,ell,r_t+g+e+q+o+u+v)`,

and the complete peak-memory exponent is

`mu=max(a_m,e_m,t_m,ell_m,beta,o+u,v_m)`.

Every loop, extension element, traversed or switched branch, failed returning
specialization, membership rejection, full-orbit output, source tuple, ambiguity branch,
and verifier operation is charged. An expected path count linear in the number of
unrestricted solutions cannot beat rho when `r,r_t,g,t_m`, and endpoint output are
omitted.

## Likely fatal obstruction

An unrestricted branch can leave `F^m` and later return, but absent a proved bias the
fraction of an output fiber lying in a frozen base is occupancy-like: among unrestricted
`m`-tuples it is approximately `(B/N)^m=N^(-m(1-beta))`. Finding a returning
specialization can therefore dominate rho even before row rank and blind descent. If
monodromy is transitive, following one labelled seed to a desired return additionally
requires branch switching, a selector, or output of the full orbit; the latter can have
the full solution-degree exponent. Finite-field Frobenius transport can also require an
extension comparable to that orbit. These are the same unremoved output/orbit/source-lift
obstructions recorded by IDEAs 043, 074, and 087.

## Proof track

Prove a target-independent return-density amplification theorem, give a public algorithm
that finds returning specializations and selects their exact source branches without a
decomposition oracle or full-orbit output, bound extension and branch-switching costs,
and complete the seven-step rank and blind-descent proof with `lambda,mu<1/2`.

## Disproof track

Measure returning-endpoint density against `(B/N)^m`, show that locating a return is
equivalent to fresh endpoint-membership search, require full monodromy-orbit output or an
unavailable branch selector, or establish `r`, `r_t`, `g+e+q`, `t_m`, `lambda`, or `mu`
at least `1/2`. Any one closes the proposal as written.

## Positive and negative controls

- Positive continuation control: a generic complex polynomial family with published
  monodromy behavior and independently known solutions.
- Positive finite-field control: a family whose unrestricted solutions form an explicitly
  computable Frobenius orbit.
- Negative membership control: transport unrestricted branches and compare their endpoint
  return rate to a matched `(B/N)^m` occupancy baseline.
- Mechanism controls: solve each Semaev fiber independently, transport unrestricted
  points, and post-filter endpoints into `F`.
- Leakage control: seed loops must not be selected from the desired target witness.
- Baseline control: matched Pollard-rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

No promotion gate remains for this membership-cost no-go formulation. A successor must
first prove target-independent return-density amplification and a public returning-branch
algorithm that is cheaper than endpoint-membership search and full-orbit output. Any
later toy study would require zero endpoint-membership errors, exhaustive agreement
through 18 bits, `1,000` independent rows, `100` blind descents, fresh rank at least
`0.8B`, and upper 95% bounds `lambda,mu<=0.45` under the complete formulas above.
Falsify immediately if the return rate matches `(B/N)^m`, finding a return reopens fresh
membership search, or branch selection requires the full monodromy/Frobenius orbit.

## Artifact plan

- No-go proof: `ideas/artifacts/ECDLP-IDEA-107/frozen_membership_transport_no_go.md`
- Family specification: `ideas/artifacts/ECDLP-IDEA-107/transport_family.yaml`
- Diagnostic branch tracker: `ideas/artifacts/ECDLP-IDEA-107/track_branches.sage`
- Independent endpoint verifier: `ideas/artifacts/ECDLP-IDEA-107/verify_endpoints.py`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-107/analysis.md`
- Any diagnostic receipts: `ideas/artifacts/ECDLP-IDEA-107/runs/<run-id>/`

## Interpretation boundary

This rejected record is toy, heuristic, model-bound, and novelty-unverified. A successful
homotopy path, transitive monodromy action, exact transported point, valid relation, or toy
scalar does not show a better-than-rho algorithm. Frozen factor-base membership and blind
source recovery remain the closed obstruction because return density, returning-
specialization search, branch switching, and full-orbit output are unpaid.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-107/frozen_membership_transport_no_go.md` deriving the returning-endpoint density and charged specialization-search, branch-switching, extension, and full-monodromy-orbit bounds for the proposed transport family.
