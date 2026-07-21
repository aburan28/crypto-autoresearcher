# ECDLP Idea Generation — Report 11 (batch9)

Date: 2026-07-19
Role: Research Director, empirical cryptanalysis laboratory
Target: a non-generic prime-field-ECDLP algorithm whose **complete** single-target
cost beats Pollard-rho `~0.886*sqrt(n)`. Toy correctness, a new coordinate system,
a relation certificate, faster preprocessing, or a solver swap alone is **not** a
breakthrough.

Authorized scope: generated toy curves, public benchmark instances, synthetic data
only. No wallets, production keys, accounts, or unauthorized systems.

---

## 0. Required input review and machine-readable inventory

Read in full or by structured extraction:

1. `research_ledger.md` (2478 lines / 2.8 MB) — main ECFG ledger.
2. `ecdlp_index_calculus_state/research_ledger.md` (720 lines) — IC-state ledger.
3. `research/non_generic_transfer_search_20260610.md` (389 lines) — transfer program.
4. `ecdlp_index_calculus_state/research_sources/bibliography.json` (11 primary entries).
5. All **ten** prior idea-generation reports `idea_generation_2026071{7,8,9}[ _batchN].md`.

### Inventory (ID families and extracted mechanism axes)

- **Main ledger frontier**: `ECFG-P/NR/RT/MX/OBS-14xx` up to ~`1485`. The two open
  rho-crossing gates are the only live positive surface:
  - **ECFG-RT-1472** — 2-large-prime graph enrichment: needs `delta>1/4` at
    `L=q^{1/5}`; exact restricted-model exponent `max(2ell,1-ell,1+1/5-2ell)`,
    min `2/3` at `ell=1/3`; without enrichment an explicit deck loses to rho.
  - **ECFG-RT-1476** — five-term implicit membership backend: needs query
    `alpha<3/2` at `m=5` (`ell=1/(m+1-alpha)`; `m<=3` impossible, `m=4` needs
    `alpha<1`, `m=5` needs `alpha<3/2`); sparse-LA stage `q^{2/5}` is **not**
    binding. Serial-S3 forward-two-sum / backward-three-sum split is the object;
    strong prior `beta -> 3/2`.
  - Recent negatives: `NR-1474` (non-invariant CM orbit no compression),
    `NR-1475` (character-residual buckets no concentration), `NR-1477`
    (materialized serial-S3 no backend below `L^1.5`), `MX-1478` (`X^L-1` sparse
    factor gives log one-transition norm but dense on first composition),
    `NR-1479` (subgroup-x logs not in any `<=L^{1/2}` public linear feature space).
  - `ISO-*-IKD/ONK-0xx` oriented-ideal Kani transfer line: split plumbing and
    recovery-admissible toy fixtures, but no prime-field original-subgroup break;
    all `TOY/MODEL-BOUND`.
- **IC-state ledger frontier**: `P1509–P1513`. `P1509` local Hasse-jet source
  section (exact positive, no global compiler); `P1510[-R1]` global degree-2
  marked-resultant compiler (source-blind, `r^2` constant-size pair resultants);
  `P1511-R2` product-circuit gcd/subresultant/Hasse **semijoin closed** at input
  degree `r^3`; `P1512-R1` scalar-linear Chow/Tate/determinant-of-cohomology
  atomizer **closed** at `Omega(r^5)`, only the **nonlinear-circuit exception**
  preserved; `P1513` shared common-norm both-norms-cubic. `P1506–P1508` closed
  Plücker antisymmetrization, integer-lift small-root, Boolean quadratic-phase.
- **Transfer program** (`non_generic_transfer_search` + `PO-transfer-001..006`):
  same-field isogeny closed for order-based channels; scalar Weil/Kummer
  diagnostic-only; twist positive is an adjacent invalid-curve channel;
  `PO-002` target-coupling `178x–317x` rho; `PO-003` BNIT bielliptic native
  source `3375.96x` rho floor, toy `n^{1.687}`; `PO-004` Plücker gate closed;
  `PO-005/006` trace-quotient multiplicity proven non-gaining, `(3,3)`-cofiber
  hypergraph closed at rank `t=B`; next open = cyclic-cover `X_d:z^d=h(P)` with a
  **measured label-conditioned factorization advantage** (not credited preimages).
- **Bibliography**: Semaev 2004; Gaudry 2009; FPPR 2012; Shantz–Teske 2013;
  Faugère–Huot–Joux–Renault–Vitse 2014; Kousidis–Wiemers 2015; Karabina 2015;
  Amadori–Pintore–Sala 2017; McGuire–Mueller 2017; Trimoska–Ionica–Dequen 2020.
  All prime-field/binary Semaev-Gröbner-SAT or extension-field index calculus;
  none reaches sub-rho single-target on ordinary prime fields.

**Entries reviewed**: main-ledger ECFG rows through `~1485` plus the full
`ISO-*` Kani block; IC-state `P1072..P1513` frontier; six PO-transfer stages;
10 prior reports spanning ~60 distinct mechanism lanes. **ID families covered**:
`ECFG-{P,NR,RT,MX,OBS}`, `ISO-{NR,OBS,RT}-{IKD,ONK}`, `PO-transfer-00x`,
`IDEA-0xx`, `P15xx` (report-proposed, through `P1573`).

### Saturation finding (11th report)

The mechanism space is **saturated** at the level of "new attack primitive." Ten
reports have consumed, among ~60 lanes: subresultant/Toeplitz-Bézoutian, cycle-
matroid/homology, effective-resistance, power-sum resultant, Heisenberg/theta,
Weil-Châtelet, Berkovich skeleton, Holant/matchgate, nilsequence, orthogonal
lattice, sum-product energy, SOS-Lasserre, apolarity, Wormald 2-core, generalized
Jacobian, syzygy/Betti, sign-rank/γ2, growth/SL2, Pila-Wilkie, sandpile,
power-projection, matroid-union, descent-branching, Mahler, Fourier-Mukai, motivic
arc, **arboreal/iterated-monodromy**, Cohen-Lenstra, free-probability, Baur-
Strassen, HDX coboundary, **Lang-Weil count**, Cohn-Umans, Picard-Fuchs, graphon
cut-norm, DML, Ben-Or-Tiwari, **Adolphson-Sperber**, Guth-Katz, Ronkin, Guruswami-
Sudan, plethysm, ACFA, elliptic-net, Croot-Sisask, Valiant rigidity, Delsarte LP,
block-Hankel, formal-group/Coleman, **GKZ D-module**, cluster mutation, TDA, RKHS,
probabilistic-polynomial; and barriers OV/3SUM, τ-conjecture, asymptotic-spectrum,
Serre open-image, VC-dim, lifting, PC/IPS-**refutation** Nullstellensatz, NOF/BNS,
Shearer, approximate-degree, **slice-rank/Croot-Lev-Pach (rank-1 vacuous)**,
**Rudnev/BGKS point-plane incidence** (batch3).

Continuing the batch5–8 discipline: this report supplies **exact meters on the two
live gates** and **structurally-new barriers**, each importing a lower-bound or
measurement technology **no prior report used**, and each barrier threshold chosen
so that reaching it **closes a live gate** (`delta<=1/4` kills RT-1472;
`alpha>=3/2` kills RT-1476). No new "attack primitive" is claimed to exist; the
value is in tightening or closing the two conditional theorems.

### Fingerprint discipline

For each candidate C, `F(C) = (algebraic object, public operations, hidden
structure, info discarded, info retained, relation primitive, compression
primitive, rank mechanism, descent mechanism, dominant cost exponent)`. C is a
duplicate if any ledger/report entry matches the essential fingerprint even under
renaming. Explicitly checked and **rejected as duplicates before writing**:
Rudnev point-plane incidence (batch3 supply barrier), constructive Croot-Lev-Pach
(= batch4 `SLICE-RANK-1-D2`, rank-1 vacuous in cyclic `E(F_p)`), PC/IPS
*refutation* Nullstellensatz (batch7 `POLYCALC-D2`), arboreal/iterated monodromy
(batch5/6). The surviving twelve use technologies absent from all eleven sources.

---

## Group A — conservative extensions

## Candidate: NULLSTELLENSATZ-CERT-A1

### One-sentence mechanism
Exploit the **effective arithmetic Nullstellensatz** (Kollár / D'Andrea–Krick–
Sombra degree-and-height bounds) to obtain an *exact lower bound on the query
exponent* `alpha` of any five-term membership backend, by measuring the minimal
degree of a **feasibility certificate** `1 = sum g_i f_i` (equivalently the
membership representation of the target coordinate) on the true P1510/P1511 source
ideal — the algebra any backend must implicitly evaluate.

### Status
HYPOTHESIS (exact meter on RT-1476).

### Novelty classification
POSSIBLY NOVEL (documented search: the ECDLP index-calculus literature — Miller,
Silverman–Suzuki, Gaudry, Diem, McGuire–Mueller — bounds Gröbner/first-fall degree,
never the arithmetic-Nullstellensatz *feasibility*-certificate degree×height).

### Semantic fingerprint
- algebraic object: the P1510 source-marked ideal `I = <f_1,...,f_r>` whose
  feasibility for a public target encodes a valid five-term decomposition;
- public operations: ideal membership, Gröbner-free certificate construction,
  degree/height accounting;
- hidden structure exploited: the *representation complexity* (Bézout-type
  degree×height) of expressing the target inside `I`, not its refutation degree;
- info discarded: the specific witness tuple (only certificate size retained);
- info retained: minimal `(deg, height)` of the certificate over the successful-
  membership subset;
- relation primitive: certificate coefficient polynomials `g_i`;
- compression primitive: none — this is a *meter*, output is the exponent;
- rank mechanism: n/a (bounds the pre-LA generation stage);
- descent mechanism: same certificate reused for individual-log descent (stage 7);
- dominant cost exponent: `alpha_cert = log_L(deg×height of minimal certificate)`.

### Nearest ledger entries
1. `POLYCALC-D2` (batch7) — PC/IPS Nullstellensatz **refutation** degree of an
   *infeasible* non-membership system. **Distinction**: refutation degree lower-
   bounds proving a non-instance has *no* decomposition; A1 bounds the *feasibility*
   certificate degree of a *true* membership — the object the backend actually
   computes. Different theorem (Kollár effective NSS vs Razborov PC lower bound),
   different sign of the statement.
2. `ECFG-P1510-R1` — the degree-2 marked-resultant compiler. **Distinction**: P1510
   *builds* the source-blind object; A1 *lower-bounds the intrinsic degree×height*
   any such object must carry to certify membership, independent of the compiler.
3. `ECFG-P1512-R1` — scalar-linear Chow atomizer closed at `Omega(r^5)`.
   **Distinction**: that is a *linear-algebraic* corank bound on an incidence
   matrix; A1 is a *polynomial-certificate* degree×height bound (nonlinear circuit,
   the preserved exception).
4. `RT-1476-SUBRES-A1` (batch2) — subresultant eliminant-degree `beta` meter.
   **Distinction**: eliminant degree measures the *elimination-ideal* generator; the
   arithmetic-NSS certificate measures the *membership representation* including the
   integer height, a strictly finer Bézout-height object.
5. `ADOLPHSPERBER-A2` (batch7) — p-adic Newton-polygon valuation meter.
   **Distinction**: valuation of the *zeta/point-count* side, not the certificate
   representation degree×height.

### Nearest literature
- Kollár, "Sharp effective Nullstellensatz" (J. AMS 1988): certificate degree
  `<= d^n` for `n` polynomials of degree `d`. — worst-case; the gap is the *typical*
  degree on the structured elliptic source ideal.
- D'Andrea, Krick, Sombra, "Heights of varieties in multiprojective spaces and
  arithmetic Nullstellensätze" (Ann. ENS 2013): joint degree×**height** bounds. —
  needed because over `F_p` the height collapses but the multiprojective degree is
  the operative cost; gap: no application to Semaev source ideals.
- McGuire–Mueller 2017 (bibliography): Gröbner-free summation-poly evaluation with
  complexity worse than rho. — establishes the baseline the certificate meter would
  have to undercut. Gap: no certificate-degree analysis.

### Target family
Ordinary prime-field curves `E/F_p`, prime target-subgroup order `n`, `gcd(p,n)=1`,
`j not in {0,1728}`, non-anomalous, non-supersingular, embedding degree `>1`.
Excluded: CM `j=0/1728` (special source symmetry), anomalous `n=p`, supersingular.

### Full algorithmic path
1. factor base: canonical `L=q^{1/5}` subgroup-x deck as in P1473/P1477.
2. relation generation: for a successful membership, build the certificate
   `x_target - sum = sum_i g_i f_i` fraction-free on the P1510 source ideal.
3. witness extraction & verification: re-substitute `g_i` and check the identity
   exactly; a certificate is valid iff the polynomial identity holds over `Z`
   (then reduced mod `p`).
4. relation probability: unchanged from RT-1476 support `min(1,L^m/q)`.
5. matrix dims/density/rank: the certificate is pre-LA; LA stage stays `L^2`.
6. factor-log calibration: certificate degree maps to query cost `L^{alpha_cert}`.
7. individual-log / descent: same certificate at descent nodes.
8. offline/online: certificate *template* offline; per-target coefficients online.
9. memory/parallelism: certificate coefficient storage `O(deg^n)` worst; measured.

### Cost model
Query per membership `= L^{alpha_cert}` where `alpha_cert = log_L(D·H)`, `D` the
measured multiprojective certificate degree, `H` its height (mod-`p` = 0 but the
`F_p`-arithmetic count tracks `D`). Setup `L^2`. Total `2/(m+1-alpha_cert)`. Compare
rho `1/2`, BSGS `1/2`, nearest IC baseline (McGuire–Mueller > `1/2`). Promotion iff
measured `alpha_cert < 3/2` with a downward trend across `m=5` toy sizes.

### Why the existing negative results do not already kill it
`P1512-R1` closed only the *linear* atomizer (`Omega(r^5)`); the arithmetic-NSS
certificate lives in the *nonlinear-circuit exception* explicitly preserved there.
The new operation is measuring degree×height of a **feasibility** representation,
which no refutation/eliminant/valuation meter (`POLYCALC`, `SUBRES`, `ADOLPHSPERBER`)
computes.

### Likely fatal obstruction
Kollár's bound is `d^n`; on `m=5` the generic certificate degree is almost certainly
`Theta(r^{c})` with `c>=2`, giving `alpha_cert >= 2 > 3/2` — i.e. the meter most
likely *re-derives the rho barrier* and upgrades to a matching lower bound. That is
the high-EV outcome (closes RT-1476), not a crossing.

### Minimal falsifying experiment
Toy `p in {1009,4099,16411}` (three sizes), `m in {3,4,5}`, seeds `20260719..23`,
ordinary prime-order controls; **positive control**: a hand-built ideal with a known
low-degree membership certificate (must report `alpha_cert < 3/2`); **negative
control**: a random dense ideal of the same shape (must report `alpha_cert >= 2`).

### Quantitative promotion gate
Measured `alpha_cert` on the successful-membership subset shows a fitted trend
`alpha_cert(m=5) < 3/2` across the three sizes with `R^2 > 0.9`. Correctness of the
certificate is *not* the gate; the exponent trend is.

### Proof track
Theorem: the multiprojective certificate degree of target-membership in the P1510
source ideal is `Theta(r^{3/2})` (would give `alpha_cert = 3/2`, the exact RT-1476
boundary), or `Omega(r^2)` (closes the gate).

### Disproof track
Exhibit one ordinary prime-order family where the measured certificate degree is
`o(r^{3/2})` — would reopen a sub-rho route; strong prior says impossible.

### Reproduction artifact
- contract: `research/exp_nullstellensatz_cert_alpha_meter.md`
- implementation: `experiments/ecdlp_prime_field/nss_cert_alpha_meter.sage`
- result: `experiments/ecdlp_prime_field/nss_cert_alpha_meter_result.json`
- audit: `experiments/ecdlp_prime_field/nss_cert_alpha_meter_verify.sage`
- ledger ID: `ECFG-P1574`

---

## Candidate: AX-KATZ-SUPPLY-A2

### One-sentence mechanism
Exploit the **Ax–Katz theorem** (exact `p`-adic divisibility of the number of
`F_p`-solutions of a polynomial system) as a *supply/parity meter*: the count of
valid five-term decompositions of a target is forced into a residue class mod a
power of `p`, giving an exact congruence floor on achievable relation supply.

### Status
HYPOTHESIS (exact p-adic count meter, feeds RT-1472 and RT-1476 supply).

### Novelty classification
POSSIBLY NOVEL (Ax–Katz absent from all eleven sources; the ledger's count meters
are archimedean Lang-Weil (batch6) and Newton-polygon Adolphson–Sperber (batch7),
never the exact `q`-divisibility statement).

### Semantic fingerprint
- algebraic object: solution set of the Semaev/source membership system as a variety
  over `F_p`;
- public operations: degree accounting, Ax–Katz exponent `ceil((n - sum d_i)/max d_i)`;
- hidden structure: forced `p`-adic valuation of `#solutions`;
- info discarded: solution identities;
- info retained: `v_p(#decompositions)` congruence class;
- relation primitive: none (meter);
- compression primitive: none;
- rank mechanism: constrains honest-graph edge multiplicity parity for RT-1472;
- descent mechanism: bounds branch counts mod `p` at descent nodes;
- dominant cost exponent: not a cost — a *feasibility congruence* on `delta`.

### Nearest ledger entries
1. `LANGWEIL-METER-A3` (batch6) — archimedean Deligne/Lang-Weil count.
   **Distinction**: Lang-Weil gives `#=q^{dim}+O(q^{dim-1/2})` (size); Ax–Katz gives
   an *exact divisibility* `p^{mu} | #` (congruence). Different theorem, orthogonal
   information (magnitude vs valuation).
2. `ADOLPHSPERBER-A2` (batch7) — Newton-polygon of the L-function.
   **Distinction**: Adolphson–Sperber bounds the *lowest-slope Frobenius eigenvalue
   valuation*; Ax–Katz bounds `v_p(#points)` directly via degrees only — coarser,
   exact, and degree-only (no polytope).
3. `RT-1472-CYCLEMAT-A2` (batch2) — cycle-matroid enrichment `delta`.
   **Distinction**: matroid rank is combinatorial; Ax–Katz is a number-theoretic
   congruence on the same edge-count supply.
4. `SHEARER-D3` (batch8) — submodular entropy supply ceiling.
   **Distinction**: entropy is an upper bound on log-count; Ax–Katz is an exact
   modular constraint, not an inequality.
5. `ENERGY-D1` (batch3) — additive-energy relation-supply ceiling.
   **Distinction**: energy bounds second-moment collisions; Ax–Katz bounds the
   count's `p`-valuation.

### Nearest literature
- Ax (1964), Katz (1971): `p^{ceil((n-sum d_i)/D)} | #V(F_p)`. — exact; gap: never
  applied to decomposition-count supply for index calculus.
- Adolphson–Sperber (1987, 1989): refined Newton-polygon divisibility. — the sharper
  cousin; A2 uses only the elementary degree bound as a fast pre-filter meter.

### Target family
Same as A1. Excluded: `p` small enough that `v_p` saturates trivially.

### Full algorithmic path
1. factor base: canonical `L=q^{1/5}` deck. 2. relation generation: enumerate the
system's degrees `d_i` and ambient dimension `n`. 3. witness/verify: compute
`#decompositions` exactly on toy fixtures and check the Ax–Katz congruence holds.
4. probability: `#/q^{n-#eqs}`. 5. matrix: constrains honest edge multiplicity
parity (RT-1472). 6. calibration: n/a. 7. descent: branch-count congruence.
8. offline/online: degrees offline; per-target count online. 9. memory: negligible.

### Cost model
This is a **feasibility meter**, not a cost: it outputs whether any `delta>1/4`
enrichment is *congruence-consistent*. If Ax–Katz forces `#decompositions ≡ 0 mod
p^{mu}` with `mu` large relative to `L`, the honest graph cannot carry the extra
independent cycles enrichment needs, giving `delta<=1/4`.

### Why the existing negative results do not already kill it
No prior supply meter (Lang-Weil size, Adolphson–Sperber slope, Shearer entropy,
matroid rank, VC, Delsarte) is a `p`-adic congruence; the new operation is the exact
`v_p(#)` floor.

### Likely fatal obstruction
For `m=5` and typical degrees the Ax–Katz exponent `mu = ceil((n - sum d_i)/D)` may
be `<=0` (vacuous divisibility), giving no constraint. Likely partly vacuous —
pairs with `AX-KATZ-BARRIER-D3` to test the non-vacuous regime.

### Minimal falsifying experiment
Toy `p in {1009,4099,16411}`, `m in {4,5}`, seeds `20260719..23`; positive control:
a system with a designed high `mu` (must show forced divisibility); negative control:
random system (`mu<=0`, no constraint). Compare measured `v_p(#)` to Ax–Katz floor.

### Quantitative promotion gate
Ax–Katz floor `mu` is non-vacuous (`mu>=1`) AND forces `#decompositions` too small
to support `delta>1/4` on all three sizes — i.e. an exact `delta<=1/4` congruence
certificate. Otherwise INCONCLUSIVE (not a crossing either way).

### Proof track
Theorem: for `m=5` ordinary source systems, `v_p(#decompositions) >= 1`, capping
enrichment supply at `delta<=1/4`.

### Disproof track
A family with `mu<=0` for all relevant subsystems → meter vacuous, no constraint.

### Reproduction artifact
- contract: `research/exp_axkatz_supply_meter.md`
- implementation: `experiments/ecdlp_prime_field/axkatz_supply_meter.sage`
- result JSON + audit; ledger ID `ECFG-P1575`.

---

## Candidate: CONTAINER-CEILING-A3

### One-sentence mechanism
Exploit the **hypergraph container method** to prove that the honest two-large-prime
summation graph's edge set is confined to a small family of "containers," bounding
the number of achievable enriched cycle configurations and hence `delta`.

### Status
HYPOTHESIS (δ-ceiling meter for RT-1472).

### Novelty classification
NOVELTY-UNVERIFIED (container method absent from all reports; nearest is VC-dimension
Sauer–Shelah (batch7) and matroid-union (batch5), both different counting principles).

### Semantic fingerprint
- object: the 3-uniform (pair,pair,row) incidence hypergraph of the 2-LP deck;
- public ops: container-lemma packing, independent-set counting;
- hidden structure: sparse-container confinement of relation-carrying subgraphs;
- discarded: exact edge labels;
- retained: log-count of admissible enriched configurations;
- relation primitive: cycle in the container;
- compression primitive: none;
- rank mechanism: cycle-space dimension inside a container;
- descent mechanism: n/a;
- dominant exponent: `delta_ceiling = log_L(#containers)/log_L(L^2)`.

### Nearest ledger entries
`VCDIM-D3` (batch7, shatter bound), `MATUNION-A2` (batch5, matroid union),
`CORRELATED-PEEL-A3` (batch4, 2-core threshold), `RT-1472-CYCLEMAT-A2`,
`SHEARER-D3`. **Distinction**: containers bound the *number of near-independent
configurations avoiding a dense cycle*, a different counting theorem from
shattering, matroid rank, DE-method thresholds, or entropy — it directly caps how
many distinct `delta>1/4` enrichments can even exist.

### Nearest literature
- Balogh–Morris–Samotij (2015); Saxton–Thomason (2015): hypergraph container
  theorems. Gap: never applied to index-calculus relation graphs.

### Target family
Same as A1/A2; honest hash-like 2-LP deck at `L=q^{1/5}`.

### Full algorithmic path
1. deck as A1. 2. build the incidence hypergraph. 3. apply container lemma; count
containers. 4. probability inherited. 5. cycle-space rank inside a container.
6. n/a. 7. n/a. 8. offline container census; online cycle search. 9. memory
`#containers`. INCOMPLETE-risk on stage 7 (descent) — flagged; this is a supply
meter, descent is not its subject.

### Cost model
Meter: outputs `delta_ceiling`. If `#admissible containers = L^{o(1)}·L^{1/2}`,
then `delta<=1/4`.

### Why negatives don't kill it
Distinct counting principle from all prior supply barriers.

### Likely fatal obstruction
Container bounds are often loose (they over-count); the ceiling may land above `1/4`
and be inconclusive.

### Minimal falsifying experiment
Toy `p` three sizes, honest vs planted-enriched decks, seeds `20260719..23`;
positive control: designed dense-cycle deck (containers should be many); negative
control: Sidon-like deck (few containers, `delta<=1/4`).

### Quantitative promotion gate
`delta_ceiling <= 1/4` on all three sizes with monotone trend.

### Proof track / Disproof track
Theorem: honest 2-LP hypergraph has `L^{1/2+o(1)}` containers ⇒ `delta<=1/4`.
Disproof: a family with super-polynomially many containers.

### Reproduction artifact
`research/exp_container_delta_ceiling.md`,
`experiments/ecdlp_prime_field/container_delta_ceiling.sage`, result+audit,
ledger `ECFG-P1576`.

---

## Group B — genuine representation changes

## Candidate: MATCHING-VECTOR-B1

### One-sentence mechanism
Represent the five-term sum-zero membership predicate as a **matching-vector (MV)
code** decoding (Grolmusz-style low-degree representation of an OR/equality over a
composite modulus), aiming for a backend whose query degree is the MV code's
super-low degree rather than the eliminant degree.

### Status
HEURISTIC (representation change; likely self-killing).

### Novelty classification
POSSIBLY NOVEL (matching-vector codes / Grolmusz representations absent from all
reports; RKHS/kernel (batch8) and list-decoding (batch7) are the nearest coding-
flavored entries, both different).

### Semantic fingerprint
- object: the `m=5` sum-zero indicator on the subgroup-x deck;
- public ops: MV set-system construction, low-degree polynomial evaluation;
- hidden structure: composite-modulus MV representation collapsing the indicator
  degree;
- discarded: exact witness identity;
- retained: MV codeword coordinates;
- relation primitive: MV-decoded membership hit;
- compression primitive: MV low-degree representation;
- rank mechanism: MV code rank;
- descent mechanism: MV decode at descent nodes;
- dominant exponent: `alpha_MV = log_L(MV degree)`.

### Nearest ledger entries
`RKHS-KERNEL-C2` (batch8, killed by Peter-Weyl rank `Theta(n)`), `LISTDECODE-B2`
(batch7, decoding-radius kill), `PROBABILISTIC-POLY-C3` (batch8), `DELSARTE-LP-A2`
(batch8), `SIGNRANK-GAMMA2-B3` (batch4). **Distinction**: MV codes get *sub-linear*
degree only over **composite** moduli (Grolmusz); the group order `n` here is
**prime**, so the composite-modulus mechanism is structurally unavailable — the
distinction is precisely why this is a near-certain kill and worth stating.

### Nearest literature
- Grolmusz (2000): superpolynomial-size set systems / low-degree OR mod composite.
- Efremenko (2009); Dvir–Gopalan–Yekhanin: MV codes for LDCs. Gap: prime modulus
  destroys the construction — no prime-field MV backend exists.

### Target family
Ordinary prime-field, **prime** subgroup order `n` (the fatal condition is built in).

### Full algorithmic path
1. deck. 2. attempt MV representation of the 5-sum indicator. 3. verify degree.
4–9 as RT-1476. The path is complete but stage 2 is expected to fail for prime `n`.

### Cost model
`alpha_MV`; expected `>= 3/2` because prime modulus forbids the sub-linear MV degree.

### Why negatives don't kill it
It is a *new representation*; its kill is a *new* obstruction (prime-modulus MV
non-existence), not a prior one.

### Likely fatal obstruction
Prime `n` ⇒ no composite-modulus MV gain ⇒ `alpha_MV >= 3/2`.

### Minimal falsifying experiment
Toy `p`, prime vs (control) smooth-composite-order curves, seeds `20260719..23`;
positive control: composite-order deck (MV degree should drop); negative control:
prime-order deck (no drop). Three sizes.

### Quantitative promotion gate
`alpha_MV < 3/2` on prime-order decks (near-certainly fails → scoped negative that
*names* why the coding lane cannot help prime-order ECDLP).

### Proof track / Disproof track
Theorem: any MV representation of the prime-order 5-sum indicator has degree
`Omega(L^{3/2})`. Disproof: a prime-modulus MV construction (would be independently
notable).

### Reproduction artifact
`research/exp_matching_vector_backend.md`,
`experiments/ecdlp_prime_field/mv_backend.sage`, result+audit, `ECFG-P1577`.

---

## Candidate: ELEKES-SZABO-B2

### One-sentence mechanism
Treat the symmetrized Semaev relation as the vanishing hypersurface `F=0` of an
**Elekes–Szabó** problem and measure whether its group-law "special form" forces
relation supply to *concentrate* (exploitable, `delta>1/4`) or to *expand*
(`o(L^2)` hits per row, `delta<=1/4`) — an exact structural δ-meter tied to the one
feature that distinguishes Semaev from a generic polynomial: it encodes the group
law.

### Status
HYPOTHESIS (structural δ-meter on RT-1472; representation winner).

### Novelty classification
POSSIBLY NOVEL / LITERATURE-ADJACENT (Elekes–Szabó/Elekes–Rónyai have been extended
to elliptic-curve sum-product and AP-in-coordinates, but never to Semaev-
decomposition relation supply). See external check below.

### Semantic fingerprint
- object: the symmetrized Semaev variety as an `F=0` Elekes–Szabó configuration;
- public ops: incidence counting on Cartesian products, special-form test;
- hidden structure: **the group-law special form** — Semaev's `F` is exactly the
  Elekes–Szabó exceptional (algebraic-group) case;
- discarded: witness tuples;
- retained: fiber-concentration exponent;
- relation primitive: a Cartesian-grid incidence;
- compression primitive: none;
- rank mechanism: whether concentrated fibers yield reusable rows;
- descent mechanism: n/a;
- dominant exponent: `delta_ES = ` measured excess concentration over the generic
  `O(N^{8/3})` (4-var) / arity-`m` Elekes–Szabó bound.

### Nearest ledger entries
`ENERGY-D1` (batch3, additive energy), `RUDNEV`-barrier (batch3, point-plane
incidence), `GRAPHON-CUTNORM-B3` (batch6), `CORRELATED-PEEL-A3` (batch4),
`RT-1472-CYCLEMAT-A2`. **Distinction**: energy/incidence give *unconditional* upper
bounds treating `F` as generic; Elekes–Szabó is the **dichotomy theorem** that
isolates exactly the group-law special case — it *measures the value of the group
structure* rather than discarding it, which is the crux of whether RT-1472's
enrichment can beat a random graph.

### Nearest literature (external check performed)
- Elekes–Szabó (2012); Raz–Sharir–de Zeeuw; Bays–Breuillard "Projective geometries
  arising from Elekes–Szabó problems" (arXiv 1806.03422) — the special case is an
  algebraic subgroup with a skew-field-of-endomorphisms structure (exactly the
  elliptic setting). Elekes–Szabó in 4 dimensions (arXiv 1607.03600). EC sum-product
  / Bremner conjecture (arXiv 2603.06483). **Gap**: all bound sum-product / AP
  counts on curves; none computes the *decomposition-relation supply exponent*
  `delta` for index calculus. So the *object* is adjacent but the *measurement* is
  new.

### Target family
Ordinary prime-field, prime order, `j not in {0,1728}`. Excluded: CM curves whose
extra endomorphisms change the special-form class.

### Full algorithmic path
1. deck. 2. relation generation via Cartesian-grid incidence on `F=0`. 3. verify
each incidence is a valid EC-addition tuple. 4. probability = measured
concentration. 5. rank from concentrated rows. 6. n/a. 7. n/a. 8. grid offline,
target online. 9. memory `L^2`.

### Cost model
`delta_ES` = measured excess of hits per row over the Elekes–Szabó generic ceiling.
If the group-law special form gives concentration `delta_ES>1/4`, RT-1472 could
cross; strong prior is that the concentration is *exactly balanced* by the added
advice cost (batch1 `RT-1472` exponent `2/3`), giving `delta<=1/4`.

### Why negatives don't kill it
No prior meter measures the *dichotomy value of the group law*; energy/incidence
throw it away.

### Likely fatal obstruction
Elekes–Szabó's special case does give concentration, but the concentration is on a
*coset-progression* whose advice cost is `Theta(L^2)` — self-canceling, reproducing
the `RT-1472` exponent `2/3`. Most likely `delta<=1/4`.

### Minimal falsifying experiment
Toy `p in {1009,4099,16411}`, seeds `20260719..23`; positive control: a genuinely
special-form (planted subgroup) grid (must show concentration); negative control:
a random degree-matched non-special `F` (must show generic `O(N^{8/3})` spread).
Measure hits-per-row vs `N`.

### Quantitative promotion gate
`delta_ES > 1/4` net of advice cost on all three sizes with upward trend — else a
scoped `delta<=1/4` closing RT-1472's structural hope.

### Proof track
Theorem: for the symmetrized Semaev `F`, the Elekes–Szabó concentration is exactly
offset by `Theta(L^2)` coset advice, yielding `delta<=1/4`.

### Disproof track
A prime-order family where net concentration exceeds `1/4` — would reopen RT-1472.

### Reproduction artifact
`research/exp_elekes_szabo_delta_meter.md`,
`experiments/ecdlp_prime_field/elekes_szabo_delta_meter.sage`, result+audit,
ledger `ECFG-P1578`.

---

## Candidate: NEWTON-OKOUNKOV-B3

### One-sentence mechanism
Represent the individual-log **descent** as evaluation in a **Newton–Okounkov graded
algebra** of the membership linear system, using the body's *slices* (not just its
volume) as a per-degree descent-supply meter for stage 7.

### Status
HEURISTIC (thin — flagged).

### Novelty classification
NOVELTY-UNVERIFIED (Newton–Okounkov bodies absent from reports; GKZ D-module
(batch8) used the *top* normalized volume, DESCENT-EXP (batch5) counted branching).

### Semantic fingerprint
object: valuation semigroup of the membership system; public ops: Okounkov-body
construction, slice-volume; hidden structure: graded filtration of descent degrees;
discarded: exact nodes; retained: per-degree supply profile; relation primitive:
graded generator; compression primitive: graded truncation; rank mechanism: graded
piece dimension; descent mechanism: **the subject** — slice at descent depth;
dominant exponent: `log_L` of the largest slice.

### Nearest ledger entries
`GKZ-DMODULE-B2` (batch8, holonomic rank = top volume), `DESCENT-EXP-A3` (batch5,
branching count), `MOTIVIC-B3` (batch5, arc measure), `ADOLPHSPERBER-A2`,
`SUBRES-A1`. **Distinction**: GKZ uses only the *top* mixed volume (branch count);
Newton–Okounkov exposes the *entire graded filtration* — the per-degree slices give
the descent-cost profile GKZ and DESCENT-EXP collapse to a single number.
**Honest flag**: this is thin — the slice profile may add nothing beyond DESCENT-EXP
if the filtration is linear.

### Nearest literature
Okounkov (1996); Lazarsfeld–Mustață; Kaveh–Khovanskii (2012). Gap: no ECDLP descent
application.

### Target family / path / cost
Same family as B2. Path stages 1–9 as RT-1476 with stage 7 = slice evaluation.
Cost: descent exponent from the largest slice; promotion iff descent stage drops
below the RT-1476 `q^{1/5}` descent budget while keeping generation `<3/2`.

### Why negatives don't kill it / obstruction / experiment / gate
New graded object; likely obstruction = filtration is linear ⇒ reproduces
DESCENT-EXP. Experiment: three toy sizes, positive control = graded system with
non-linear slices, negative control = linear filtration. Gate: measured descent
exponent `< 1/5` with slice non-linearity, else INCONCLUSIVE.

### Proof/Disproof track
Theorem: the membership Okounkov body has non-linear slices lowering descent below
`q^{1/5}`. Disproof: linear filtration.

### Reproduction artifact
`research/exp_newton_okounkov_descent.md`,
`experiments/ecdlp_prime_field/newton_okounkov_descent.sage`, result+audit,
`ECFG-P1579`.

---

## Group C — high-risk speculative mechanisms

## Candidate: METHOD-OF-MULTIPLICITIES-C1

### One-sentence mechanism
Build a membership backend from the **method of multiplicities** (Dvir–Kopparty–
Saraf–Sudan): impose *high-order Hasse-derivative* vanishing of the membership
variety at few evaluation points instead of simple vanishing at many points, trading
point-count for multiplicity to lower the query exponent `alpha`.

### Status
HYPOTHESIS (high-risk backend; high-risk winner).

### Novelty classification
POSSIBLY NOVEL (documented search: method of multiplicities applied to finite-field
subsets and small-char DLP presentations, but never as a Semaev membership backend).
This is the one **new operation on the never-fully-consumed jet seed**: batch4's
`JET-B1`/P1509 used *first-order* Hasse sections; multiplicity-boosting is the
untried degree-vs-multiplicity trade.

### Semantic fingerprint
- object: the 5-term membership variety with a Hasse-jet scheme structure;
- public ops: high-multiplicity interpolation, multiplicity-Schwartz–Zippel;
- hidden structure: jet-thickened incidence lowering interpolation degree;
- discarded: redundant evaluation points;
- retained: multiplicity-weighted constraints;
- relation primitive: multiplicity-vanishing hit;
- compression primitive: multiplicity in place of point-count;
- rank mechanism: multiplicity-weighted constraint matrix rank;
- descent mechanism: same multiplicity backend at descent;
- dominant exponent: `alpha_mult = log_L(deg / multiplicity-gain)`.

### Nearest ledger entries
`ECFG-P1509` (Hasse-jet local section, first-order), `JET-B1` (batch4),
`POWERPROJ-A1` (batch5, transposed evaluation), `BENORTIWARI-A1` (batch7, sparse
interpolation), `PROBABILISTIC-POLY-C3` (batch8). **Distinction**: P1509/JET-B1 use
multiplicity **one**; the method of multiplicities uses multiplicity `>1` with the
DKSS multiplicity-Schwartz–Zippel lemma to *reduce degree* — a genuinely different
interpolation regime and the untried arm of the jet seed.

### Nearest literature (external check performed)
- Dvir–Kopparty–Saraf–Sudan (2013) "Extensions to the method of multiplicities";
  Guo–Kopparty–Sudan (multiplicity codes). — establish the degree/multiplicity
  trade. **Gap**: over `F_p` multiplicity is capped at `< p`, and small-char DLP
  work (arXiv 2206.10327) uses EC *presentations*, not a multiplicity membership
  backend. No prime-field Semaev application.

### Target family
Ordinary prime-field, prime order, `p` large enough that multiplicity `s ~ L^{eps}`
is available (`s < p`). Excluded: small `p` where multiplicity saturates.

### Full algorithmic path
1. deck. 2. relation generation via `s`-fold Hasse-derivative vanishing at
`L^{alpha_mult}` points. 3. verify multiplicity constraints exactly (recompute Hasse
derivatives). 4. probability via multiplicity-SZ. 5. constraint matrix rank
(multiplicity-weighted), LA `L^2`. 6. calibration to `alpha_mult`. 7. descent with
the same backend. 8. offline jet templates, online target derivatives. 9. memory
`s·L`.

### Cost model
`alpha_mult = log_L( eliminant_degree / s )` with `s <= p-1`. Over `F_p` the gain is
`log_L(s)` which is `O(1)` unless `s` grows with `L` — the make-or-break question.
If `s = L^{eps}` is usable, `alpha_mult = 3/2 - eps` could cross; if `s = O(1)`,
`alpha_mult = 3/2` (no gain). Total `2/(m+1-alpha_mult)`; compare rho `1/2`.

### Why the existing negative results do not already kill it
P1509 and the batch4 jet closeout used multiplicity one; multiplicity `>1` is the
explicitly-untried operation. The strong-prior `beta->3/2` was measured at
multiplicity one.

### Likely fatal obstruction
Over `F_p` the usable multiplicity is `s < p` but the *gain* is only `log_L(s)`; to
reach `alpha < 3/2` you need `s = L^{Omega(1)}`, and the interpolation cost scales
with `s^n`, so the memory/verification cost eats the degree gain — most likely a
constant-factor win only (scoped negative on the jet lane's last arm).

### Minimal falsifying experiment
Toy `p in {4099,16411,65537}` (need larger `p` for multiplicity room), `m=5`,
`s in {1,2,4,8}`, seeds `20260719..23`; positive control: a designed
multiplicity-friendly system (`alpha_mult` should drop with `s`); negative control:
a system where multiplicity gives no degree reduction. Fit `alpha_mult` vs `s` and
vs `L`.

### Quantitative promotion gate
`alpha_mult` fitted trend `< 3/2` at `s = L^{eps}` for some `eps>0`, net of the
`s^n` interpolation cost, across three sizes. Correctness at multiplicity `>1` is not
the gate; the *net* exponent is.

### Proof track
Theorem: for `m=5` there exists `s=L^{eps}` with multiplicity-weighted eliminant
degree `L^{3/2-eps}` and total cost still `< L^{3/2}` — would cross RT-1476.

### Disproof track
Show the `s^n` interpolation/verification cost dominates any degree gain for all
`s>1` (closes the jet lane's last arm).

### Reproduction artifact
`research/exp_method_multiplicities_backend.md`,
`experiments/ecdlp_prime_field/multiplicity_backend.sage`, result+audit,
ledger `ECFG-P1580`.

---

## Candidate: PFR-DICHOTOMY-C2

### One-sentence mechanism
Apply the (now-proven) **polynomial Freiman–Ruzsa** theorem to the two-large-prime
set: small doubling ⇒ the set sits in a bounded-size coset progression exploitable
by a BSGS-in-progression enrichment (`delta>1/4`); the honest hash-like set has
maximal doubling ⇒ no progression ⇒ `delta<=1/4`.

### Status
HEURISTIC (high-risk structural attack; near-certain kill).

### Novelty classification
POSSIBLY NOVEL (PFR / Freiman structure absent from all reports; ENERGY-D1 used
additive energy but not the structural dichotomy).

### Semantic fingerprint
object: the large-prime residue set as an additive set; public ops: doubling
constant, coset-progression cover; hidden structure: small-doubling ⇒ progression;
discarded: labels; retained: progression dimension/size; relation primitive:
progression-aligned pair; compression primitive: progression coordinates; rank
mechanism: progression cycle space; descent mechanism: n/a; dominant exponent:
`delta_PFR` from progression size.

### Nearest ledger entries
`ENERGY-D1` (batch3), `NILSEQ-C2` (batch3, higher-order Fourier), `MATUNION-A2`
(batch5), `RT-1472-CYCLEMAT-A2`, `CROOTSISASK-C3` (batch7). **Distinction**: PFR is
the *structure theorem* (small doubling ⇒ coset progression), not an energy bound or
almost-periodicity smoothing — it tests whether the large-prime set has *any*
exploitable additive structure at all.

### Nearest literature
Gowers–Green–Manners–Tao (2023, PFR proof); Sanders (Bogolyubov–Ruzsa). Gap: no
index-calculus application.

### Target family
Ordinary prime-field, prime order; honest hash-derived large-prime set.

### Full algorithmic path
1. deck + large-prime set. 2. measure doubling `|A+A|/|A|`. 3. if small, cover by
coset progression and generate progression-aligned relations; verify. 4–5 progression
cycle rank. 6 n/a. 7 n/a. 8 offline doubling census. 9 memory `|A|`. Complete for
the enrichment sub-question.

### Cost model
`delta_PFR>1/4` only if doubling is `O(1)`; honest set has doubling `~|A|`
(Sidon-like) ⇒ `delta_PFR=0`.

### Why negatives don't kill it / obstruction
New structural test; obstruction = honest large-prime set is Sidon-like (maximal
doubling) ⇒ PFR vacuous ⇒ `delta<=1/4`.

### Minimal falsifying experiment
Three toy sizes, seeds `20260719..23`; positive control: a planted small-doubling
set (must yield progression + enrichment); negative control: honest hash set (must
show maximal doubling, no enrichment).

### Quantitative promotion gate
`delta_PFR>1/4` on honest sets (near-certainly fails → scoped negative naming why the
additive-structure lane cannot enrich an honest 2-LP deck).

### Proof / Disproof track
Theorem: honest hash-derived large-prime sets have doubling `(1-o(1))|A|` ⇒
`delta<=1/4`. Disproof: a hash family producing small doubling.

### Reproduction artifact
`research/exp_pfr_dichotomy.md`,
`experiments/ecdlp_prime_field/pfr_dichotomy.sage`, result+audit, `ECFG-P1581`.

---

## Candidate: ZETA-MONODROMY-C3

### One-sentence mechanism
Use the **geometric (étale) monodromy** of the family of Semaev decomposition
varieties as the target varies (Katz–Sarnak equidistribution): a *large* monodromy
group forces decomposition counts to equidistribute (no target-specific bias, a
barrier-in-waiting); a *small* monodromy would expose a target-conditioned channel.

### Status
OPEN (speculative; flagged thin / likely count-only).

### Novelty classification
LITERATURE-ADJACENT (monodromy appears in reports only as *arboreal/iterated*
(dynamical) monodromy, batch5/6; the *geometric family monodromy* à la Katz is a
different object; but likely count-only like batch6 EXPLICIT-FORMULA).

### Semantic fingerprint
object: the family `{V_Q}` of decomposition varieties over the target-parameter base;
public ops: monodromy/Frobenius-conjugacy sampling; hidden structure: monodromy group
size controlling bias; discarded: geometry; retained: equidistribution defect;
relation primitive: n/a; compression primitive: n/a; rank mechanism: n/a; descent
mechanism: n/a; dominant exponent: bias defect (a *bias*, not a cost).

### Nearest ledger entries
`EXPLICIT-FORMULA-C3` (batch6, Sato–Tate washout), `ARBOREAL-C1` (batch5, iterated
monodromy), `LANGWEIL-METER-A3` (batch6), `MOTIVIC-B3` (batch5), `ACFA-C1` (batch7).
**Distinction**: geometric *family* monodromy of the decomposition variety (not the
preimage-tree iterated monodromy and not the single-variety point count). Honest
flag: almost certainly count/bias-only, no cost route — likely reject-tier like
EXPLICIT-FORMULA.

### Nearest literature
Katz–Sarnak (1999); Katz "Twisted L-functions and monodromy". Gap: no ECDLP-
decomposition family-monodromy computation.

### Target family / path / cost
Ordinary prime-field. **INCOMPLETE**: no target-descent route (this is a bias
diagnostic, not a backend). Flagged INCOMPLETE per template — retained only as a
negative-theory probe: if monodromy is *maximal*, it is a barrier confirming no
target bias (feeds RT-1476's "random-like support" assumption).

### Cost model / gate
Bias defect `= 0` (maximal monodromy) would *confirm* random-like support (a
barrier); nonzero defect would be a new observation. No cost crossing possible.

### Proof / Disproof / artifact
Theorem: the decomposition-family monodromy is the full symmetric/symplectic group ⇒
no target bias. Disproof: a family with small monodromy. Artifact
`research/exp_zeta_monodromy_bias.md`, `..._monodromy_bias.sage`, `ECFG-P1582`.

---

## Group D — negative-theory / barrier candidates

## Candidate: RESTRICTION-KAKEYA-D1

### One-sentence mechanism
Use a **finite-field restriction / extension estimate** (Mockenhaupt–Tao; Dvir's
polynomial method for finite-field Kakeya) to upper-bound how concentrated the
relation-hit measure can be on the Semaev variety, yielding simultaneously a
δ-ceiling (RT-1472) and an α-floor (RT-1476).

### Status
CONJECTURE (structurally-new barrier).

### Novelty classification
POSSIBLY NOVEL (restriction/Kakeya absent from all reports; Lang-Weil supply (batch6)
bounds *count*, restriction bounds *Fourier concentration* — orthogonal).

### Semantic fingerprint
object: the Semaev variety with its counting measure; public ops: Fourier extension
norm, Kakeya polynomial-method bound; hidden structure: extension-norm ceiling on
concentration; discarded: identities; retained: `L^p`-concentration exponent;
relation primitive: n/a (barrier); rank mechanism: concentration ⇒ reusable-row
ceiling; descent mechanism: concentration ⇒ branch floor; dominant exponent:
restriction exponent → `delta<=1/4` / `alpha>=3/2`.

### Nearest ledger entries
`LANGWEIL-SUPPLY-D2` (batch6, count), `ENERGY-D1` (batch3, energy), `SHEARER-D3`
(batch8, entropy), `RUDNEV`-barrier (batch3, incidence), `DELSARTE-LP-A2` (batch8).
**Distinction**: restriction/extension bounds the *Fourier-analytic concentration*
(how peaked the hit measure can be), which none of the count/energy/entropy/incidence
barriers control; it is the natural tool for "random-like support."

### Nearest literature
Mockenhaupt–Tao (2004) finite-field restriction; Dvir (2009) finite-field Kakeya;
Iosevich–Rudnev. Gap: no ECDLP relation-measure application.

### Target family
Ordinary prime-field, prime order. Excluded: degenerate low-dimensional Semaev
strata.

### Full algorithmic path (barrier)
1. deck. 2. form the empirical hit measure on `V`. 3. bound its extension norm.
4. translate to concentration exponent. 5. concentration ⇒ reusable-row ceiling
(RT-1472) and query floor (RT-1476). 6–9 n/a (barrier). Complete as a barrier.

### Cost model
Outputs a *ceiling/floor*: if the extension estimate gives concentration exponent
`c`, then `delta<=f(c)` and `alpha>=g(c)`; the gate is `f(c)<=1/4` and `g(c)>=3/2`.

### Why negatives don't kill it / obstruction
New analytic technology; obstruction = finite-field restriction exponents are often
loose, so the ceiling may be inconclusive.

### Minimal falsifying experiment
Three toy sizes, seeds `20260719..23`; positive control = deliberately concentrated
planted measure (barrier should detect low restriction norm); negative control =
random-like measure (high norm). Measure extension norm vs `L`.

### Quantitative promotion gate
Restriction bound yields `delta<=1/4` AND `alpha>=3/2` on all three sizes ⇒ closes
both gates simultaneously. Otherwise INCONCLUSIVE.

### Proof / Disproof track
Theorem: the Semaev hit measure satisfies a `R^*(2->q)` extension estimate forcing
concentration `<=1/4`. Disproof: a family violating the estimate.

### Reproduction artifact
`research/exp_restriction_kakeya_barrier.md`,
`experiments/ecdlp_prime_field/restriction_kakeya_barrier.sage`, result+audit,
ledger `ECFG-P1583`.

---

## Candidate: COMBINATORIAL-NULLSTELLENSATZ-D2

### One-sentence mechanism
Use **Alon's Combinatorial Nullstellensatz** (coefficient-nonvanishing) to prove a
*non-existence* α-floor: if a five-term membership backend must vanish on a grid
larger than its degree permits while a top coefficient is nonzero, no low-degree
backend exists.

### Status
CONJECTURE (structurally-new barrier; complements A1).

### Novelty classification
POSSIBLY NOVEL (Alon Combinatorial Nullstellensatz absent from reports; batch7's
Nullstellensatz was PC/IPS *refutation* degree — a different theorem from the
coefficient-nonvanishing existence method).

### Semantic fingerprint
object: the membership polynomial's coefficient at the top grid monomial; public ops:
coefficient extraction, grid-vanishing test; hidden structure: nonzero top
coefficient forces degree `>=` grid size; discarded: values; retained: one
coefficient; relation primitive: n/a; rank mechanism: n/a; descent mechanism: n/a;
dominant exponent: `alpha>=3/2` if the grid forces it.

### Nearest ledger entries
`NULLSTELLENSATZ-CERT-A1` (this report — *certificate degree*, feasibility),
`POLYCALC-D2` (batch7 — *refutation degree*), `APPROXDEG-D1` (batch8 — approximate
degree), `SLICE-RANK-1-D2` (batch4), `SIGNRANK-GAMMA2-B3` (batch4). **Distinction**:
Combinatorial Nullstellensatz is a *coefficient*-based existence lower bound (a
polynomial nonvanishing on a grid has degree `>=` the grid dimension), distinct from
certificate degree (A1), refutation degree (POLYCALC), and approximate degree.

### Nearest literature
Alon (1999) "Combinatorial Nullstellensatz." Gap: no membership-backend degree floor.

### Target family
Ordinary prime-field, prime order. Excluded: grids collapsing below the field size.

### Full algorithmic path (barrier)
1. deck. 2. express any backend as a polynomial that must vanish on the
non-decomposable grid and be nonzero on decomposable points. 3. extract the top
coefficient. 4. if nonzero, degree `>=` grid dimension ⇒ `alpha>=3/2`. 5–9 n/a.

### Cost model / gate
`alpha_floor = log_L(grid dimension)`; gate `alpha_floor >= 3/2` on all sizes.

### Why negatives don't kill it / obstruction
New existence method; obstruction = the required top coefficient might vanish
(Combinatorial Nullstellensatz inapplicable), giving no floor.

### Minimal falsifying experiment
Three toy sizes, seeds `20260719..23`; positive control = a grid with provably
nonzero top coefficient (floor holds); negative control = a degenerate grid (top
coefficient zero, no floor).

### Quantitative promotion gate
`alpha_floor >= 3/2` on all three sizes ⇒ closes RT-1476. Else INCONCLUSIVE.

### Proof / Disproof track
Theorem: the five-term non-decomposable grid forces backend degree `>=L^{3/2}` via a
nonzero top coefficient. Disproof: a vanishing top coefficient.

### Reproduction artifact
`research/exp_combinatorial_nss_barrier.md`,
`experiments/ecdlp_prime_field/combinatorial_nss_barrier.sage`, result+audit,
ledger `ECFG-P1584`.

---

## Candidate: AX-KATZ-BARRIER-D3

### One-sentence mechanism
Turn A2 into a hard barrier: **Ax–Katz** forces the honest decomposition count into a
fixed `p`-adic residue class, so any enrichment claiming `delta>1/4` must produce
solution counts violating the Ax–Katz divisibility floor — a `p`-adic *congruence*
obstruction on `delta`, categorically distinct from every prior (archimedean/
entropic) supply barrier.

### Status
CONJECTURE (structurally-new barrier; partner of A2).

### Novelty classification
POSSIBLY NOVEL (p-adic congruence supply barrier; all prior supply barriers — matroid
independence, VC, Delsarte, Shearer entropy, Lang-Weil count, energy — are
archimedean or entropic inequalities, never a modular congruence).

### Semantic fingerprint
object: `#decompositions mod p^{mu}`; public ops: Ax–Katz exponent; hidden structure:
forced `p`-divisibility of honest supply; discarded: identities; retained: congruence
class; relation primitive: n/a; rank mechanism: congruence caps independent cycles;
descent mechanism: n/a; dominant exponent: `delta<=1/4` if `mu` non-vacuous.

### Nearest ledger entries
`AX-KATZ-SUPPLY-A2` (this report — the *meter*), `SHEARER-D3` (batch8),
`LANGWEIL-SUPPLY-D2` (batch6), `VCDIM-D3` (batch7), `MATUNION-INDEP-D2` (batch5).
**Distinction**: a *modular congruence* barrier, not an inequality — pairs with A2 as
meter↔barrier exactly like prior batches paired a meter with its killer.

### Nearest literature
Ax (1964), Katz (1971), Wan (Newton polygons over p-adic). Gap: no supply-barrier use.

### Target family
Ordinary prime-field, prime order; `p` in the non-vacuous Ax–Katz regime
(`n - sum d_i > 0`).

### Full algorithmic path (barrier)
1. deck. 2. compute Ax–Katz exponent `mu` for the honest 5-term system. 3. if
`mu>=1`, the honest count is `≡0 mod p^{mu}`, forcing supply into buckets too coarse
for `delta>1/4`. 4–9 n/a.

### Cost model / gate
Gate: `mu>=1` AND the forced congruence caps enriched cycle supply at `delta<=1/4`.

### Why negatives don't kill it / obstruction
New modular obstruction; obstruction = `mu<=0` (vacuous) for `m=5` typical degrees —
the regime A2 measures. If vacuous, this barrier is silent (honest scoped null).

### Minimal falsifying experiment
Three toy sizes, seeds `20260719..23`; positive control = designed high-`mu` system
(barrier bites); negative control = `mu<=0` system (silent). Cross-check with A2's
measured `v_p(#)`.

### Quantitative promotion gate
`mu>=1` and enrichment-inconsistent on all three sizes ⇒ `delta<=1/4` congruence
certificate closing RT-1472. Else INCONCLUSIVE.

### Proof / Disproof track
Theorem: `mu = ceil((n - sum d_i)/max d_i) >= 1` for `m=5` ordinary systems, forcing
`delta<=1/4`. Disproof: a family with `mu<=0`.

### Reproduction artifact
`research/exp_axkatz_barrier.md`,
`experiments/ecdlp_prime_field/axkatz_barrier.sage`, result+audit, `ECFG-P1585`.

---

## Ranking

Scores 0–5 on: distance from prior ledger mechanisms (Dist); plausibility of an exact
verifier (Ver); chance of changing an exponent not a constant (Exp); complete-path
coverage (Path); toy-scale falsifiability (Fals); literature-novelty confidence
(Nov); freedom from hidden preprocessing/memory cost (Clean).

| Cand | Dist | Ver | Exp | Path | Fals | Nov | Clean | Verdict |
|---|---|---|---|---|---|---|---|---|
| NULLSTELLENSATZ-CERT-A1 | 4 | 5 | 4 | 5 | 5 | 4 | 5 | **winner: conservative** |
| AX-KATZ-SUPPLY-A2 | 5 | 5 | 3 | 4 | 4 | 5 | 5 | keep |
| CONTAINER-CEILING-A3 | 4 | 3 | 3 | 3 | 4 | 4 | 4 | keep |
| MATCHING-VECTOR-B1 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | keep (self-killing, names lane) |
| ELEKES-SZABO-B2 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | **winner: representation** |
| NEWTON-OKOUNKOV-B3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | keep (thin) |
| METHOD-OF-MULTIPLICITIES-C1 | 5 | 4 | 4 | 5 | 4 | 5 | 3 | **winner: high-risk** |
| PFR-DICHOTOMY-C2 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | keep (near-certain kill) |
| ZETA-MONODROMY-C3 | 3 | 2 | 1 | 1 | 3 | 3 | 4 | **reject: INCOMPLETE path, no descent, no rho comparison** |
| RESTRICTION-KAKEYA-D1 | 5 | 3 | 4 | 4 | 3 | 5 | 4 | keep (barrier, high-EV) |
| COMBINATORIAL-NSS-D2 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | keep (barrier, high-EV) |
| AX-KATZ-BARRIER-D3 | 5 | 4 | 3 | 4 | 4 | 5 | 5 | keep (barrier, high-EV) |

Rejected: **ZETA-MONODROMY-C3** — semantic novelty ≥3 but fails the hard filters
(INCOMPLETE target-descent path, no quantitative rho comparison). Retained only as a
labelled negative-theory probe of the "random-like support" assumption. All other
eleven pass the filters (novelty ≥3, complete route or explicit barrier scope,
quantitative rho/gate comparison, precise ledger distinction).

Winners:
1. **Conservative** — NULLSTELLENSATZ-CERT-A1 (exact feasibility-certificate α-meter
   on RT-1476; different theorem from batch7 refutation degree; lives in the
   preserved nonlinear-circuit exception of P1512-R1).
2. **Representation** — ELEKES-SZABO-B2 (structural δ-meter that measures the value
   of the group-law special form — the exact feature separating Semaev from a generic
   polynomial and the crux of RT-1472).
3. **High-risk** — METHOD-OF-MULTIPLICITIES-C1 (the untried multiplicity-`>1` arm of
   the jet seed; the only candidate here with a *constructive* route that could lower
   `alpha` below `3/2` if `s=L^{eps}` survives the `s^n` cost).

---

## Winner contracts and first executable commands

### Contract 1 — NULLSTELLENSATZ-CERT-A1 (`ECFG-P1574`)

```yaml
experiment: ECFG-P1574
title: Effective arithmetic Nullstellensatz feasibility-certificate alpha-meter
hypothesis: >
  The minimal multiprojective degree of a feasibility certificate for target
  membership in the P1510 source ideal grows like L^{alpha_cert} with
  alpha_cert >= 3/2 for m=5 ordinary prime-order curves (closing RT-1476), and
  a downward trend to alpha_cert < 3/2 would reopen a sub-rho route.
null_hypothesis: alpha_cert is >= 3/2 on the successful-membership subset.
claim_tier: META-METER  # measures an exponent, claims no solve
target_family: ordinary E/F_p, prime n, gcd(p,n)=1, j not in {0,1728}
parameters:
  primes: [1009, 4099, 16411]
  m: [3, 4, 5]
  seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
  factor_base: canonical L=q^{1/5} subgroup-x deck (P1473/P1477 construction)
controls:
  positive: hand-built ideal with known low-degree membership certificate
  negative: random dense ideal of matched shape
metrics:
  - certificate multiprojective degree D (measured, successful subset only)
  - fitted alpha_cert = log_L(D) vs L, per m
  - R^2 of the fit
promotion_gate: alpha_cert(m=5) fit < 3/2 with R^2 > 0.9  # else scoped negative
verification: independent re-substitution of g_i and exact identity check over Z
artifacts:
  implementation: experiments/ecdlp_prime_field/nss_cert_alpha_meter.sage
  result: experiments/ecdlp_prime_field/nss_cert_alpha_meter_result.json
  audit: experiments/ecdlp_prime_field/nss_cert_alpha_meter_verify.sage
```

First command:

```bash
sage experiments/ecdlp_prime_field/nss_cert_alpha_meter.sage \
  --primes 1009,4099,16411 --m 3,4,5 --seeds 20260719-20260723 \
  --deck subgroup_x_L15 --controls pos,neg \
  --out experiments/ecdlp_prime_field/nss_cert_alpha_meter_result.json
```

### Contract 2 — ELEKES-SZABO-B2 (`ECFG-P1578`)

```yaml
experiment: ECFG-P1578
title: Elekes-Szabo group-law special-form delta-meter for RT-1472
hypothesis: >
  The symmetrized Semaev variety is the Elekes-Szabo special (algebraic-group)
  case; its relation-hit concentration net of Theta(L^2) coset advice yields
  delta <= 1/4 (closing RT-1472's structural hope). Net concentration > 1/4 on
  a prime-order family would reopen it.
null_hypothesis: net concentration delta_ES <= 1/4.
claim_tier: META-METER
target_family: ordinary E/F_p, prime n, j not in {0,1728}, non-CM
parameters:
  primes: [1009, 4099, 16411]
  seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
  grid_sizes: N in {L, 2L, 4L}, L = q^{1/5}
controls:
  positive: planted special-form (subgroup) grid  -> expect concentration
  negative: random degree-matched non-special F   -> expect O(N^{8/3}) spread
metrics:
  - hits per row vs N (log-log slope)
  - excess over Elekes-Szabo generic ceiling
  - delta_ES net of measured advice cost
promotion_gate: delta_ES > 1/4 net of advice on all three sizes, upward trend
verification: every counted incidence re-checked as a valid EC-addition tuple
artifacts:
  implementation: experiments/ecdlp_prime_field/elekes_szabo_delta_meter.sage
  result: experiments/ecdlp_prime_field/elekes_szabo_delta_meter_result.json
  audit: experiments/ecdlp_prime_field/elekes_szabo_delta_meter_verify.sage
```

First command:

```bash
sage experiments/ecdlp_prime_field/elekes_szabo_delta_meter.sage \
  --primes 1009,4099,16411 --seeds 20260719-20260723 \
  --grid L,2L,4L --controls special,random \
  --out experiments/ecdlp_prime_field/elekes_szabo_delta_meter_result.json
```

### Contract 3 — METHOD-OF-MULTIPLICITIES-C1 (`ECFG-P1580`)

```yaml
experiment: ECFG-P1580
title: Method-of-multiplicities five-term membership backend (jet seed, s>1 arm)
hypothesis: >
  An s-fold Hasse-derivative-vanishing membership backend achieves query
  alpha_mult = log_L(eliminant_degree / s); a usable s = L^{eps} would give
  alpha_mult < 3/2 and cross RT-1476, IF the s^n interpolation/verification cost
  does not dominate. Strong prior: gain is only log_L(s) = O(1) over F_p.
null_hypothesis: net alpha_mult >= 3/2 for all s > 1 (jet lane last arm closed).
claim_tier: RELATION-BACKEND  # candidate membership relations, not ECDLP recovery
target_family: ordinary E/F_p, prime n, p large enough for s < p multiplicity room
parameters:
  primes: [4099, 16411, 65537]
  m: 5
  multiplicity_s: [1, 2, 4, 8]
  seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
controls:
  positive: designed multiplicity-friendly system -> alpha_mult drops with s
  negative: system where multiplicity gives no degree reduction
metrics:
  - eliminant degree at each s
  - net alpha_mult = log_L(deg/s) INCLUDING s^n interpolation cost
  - fit alpha_mult vs s and vs L
promotion_gate: net alpha_mult fit < 3/2 at s = L^{eps}, eps > 0, all three sizes
verification: recompute Hasse derivatives and multiplicity constraints exactly
artifacts:
  implementation: experiments/ecdlp_prime_field/multiplicity_backend.sage
  result: experiments/ecdlp_prime_field/multiplicity_backend_result.json
  audit: experiments/ecdlp_prime_field/multiplicity_backend_verify.sage
```

First command:

```bash
sage experiments/ecdlp_prime_field/multiplicity_backend.sage \
  --primes 4099,16411,65537 --m 5 --mult 1,2,4,8 \
  --seeds 20260719-20260723 --controls pos,neg \
  --out experiments/ecdlp_prime_field/multiplicity_backend_result.json
```

---

## Red-team: are the three winners disguised repetitions or cost-negative?

**NULLSTELLENSATZ-CERT-A1.**
- *Disguised repeat?* Closest is batch7 `POLYCALC-D2`. That measures **refutation**
  degree (proving a non-instance has no decomposition); A1 measures the **feasibility**
  certificate degree×height of a *true* membership — opposite sign, different theorem
  (Kollár/D'Andrea–Krick–Sombra effective NSS vs Razborov PC lower bound). Also
  distinct from `SUBRES` (eliminant, not certificate-height) and `P1512-R1` (linear
  atomizer; A1 is the nonlinear-circuit exception). Not a repeat.
- *Cost-negative?* **Almost certainly, and that is the point.** Kollár's `d^n` and the
  strong prior `beta->3/2` predict `alpha_cert >= 2`. A1 most likely *re-derives and
  matches the rho barrier from below* — closing RT-1476 rather than crossing. It is a
  scoped-negative/exact-tightening, not a break.

**ELEKES-SZABO-B2.**
- *Disguised repeat?* Closest are `ENERGY-D1` and the batch3 Rudnev incidence barrier.
  Those bound hits treating `F` as generic and *discard* the group law; Elekes–Szabó
  is the dichotomy that *isolates and measures* the group-law special case. Different
  theorem, different information. Not a repeat.
- *Cost-negative?* Most likely: the special-form concentration is offset by
  `Theta(L^2)` coset advice, reproducing the batch1 `RT-1472` exponent `2/3` and
  giving `delta<=1/4`. Scoped negative that finally *names why* the group structure
  does not enrich an honest 2-LP deck. Not a break.

**METHOD-OF-MULTIPLICITIES-C1.**
- *Disguised repeat?* Closest are `P1509`/batch4 `JET-B1` (multiplicity **one**). C1
  is the untried multiplicity-`>1` regime with the DKSS multiplicity-Schwartz–Zippel
  degree/point trade — a genuinely new interpolation operation, not a re-run. Not a
  repeat.
- *Cost-negative?* Likely: over `F_p` the degree gain is `log_L(s)` while the
  interpolation/verification cost scales `s^n`, so the net exponent probably stays at
  `3/2` (constant-factor win only) — closing the jet lane's last arm. But it is the
  **one winner with a real constructive crossing route** if `s=L^{eps}` survives the
  cost; hence its place as the high-risk pick.

**Meta-assessment (unchanged from batches 5–8).** All three winners are
scoped-negatives / exact-tightenings, not crossings. The **higher-EV** work this batch
is the three barriers: `RESTRICTION-KAKEYA-D1` (closes *both* gates if the extension
estimate bites), `COMBINATORIAL-NSS-D2` (α-floor `>=3/2` closes RT-1476), and
`AX-KATZ-BARRIER-D3` (δ-congruence `<=1/4` closes RT-1472). Each imports a lower-bound
technology **no prior barrier used** (finite-field restriction; Alon coefficient
nonvanishing; Ax–Katz p-adic congruence) and each threshold, if reached, *closes a
live gate* — the highest-value outcome available after eleven reports.

## Claim discipline

No break is claimed. Every candidate is CONJECTURE / HYPOTHESIS / HEURISTIC / OPEN at
toy scale under stated models. Certificate correctness, relation validity, and count
congruences are distinguished from verified single-target ECDLP recovery; no meter or
backend here asserts above a META-METER / RELATION-BACKEND tier. A failed candidate is
a **scoped negative result** bounded to the tested curves, parameters, degrees, and
budget — never evidence that prime-field ECDLP cannot be improved. The two live
rho-crossing gates **RT-1472** (`delta>1/4`) and **RT-1476** (`alpha<3/2`) **remain
open**; this report supplies exact meters and structurally-new barriers aimed at
closing or tightening them, not a crossing.
```

Sources consulted for novelty: [Elekes–Szabó in four dimensions](https://arxiv.org/abs/1607.03600), [Projective geometries arising from Elekes–Szabó problems](https://arxiv.org/pdf/1806.03422), [quasi-polynomial DLP small characteristic](https://arxiv.org/abs/2206.10327), [McGuire–Mueller Gröbner-free IC](https://eprint.iacr.org/2017/1262.pdf).
