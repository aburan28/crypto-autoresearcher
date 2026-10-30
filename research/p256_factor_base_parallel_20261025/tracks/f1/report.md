# F1: symmetric membership and generic torus cosets on P-256

2026-10-25 · TASK-20261025-cfb933 · implementation validation and exact mathematical
screening. This is neither an official performance trial nor a hypothesis
transition. No EXP identifier, speed advantage, or complete ECDLP claim is made.

The delivered symmetric quadratic membership circuit works over the published
P-256 field. Two actual algebraic solution formulations were exercised. Complete
finite-domain decomposition sets pass a separate replay implementation. Global
implicit solving remains open: backward recursion enumerates the full triple
space, while expanded forward elimination already needs explicit handling of
nonreduced symmetric fibres.

## Fixed inputs and environment

The input commit supplied by the Coordinator is
`2c8c71cfff6f7f63297fbe4de4608cd94d857184`. Exact committed constants and the current
35-term S4 polynomial are loaded from `baseline/parameters.py` and
`baseline/s4-symmetric.json`; their SHA-256 digests are in
[checks-02/checks.json](checks-02/checks.json). P-256 means

```
p = 2^256 − 2^224 + 2^192 + 2^96 − 1
a = −3
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
r = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
h = 1.
```

The implementation uses `/workspace/dickson-solver/.venv/bin/python`: CPython
3.12.14, SymPy 1.14.0, python-flint 0.8.0. The repository-prescribed
`/usr/local/bin/python3` is absent; that failed probe is retained. No installation,
Docker use, Git action, PR edit, or shared-file edit was performed. The shared
working tree is managed by the parent session; this track adds its scoped source
and artifacts and does not assert a clean tree. Runtime model binding is inherited
and unprobed. Hardware timing and peak memory were not measured: resource watchdog
limits and algebraic operation/state counts are reported, without a timing study.

## Derived construction

For elementary symmetric coordinates (u,v,w) of three input coordinates, one
Dickson step x↦x²−2 induces

```
Φ(u,v,w) = (u²−2v−6,
            v²−2uw−4u²+8v+12,
            w²−2v²+4uw+4u²−8v−8).
```

The terminal equations are Φᵏ(u,v,w)=(3c,3c²,c³), joined to S4. Generic terminals
are c=Tr(z₀^(2^k)), c≠±2, for z₀ in the norm-one torus over Fp². Every exact-order
power-of-two torus generator is certified by exponentiation. Generic domains have
2^k distinct coordinates; ramified c=2 domains have 2^(k−1)+1. Actual factor-base
sizes M count only canonical x-coordinates lifting to P-256 points. Affine controls
use x=3t+β and the corresponding symmetric-coordinate transformation.

[derivations.md](derivations.md) gives the proofs, formulas, scope and accounting.
[diagram.svg](diagram.svg) is editable vector source; the Coordinator owns the
aggregate PDF rendering. This track changes no shared canonical graph.

## Checked observations

The complete finite-domain workload was fixed to ramified k=3,4,5, with one
generic k−1 coset and one affine coordinate control per size. A deterministic
bounded coset search and bounded β search matched the **actual** lifted M; every
search candidate is retained in the receipt. These chosen matches are correctness
fixtures, not a distributional sample.

| Actual M | Ramified S / domain N / states | Generic S / domain N / states | Affine generic states |
|---:|---:|---:|---:|
| 3 | 8 / 5 / 35 | 4 / 4 / 20 | 20 |
| 7 | 16 / 9 / 165 | 8 / 8 / 120 | 120 |
| 10 | 32 / 17 / 969 | 16 / 16 / 816 | 816 |

Here states means exactly C(N+2,3) symmetric coordinate triples before curve
lifting. All nine bundles supply their full domain, signed factor base, targets,
all accepted signed decomposition index triples, branch counts and solution
hashes. Each has three finite public target checks:

- A deliberately constructed positive, with one complete signed decomposition.
- A base-member target, with exactly M decompositions from inverse-pair
  cancellation; these certify exceptional-case handling and are not counted as
  independent useful relations.
- The published P-256 generator G as a fixed unrelated point, with a certified
  empty decomposition set in that finite domain.

All 27 sets match both a signed point pair join and an independently implemented
exhaustive signed-triple replay. The replay also verifies explicit full polynomial
factor identities for each domain's squarefree radical, and exact lifted-base
membership. This is separate code in the same session, **not independent review**.
No generation scalar is passed to the solvers. Positive fixtures certify
correctness; the empty G checks say nothing about uniform-target success rates.

Additional exact checks comprise three symbolic circuit identities, 40 numeric
circuit identities, 40 S4/resultant identities, the published generator order,
every retained base point's order, and seven torus/circuit witness depths
k=6,7,8,16,32,64,96. Complete generic domains at the first three depths have sizes
64,128,256 and actual M=29,58,119. The four higher depths have witnesses only,
without domain or relation-solution completeness claims.

## Forward algebraic formulation

The forward adapter expands three membership polynomials, adjoins S4, computes a
grevlex Groebner basis, then recursively obtains rational roots via lex elimination
and FLINT univariate roots. Source and input equations are retained, including
all finite symmetric solutions on completed joint cases.

| Fixed check | Quotient length | Distinct tested zero states | Outcome |
|---|---:|---:|---|
| Membership k=1 | 8 | 4 | Complete membership reference |
| Membership k=2 | 64 | 20 | Complete membership reference |
| Membership + S4 k=1 | 3 | 2 | All rational roots match inverse reference |
| Membership + S4 k=2 | 2 | 1 | All rational roots match inverse reference |
| Membership + S4 k=3 | unavailable | unavailable | 30-second process watchdog during basis construction |

These forward fixtures are subfibres of the fixed generic k=3 case; they are
identified by their exact c and target point in their files. They are distinct
from the matched-M fixture selection. All five attempts share a declared 2 GiB
address-space limit and are run sequentially. The stopped case is a resource
outcome for this SymPy adapter, not a certified empty set or a mathematical
obstruction. Groebner ideal-membership witnesses are not exported; completed
joint answers are checked against a separate exhaustive finite-domain reference.

A notable exact issue survives switching to an unramified scalar coset:
**the symmetric membership scheme is nonreduced at the triple-equal terminal**.
Its length is S³ but its distinct points number C(S+2,3), with local multiplicities
1,3,6 according to repetition type. The measured finite quotient lengths agree
with the derived formula. A solver using a squarefree-characteristic-polynomial
certificate on the unradicalized algebra cannot be applied without adaptation.

## Growth and operation counts

A shared Φ stage uses 3 squarings, 1 general multiplication, 8 written small-scalar
scalings and 11 additions/subtractions. An auxiliary-variable representation has
3k quadratic equations in 3(k+1) variables plus terminal equations and S4. No bound
on its elimination or solving degree has been established.

Expansion produces degree 2^k. Exact combined nonzero coefficient slots for the
three outputs at k=1…5 are 14,42,180,1008,6664. The corresponding per-output counts
and a dense total-degree cap are in [representation-01.json](representation-01.json).
The backward solver has at most eight raw inverse branches per state and stores
C(N+2,3) complete leaf states; actual square-root requests and raw branches at every
level appear in the case files. It avoids dense pair polynomials but enumerates
triples. These are algebraic representation counts, not timing comparisons or
lower bounds on every implicit algorithm.

## Commands, failures and limits

Run the following from `/workspace/crypto-autoresearcher`; use a fresh output
folder for a replay, retaining existing records unchanged:

```bash
PY=/workspace/dickson-solver/.venv/bin/python
TRACK=research/p256_factor_base_parallel_20261025/tracks/f1
$PY "$TRACK/f1.py" --out "$TRACK/replay-new"
$PY "$TRACK/verify.py" "$TRACK/checks-02"
$PY "$TRACK/representation.py"
```

[execution.json](execution.json) records exact original commands, environment,
source hashes and failure paths. `check_forward.py` contains the five exact
adapter commands and fixed watchdog; its output directory must be new.
[forward-01/receipt.json](forward-01/receipt.json) records every terminal outcome,
with native stdout/stderr per case. An initial implementation attempt incorrectly
chose the order-four torus element z(1)=i for high-depth generic checks, causing
c=2 and an assertion failure. Its source, console and nine already-written finite
bundles remain in `attempts/` and `checks-01/`; corrected `checks-02` is separate.

The complete-solution certificates cover only the declared finite domains on
actual P-256. No hidden base logarithms, relation rank, online success distribution,
linear algebra, final target attachment, or end-to-end costs were established.
No asymptotic bound for all implicit solvers follows from the inverse enumeration
or the bounded forward watchdog.

The precise remaining obligation is recorded in
[problem-implicit-global-solver.md](problem-implicit-global-solver.md): implement
and certify radical/local-algebra extraction on the unexpanded chain, avoiding
both complete domain-triple enumeration and per-base dense pair polynomials, then
give a justified total-cost model. The fixed k=1,2,3 public fixtures are immediate
controls for that follow-on work. Root indexing and archival are the Coordinator's
scope. Neither publication nor completion of this implementation pass changes
an official research status.
