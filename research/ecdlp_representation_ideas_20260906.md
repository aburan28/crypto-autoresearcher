# ECDLP representation ideas, 2026-09-06 (TASK-20260906-f71aaa)

Idea-generator session against `RQ-ECDLP-623a32` under the object frame of
`docs/object-frame-ideation.md` and the family table `KN-TECH-ee6696`. Four
proposal records were written; the fifth assigned identifier
(`IDEA-20260906-f95c77`) is unused and stays unused. Every record is
`status: proposed`, `approved_by: null`, `novelty_status: unverified`. No
experiment, hypothesis, approval, or edit to any existing record was made.

Method, stated so it can be audited: every path in the handoff's `inputs:`
was read in full (the 26 listed records plus the layout model
`IDEA-20260905-4dca34` and the family table). Corpus dedup was by grep over
`ledger/` and `knowledge/` for each candidate's key terms (division
polynomial / cubical / biextension; AGL / block system; Riemann-Roch / theta
group / regular representation; trace-zero / quadratic twist / `E(F_{p^2})`;
elliptic net / Somos; quadratic order / small norm; Schur-Zassenhaus /
canonical section / self-pairing), followed by reads of the nearest hits
(`IDEA-20260902-63dbc0`, `IDEA-20260905-3a30d5`, `IDEA-20260904-e9675e`,
`IDEA-20260905-be63be`, `EV-NET-001`, `TASK-20260905-a6ea8a`). The knowledge
MCP index was not queried (the runtime binding notes it starts empty). No web
search was performed; every external reference in the records is therefore
`provenance: recalled` with `verified_by: null`, and every record is
`unverified`. No interpreter was available to this session, so the YAML files
were not machine-parsed; the Coordinator must run `tools/validate_ledger.py`
before relying on them (the files were written in the folded-scalar style of
the layout model and re-issued once to remove plain scalars containing
mapping indicators).

## 1. Candidate objects enumerated, with disposition

The coordinator's ten object classes from the sibling handoff
`TASK-20260905-a6ea8a` (which produced no files, so they are guidance and not
prior art) were used as the enumeration, plus this session's own. Each object
was scored as `docs/inventor-protocol.md` section 1 asks: new or repackaging;
one-step propagation definable; survival.

| object (representation, operation set) | R-class | lossy-projection verdict against the named Sigma | disposition |
|---|---|---|---|
| Cubical lift (X~ : Z~) over the Kummer line, Sigma = cubical [m]~ | R3 | Canonical N^2-th-root section splits the lift (zero bits); residual defect d is Class III with auxiliary psi_m(x(P)) | **filed** `IDEA-20260906-86cc17` |
| Quadratic-order small-norm lift of x, Sigma = translation by factor-base elements | R1 | Class I (F2 as component); the representation changes membership and solve shape only | **filed** `IDEA-20260906-09b937` (control) |
| Level-N Riemann-Roch / theta linearisation, Sigma = operator composition | R2 | Injective (regular representation); isotypic blocks = MOV fields | **filed** `IDEA-20260906-aa6da3` (mechanism, returned unverified with obstruction) |
| F_{p^2}-twist coset P + G', Sigma = translation by G' and Frobenius | R3 | Block system on the ambient group, injective on G; padding tautology | **filed** `IDEA-20260906-476f20` (control) |
| Level-n embedding, n < N, Sigma = E[n]-translation | R2 | Orbit object is [n]P, injective | closed in `aa6da3` (D) |
| Riemann-Roch decomposition presentation (section of L((m-1)O + R)) | R2 | A presentation of F2 | already in corpus: `FINDING-PF-IC-001` line 1636, `IDEA-20260904-e9675e` table; not re-filed |
| Integer / digit / redundant encodings of x, any algebraic Sigma | R1 | No algebraic operation is compatible with a non-algebraic encoding; objects are Class II (meter of `IDEA-20260802-002`) or bounded-degree Class III (pinned by `IDEA-20260815-f558e4` E) | closed, section 3 item C1; nothing filed |
| Elliptic-net / EDS sequence object | R3 | `EV-NET-001` scoped negative; `KN-FIND-b7e091` Oracle B | not re-filed; the one unmeasured net-adjacent object is d of `86cc17` |
| (2,2)-glued genus-2 Jacobian of E x E, Mumford coordinates of the pair (P, Q) | R3 | Exists over F_p only when the 2-division cubic has cyclic Galois group; genus-2 index calculus at p^(4/3) versus rho at p^(1/2) | dominated (`KN-FIND-61347e`, `IDEA-20260727-005` C3); the (N,N) version is `IDEA-20260808-fa1d80` |
| Torsion-translate set {P + T : T in E[l]}, translation frames, l-division-point orbit pattern | R3 | The rational element determines P (injective, `dadcd2` L3); the Galois pattern of l-division points of P is P-independent (constant) | closed, section 3 item C5 |
| Distribution-valued object: multiset of x([a]P) over an index set A, Sigma = dilation | R3 | Comparing dilated multisets is a BSGS collision; generic ceiling `KN-TECH-005` | closed as F1 in new notation, item C6 |
| Tuple / pair objects under diagonal affine action | R3 | Already proved: `IDEA-20260902-63dbc0` Theorems A-C | duplicate avoided |
| Dual-number and Z/p^2 lifts | R3 | F5 (`KN-TECH-73630e`), `IDEA-20260905-3a30d5` | not re-filed; cited as the additive template of `86cc17` |
| Miller-function / divisor-class representation | R3 | The N-level version is `aa6da3`; the pairing value on G is trivial for gcd(N, p-1) = 1 | absorbed into `aa6da3` and `86cc17` |

## 2. Corpus dedup against the seven cited lane proposals

- `IDEA-20260807-8027a2`, `-e6d79e`, `-dadcd2` (degree-2 coordinates, model
  lever 1): no filed record uses a degree-2 coordinate as its object.
  `86cc17` uses the Kummer line as the *base* of a lift and says so; the lift's
  content is the un-quotiented scaling, which those records never track.
  `476f20` reuses `dadcd2` (L3) rationality as the mechanism seen from the
  extension field and cites it.
- `IDEA-20260808-2e14f7` (degree-d maps E -> P^1): none of the four objects is
  a single function on E of bounded degree. The one function-valued object,
  d of `86cc17`, has degree N^2 and is used as a statistic, not as a factor-base
  window; the F_{p^2}-component coordinate x_1(P + T) that this session also
  considered IS a degree-4 function on E and was dropped as inside `2e14f7`.
- `IDEA-20260806-0c9de1` (X_1(N) torsor): not used; `86cc17` cites its
  "second clause fails derivably" pattern as the template for its own audit.
- `IDEA-20260808-fa1d80` ((E x E)[N] split quotient): the (2,2)-gluing variant
  was considered and dropped as dominated (section 1); `fa1d80` is cited as
  the (N,N) owner.
- `IDEA-20260905-1dd2e5` (isogeny-class heterogeneity): not touched; no
  record moves between curves.
- `IDEA-20260807-4fc635` (null battery): every record carries the PGL_2
  battery, the translation-conjugate null, a matched random curve, and rho /
  BSGS matched controls, as the handoff requires.

Further nearest records read and discriminated in the records themselves:
`IDEA-20260902-63dbc0` (tuple closure, avoided), `IDEA-20260905-3a30d5`
(additive-lift defect, cited with the precise difference), `IDEA-20260904-e9675e`
and `FINDING-PF-IC-001` (Riemann-Roch presentation, not re-filed),
`EV-NET-001` (net statistics, cited).

## 3. The four records

| id | class | R-class | operation set Sigma | trichotomy | attack stage | non-generic operation | novelty | cost |
|---|---|---|---|---|---|---|---|---|
| `IDEA-20260906-86cc17` | representation | R3 (cubical lift) | cubical [m]~, m in (Z/N)^*, with renormalisation | III, coordinate-dependent (auxiliary psi_m) | collision structure | canonical cubical section / N^2-th root in O(log N) | unverified | low / low |
| `IDEA-20260906-09b937` | control | R1 (quadratic-order residue) | translation by factor-base elements | I, partial-action (F2 component) | factor-base membership, relation decomposition | norm-ball membership by Gauss reduction, O(log p) | unverified | low / low |
| `IDEA-20260906-aa6da3` | mechanism | R2 (level-N / Riemann-Roch model) | operator composition | none because injective; returned unverified with obstruction (F4) | collision structure, linear algebra | none survives (it is the pairing) | unverified | low / low |
| `IDEA-20260906-476f20` | control | R3 (Weil restriction / twist) | translation by G' and Frobenius | I, partial-action on the ambient group; injective on G | factor-base membership, relation decomposition | subfield-coordinate test on E(F_{p^2}) | unverified | low / low |

Diversity check: three R-classes present; no two records share an R-class
and an operation set. Factor-base escape declarations: `09b937` is
KN-OPEN-020 class 2 (implicit membership) with all six costs charged;
`476f20` declares itself inside the scoped-out bounded-degree class for the
target and stops. `KN-FIND-007` is respected in both: neither claims a mean
yield.

## 4. Ranking rationale and the recommended first test

Ranking by expected information gain per unit cost:

1. **`86cc17` first.** It is the only record whose lead branch is not
   derivably empty: the residual defect d has degree N^2, so no Weil-bound
   pinning applies and its distribution and DL-spectrum are genuinely
   unmeasured. The minimal test is the cheapest valid discriminator in the
   set because (i) Stage 1 is four exact identities (G1-G4) that cost minutes
   and can each fail, (ii) Stage 2 reuses an existing instrument
   (`EXP-ECDLP-184fc4`'s DL-spectrum census, with its anomalous-curve
   calibration inherited from `IDEA-20260905-3a30d5`), and (iii) the nearby
   object with N | p - 1 is a known-true positive control (the Tate
   self-pairing's k^2 character) that the instrument must read as a quadratic
   ramp, which separates "white because nothing is there" from "white because
   the instrument is blind". Predicted outcome is the closure branch; the
   value is that the R3 cubical class then carries a mechanism (multiplicative
   Schur-Zassenhaus plus the exact law d([m]P) psi_m(x(P))^2 = d(P)^(m^2))
   instead of an absence.
2. **`09b937` second.** One hour on the frozen E1-01 harness answers the
   coordinator's quadratic-order R1 item with a measured ratio and a
   bound-product mechanism; predicted null, but the measurement is the
   deliverable.
3. **`476f20` third.** A forced value with a composite-order nearby object;
   closes the Weil-restriction R3 class on prime-order targets with the
   padding mechanism and the E3 bound. Low information gain because the forced
   value is near-certain; filed because the coordinator's item (6) had no
   record.
4. **`aa6da3` last.** The R2 closure. Its forced factorisation pattern is a
   theorem-level consequence of ord_N(p); the toy run is a bug check on the
   derivation. Lowest priority for exactly that reason.

## 5. Honest accounting (docs/inventor-protocol.md section 5)

**Objects studied.** The fourteen (representation, operation set) pairs of
section 1; four filed, ten closed in this report or already owned by a
committed record.

**Depth of verified structure**, at the tier actually verified (nothing here
was run; everything is derivation by this session and is `unverified`):

- `86cc17` (B)-(C): exact statements (uniqueness of the N^2-th root section;
  the covariance law; the three-term identity; the u^2 scaling), derived this
  session, unreviewed. The statistical prediction is a heuristic (H1) with a
  validation route.
- `09b937`: the bound-product argument is a reading of the recalled
  Coppersmith / Jochemsz-May condition; the lattice-count H1 is Gauss's
  theorem. The prediction is a pre-registered sign, not a theorem.
- `aa6da3` (A)-(D): derived this session from H^2(G, F_p^*) = 0 and the
  Galois action on characters; the identification with F4 rests on
  `KN-TECH-032` and `KN-FIND-3a7d42`, quoted through `KN-TECH-ee6696`.
- `476f20` (A)-(B): elementary counting, derived this session; (C) rests on
  `KN-FIND-61347e` and `IDEA-20260727-005` C3 as relayed by `KN-TECH-ee6696`.

**dominated_by.** `n/a (no result claimed)` for the session, written after
checking every frontier row the corpus holds: parallel rho with distinguished
points at 0.886 sqrt(N) and O(1) memory (`KN-TECH-006`), automorphism-
discounted rho (`KN-TECH-018`), BSGS at (sqrt(N), sqrt(N)) (`KN-TECH-031`),
multi-target sqrt(T N), the preprocessing frontier S T^2 = Theta(N)
(`KN-LIT-013` via `KN-TECH-ee6696`), prime-field index calculus with no known
advantage (`KN-OPEN-001`), pairing transfer at small embedding degree
(`KN-TECH-032`), and the windowed small-root lane (E1-01, `IDEA-20260808-2e14f7`).
Each record's own `dominated_by` field names the rows individually; `476f20`
and `aa6da3` are dominated by rho by explicit factors (about p^(1/2) and
Theta(N^2) setup respectively); `86cc17` and `09b937` mount no attack.

**sota_delta.** 0 on time exponent, 0 on memory exponent, 0 on data/queries,
for every record and for the session. Deliverable deltas, as counts: four
representation classes of `RQ-ECDLP-623a32` audited in-record (R3 cubical,
R1 quadratic-order, R2 level-N, R3 Weil restriction); two exact laws
(`86cc17` (C); `aa6da3` (B)'s forced factorisation); two forced values
(`476f20` padding and rank; `86cc17` b = 1 under [m] with auxiliary); one
genuinely unmeasured statistic (d) with a pre-registered null and a
known-true nearby object.

**Enumerated closures**, each with its mechanism. All are derivations of this
session at proposal tier and their honest status is `unverified`; each names
an obstruction and what remains open, per section 4, rather than a count.

- C1, R1 non-algebraic encodings. Obstruction: every operation set the ECDLP
  supplies is algebraic (group law, endomorphisms, Frobenius), and an
  encoding that is not a rational function of the coordinates (integer lift,
  digits, redundant forms) has no block system under any algebraic action;
  such objects are Class II (priced by the (L, b) meter) or bounded-degree
  Class III statistics (pinned, `f558e4` E). The only R1 representation with a
  cheap non-polynomial membership found is the quadratic-order ball, filed as
  `09b937` with a predicted null. Remains open: the formal cost class that
  would make this a theorem (`KN-OPEN-020`, `KN-TECH-ee6696` item 9).
- C2, R2 models. Obstruction: every single-point coordinate object of a model
  is a rational function on E, classified by degree (2: Kummer, lever 1;
  d: `2e14f7`), or a level structure (N: F4 by `aa6da3`; n < N: injective
  [n]P; rational-torsion models unavailable on prime-order curves, `dadcd2`).
  Remains open: genus-2 theta models (forwarded by `8027a2`) and the
  Riemann-Roch presentation on `e9675e`'s table.
- C3, R3 abelian-surface embeddings of the pair. Obstruction: Tate's theorem
  forces the complementary factor to order about p, and genus-2 index
  calculus costs p^(4/3) against rho's p^(1/2) (`KN-FIND-61347e`,
  `IDEA-20260727-005`). Remains open: only a propagation rule along the
  Lagrangian pencil (`fa1d80` prediction 3).
- C4, R3 Weil restriction and twist. Mechanism: padding tautology and E3
  bound (`476f20`). Remains open: nothing on prime-order targets; the
  extension-field setting is Gaudry's and not this program's.
- C5, R3 torsion translates and frames. Obstruction: rationality (`dadcd2`
  L3) makes the translate set injective and the l-division Galois pattern
  P-independent; frames over a Gamma-orbit are F6, frames over an interval
  are injective. Remains open: nothing found.
- C6, R3 distribution-valued objects under dilation. Obstruction: dilated
  index-set overlap is a BSGS collision, generic (`KN-TECH-005`). Remains
  open: nothing found.
- C7, Class I objects on G with an algebraic operation set. Obstruction, read
  from `IDEA-20260902-63dbc0` at m = 1 together with the fact that every
  F_p-rational morphism E -> E is an isogeny plus a translation and every
  endomorphism acts on G as a scalar: the group generated by any such Sigma is
  inside AGL(1, N), whose lossy block systems are the recentred Gamma-orbit
  partitions (F6, `863e36`) or none. So a new Class I object on G must be a
  partial action (factor-base translation, F2) or must act on an ambient set
  (`476f20`'s G'-cosets, which are injective on G). Remains open: F6
  arithmetic selectors (`863e36` C6) and the KN-OPEN-020 classes.
- C8, elliptic nets and local rings: owned by `EV-NET-001` / `KN-FIND-b7e091`
  and by `KN-TECH-73630e` / `IDEA-20260905-3a30d5`; not re-closed here, cited.

**Open directions for the next session.**

1. Class III fast high-degree functions as a family: d of `86cc17` and the
   Fermat-quotient digits of `3a30d5` are two members; the DL-spectrum census
   is the shared instrument, and a grammar of such functions (ladder-computable
   rational functions of degree about N^2) with the census run over it would be
   the natural successor to `IDEA-20260802-002`'s meter for this class.
2. Class II amortised branching (`IDEA-20260806-c5d183` forward guidance (a))
   was not touched by this session; no representation-specific branching
   object with prunable branches was found.
3. KN-OPEN-020 high-degree factor bases with an algebraic decomposition handle:
   the cubical-defect window {P : d(P) < T} has O(log N) membership but no
   decomposition handle other than enumeration, and was not filed for that
   reason; a high-degree description that comes with a solver is the missing
   object.
4. F6 arithmetic selectors (`863e36` C6), still unmeasured.
5. Genus-2 theta / Kummer-surface representations of the pair framed as
   locating the graph of [k]: dominated as an algorithm (C3), open only as the
   propagation-rule question of `fa1d80`.

**Limits of this session.** No compute; no web; no YAML parse; identifiers
were pre-assigned by the Coordinator and `tools/allocate_id.py --check` was
not run here (no shell). One identifier unused. Every claim above the
derivation tier belongs to the cited record, not to this session.
