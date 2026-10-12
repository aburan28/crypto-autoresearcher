# Primary-source and definition intake: RQ-SSI-1946c9

Date: 2026-10-04.  Scope: zero-run intake for `GOAL-SSI-2fa82a`.
This note makes no correctness, security, hardness, parameter, or novelty claim.
It opens no batch, hypothesis, experiment, or implementation task.

## Result

The four required primary specifications were obtained and read.  None is a
plain-EndRing PKE in the sense fixed below.  Each obtains public evaluation and
secret inversion from additional structured data or a separately named
assumption.  The live definition impediment is therefore:

> No audited mechanism currently supplies a sender, who knows only the public
> key, with an efficiently evaluable encryption map while reserving inversion
> to a secret EndRing witness, without also exposing or assuming an orientation,
> hidden-isogeny/torsion interface, commutative group action, or LIT diagram.

This is an interface obstruction for the mechanisms examined, not an
impossibility theorem and not evidence about EndRing hardness.

## Retrieved primary specifications

| Corpus pointer | Primary specification read | SHA-256 of retrieved PDF | Boundary relevant to this goal |
|---|---|---|---|
| `KN-LIT-6572` | De Feo et al., *SÉTA: Supersingular Encryption from Torsion Attacks*, ePrint 2019/1291 / ASIACRYPT 2021 | `e68fa5871be93bc031b5c68773b7bf1317c8033ebf917613c327aa73d6a309cd` | The trapdoor one-way function encodes a generalized CGL walk.  Its OW-CPA theorem reduces recovery to TCSSI (Problem 3.2), whose instance includes structured torsion images and whose trapdoor uses an oriented endomorphism.  Section 5's O-Uber/oriented-class-group discussion does not turn that theorem into a reduction from plain EndRing. |
| `KN-LIT-6628` | Moriya--Onuki--Takagi, *SiGamal: A Supersingular Isogeny-Based PKE and Its Application to a PRF*, DOI `10.1007/978-3-030-64834-3_19` | `b58a63807dc95cf63f36af671444889791920908020541bd82e315067b324061` | The public key and ciphertext carry curve/point pairs transformed by hidden class-group actions.  OW-CPA and IND-CPA are stated under P-CSSCDH and P-CSSDDH respectively, not under plain EndRing. |
| `KN-LIT-827` | Eaton--Jao--Komlo--Mokrani, *Towards Post-Quantum Key-Updatable Public-Key Encryption via Supersingular Isogenies*, DOI `10.1007/978-3-030-99277-4_22` | `66c77e4fb4c82ce4adb0620ad835f68eaebc629b6ca9c11d394a5c2344af2f52` | The paper studies an updatability layer.  Its viable CSIDH symmetric construction is a group-action/DEM hybrid and its IND-CPA-U result assumes the underlying construction; it is not a new plain-EndRing inversion interface.  The paper also records the public-domain homomorphism obstruction for asymmetric updates. |
| `KN-LIT-1260` | Moriya--Stopar, *LIT-SiGamal: An Efficient Isogeny-Based PKE Based on a LIT Diagram*, ePrint 2024/521 | `6921f7fb3ed409c9861c52011d9bf39c5e638e97af5f3859f6606367525ff536` | Encryption and decryption use a structured LIT/Kani diagram with public torsion bases/images and matrices.  The IND-CPA statement is under LIT-DDH.  EndRing knowledge used in setup/key generation does not by itself make the security game plain EndRing. |

Acquisition routes were the authors' ePrint record through an Internet Archive
snapshot for ePrint 2019/1291 and 2024/521, and the DOI-linked Springer PDFs for
the two proceedings papers.  Direct ePrint PDF requests returned HTTP 403 in
this session.  The archived bytes above were fully text-extracted and inspected;
the hashes make the evidence boundary reproducible.

## Frozen EndRing problem contract

Until a proposal justifies a different interface, `EndRing-eval(D)` means:

- **Field and input.** A security parameter, a prime `p`, public parameters,
  and a canonical encoding of a supersingular elliptic curve
  `E / F_{p^2}` sampled from an explicitly specified candidate-dependent
  distribution `D`.  The distribution is part of the problem, not hidden in
  KeyGen.
- **Auxiliary information.** None beyond the curve encoding and declared
  public parameters.  In particular, no orientation, secret path, torsion
  images, hidden isogeny, connecting ideal, special endomorphism, or setup
  transcript is included unless the proposal names a distinct augmented
  problem.
- **Output.** Four explicitly and efficiently evaluable endomorphisms forming
  a `Z`-basis of `End(E)` together with enough representation data to compose,
  add, and verify them.  An abstract maximal order or its isomorphism class is
  not sufficient when decryption needs to evaluate an endomorphism on points.
- **Output equivalence.** Any basis related by `GL_4(Z)` and any conjugate
  representation induced by an explicitly supplied curve-model isomorphism is
  accepted, provided evaluation transports through that isomorphism.  The
  verifier checks rank, closure/multiplication data, and agreement of the
  represented maps on its declared verification domain.
- **Conditional dependencies.** The corpus records a polynomial-expected-time
  EndRing/isogeny-path equivalence under GRH (`KN-LIT-074`).  That paper's full
  primary text was not part of this four-paper intake, so this note does not
  use the equivalence as a proved reduction.  Any later invocation must state
  its direction, representation conversion, distribution preservation, GRH
  condition, and whether KLPT-style prime sampling is heuristic or rigorous in
  the invoked result.

The `-eval` suffix matters.  A PKE reduction must end at the same computational
object its decryption mechanism consumes; silently switching between an
abstract order, an oriented order, a path, and evaluable rational maps is an
unresolved reduction gap.

## First security-game target

The first target is **OW-CPA**, before IND-CPA:

1. The challenger runs the candidate's declared `KeyGen` and gives `pk` and
   public parameters to the adversary.
2. It samples `m` uniformly from the candidate's declared message space and
   fresh encryption randomness, then gives `c* = Encrypt(pk, m; r)`.
3. The adversary outputs `m'` and wins iff `m' = m`.
4. Report success and advantage above the forced guessing baseline
   `1 / |M|`; the message distribution and malformed/failure behavior are part
   of the game.

The reduction obligation is directional: an OW-CPA inverter must be converted
to an algorithm for the exact `EndRing-eval(D)` contract above, or the proposal
must name the intermediate assumption and leave the gap visible.  Correctness
of `Decrypt(sk, Encrypt(pk,m))` is a separate obligation.  IND-CPA is deferred
until a randomized, complete candidate has a checked syntax and an auditable
OW interface; no implication from OW-CPA to IND-CPA is assumed.

## Normalized non-duplication boundaries

- A generalized CGL-walk ciphertext with torsion-image trapdoor inversion is a
  SÉTA-family mechanism unless a proposal identifies a mathematical interface
  change, not merely new notation or parameters.
- A commutative hidden action on public curve/point pairs with message masking
  is a SiGamal/C-SiGamal-family mechanism and inherits the need to account for
  P-CSSCDH/P-CSSDDH-like data.
- A key-update wrapper or group-action/DEM hybrid is UPKE prior art; update
  functionality does not create a plain-EndRing reduction.
- A dimension-two Kani/LIT square with public torsion bases, images, or matrices
  is LIT-SiGamal-family prior art and must name its LIT-DDH-style interface.
- FESTA, PIKE, POKÉ, SHealS/HealS, INKE, and FESTA-derived UPKE records in the
  corpus are additional comparison boundaries.  Their presence is not treated
  as primary-source verification in this intake.

## Decision gate after ideation

A mechanism may advance only if its proposal supplies all four items below:

1. complete sender-side public evaluation and recipient-side secret inversion
   types;
2. a correctness invariant that does not let encryption consume the secret
   EndRing witness;
3. a directional OW-CPA-to-`EndRing-eval(D)` reduction outline, or an
   explicitly separated intermediate assumption and gap; and
4. a normalized comparison against the four families above.

Failing this gate retains the proposal as a useful barrier or definition test;
it does not authorize a hypothesis, experiment, implementation, or security
claim.
