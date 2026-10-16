# EigenX-v2 prescribed-path KEM: conditional syntax and scoped obstruction

Task: `TASK-20261013-613c4e`

Batch: `BATCH-be2a37`

Goal: `GOAL-SSI-2fa82a`
Question: `RQ-SSI-1946c9`

Status: **scoped construction obstruction, not a secure scheme**. This packet
uses zero scientific, implementation, formalizer, benchmark, or parameter-
selection runs. It specifies exactly one candidate. It neither claims novelty
nor changes any ledger status.

## 1. Result first

The only source-backed way found to make the prescribed-path map both
injective and efficiently invertible is the Séta mechanism: publish the endpoint
of the degree-`D` isogeny together with the images of a full `N`-torsion basis,
under `N^2 > 4D` and the stronger trapdoor-generation conditions. This gives a
well-typed deterministic path PKE and admits the classical-ROM HHK
implicit-rejection KEM transform.

It does **not** give an EndRing-bound EigenX-v2. Séta Section 2.4 states that,
in its concrete `M=1` case, inversion needs only the action of one endomorphism
`theta` on `E[N]`. The strict finite quotient

```text
Q_N = (d, e, theta(P_N), theta(Q_N))
```

reproduces every accepted decapsulation result; a complete evaluable rank-four
basis `W` for `End(E)` is unnecessary. Replacing the torsion images in the
ciphertext by the endpoint alone avoids that exact quotient but loses the only
retrieved injectivity and polynomial inversion arguments. Page--Wesolowski's
`Isogeny <= EndRing` result returns an isogeny of bounded description between
two curves under GRH; it does not recover the sender's exact prescribed-degree
path or kernel.

Thus the candidate has a decisive O4 obstruction:

```text
endpoint only       -> exact path uniqueness/recovery is open;
endpoint + N-action -> Séta inversion works, but Q_N strictly replaces W.
```

This is an obstruction only for the prescribed-path/torsion-binding interface
defined below. It is not an impossibility theorem for every EndRing PKE.

## 2. Typed conditional candidate

Call the one candidate **EigenX-v2-Path-FO-KEM**. The following interfaces are
definitions, not available oracles. Unavailable polynomial algorithms are
listed in Section 7.

### 2.1 Public parameters and canonical objects

For security parameter `lambda`, parameters contain:

- a prime `p`, a fixed canonical representation
  `F_(p^2)=F_p[u]/g(u)`, and a canonical model/encoding function `CanCurve`;
- smooth coprime integers `D,N`, complete public factorizations, and
  `D=prod_i ell_i^e_i`, with `N>D^2`, hence `N^2>4D`;
- a fixed order of the prime factors of `D`, a fixed order of each outgoing
  kernel line, and the Séta nonbacktracking path-code set
  `X_D=prod_i ([ell_i+1] x [ell_i]^(e_i-1))`;
- a key length `kappa(lambda)` and one classical random oracle
  `H_K:{0,1}*->{0,1}^kappa`;
- a version string and domain separators.

Field elements use fixed-width coefficients reduced modulo `p`. Curves use the
unique bytes returned by `CanCurve`; exceptional `j=0,1728` choices must be
fixed in the parameters. Points use a unique compressed encoding including the
sign/root-selection bit and a unique infinity byte. Tuples are length-prefixed.
No alternate encoding is accepted.

For a curve `E`, a public torsion basis `(P_N,Q_N)` is valid exactly when both
points lie on `E`, have exact order `N` (checked using the public factorization),
and their Weil pairing has exact order `N`. The same checks apply to the two
image points on a ciphertext endpoint. Supersingularity and model membership
must be checked by a fixed deterministic verifier or a canonical certificate;
the present packet does not supply that verifier.

A complete witness `W` means a saturated rank-four `Z`-basis of exactly
`End(E)`, multiplication/reduced-trace/reduced-norm data, and polynomial-size
evaluators for every represented basis element and their integer combinations.
An abstract quaternion maximal order without a verified evaluator conversion
is not `W`.

### 2.2 Required key sampler

`TrapCurveGen_ER(1^lambda)` is required to return

```text
(pp, E, W, P_N, Q_N)
```

with `W` complete and evaluable and with a deterministic interface

```text
SelectTrap(E,W,D,N) -> (theta,d,e)
```

such that `theta` is trace zero, the Séta inversion identities and quadratic-
nonresidue conditions hold, and `theta(P_N),theta(Q_N)` are evaluable. Selection
must depend only on the semantic full ring and public parameters, not on an
erased secret path, ideal, orientation, torsion tag, or basis accident.

No retrieved source constructs this exact interface. Séta Algorithm 3 claims
polynomial generation of a curve plus the two needed torsion actions from an
abstract maximal-order computation, but does not output the above complete
evaluator contract. Its alternative secret-walk generator transports the
finite trapdoor, not a certified saturated evaluator basis. Naively transporting
`alpha` along `phi:E0->E` as `phi alpha phi_hat / deg(phi)` creates an integral
division/saturation obligation; an explicit polynomial full-ring transport
algorithm and representation-cost bound were not supplied.

### 2.3 Deterministic path map

For `x in X_D`, `PathEval(pk,x)` follows the canonically ordered,
nonbacktracking prime-degree walks encoded by `x`. Let their composite be
`phi_x:E->E_x`. It returns the canonical bytes

```text
c0 = Encode("EigenX-v2/c0", Hash(pk),
            CanCurve(E_x), phi_x(P_N), phi_x(Q_N)).
```

The relation `R_path(pk,x,c0)` holds exactly when canonical re-evaluation of
`x` is byte-for-byte equal to `c0`. The endpoint and the two torsion images are
public binding data, not hidden advice.

Séta Lemma 3.1 supplies the relevant injectivity argument: if two degree-`D`
isogenies have the same endpoint and the same action on the full `N`-torsion,
then their difference has degree at most `4D` and contains `E[N]` in its
kernel; `N^2>4D` forces equality. This does not prove endpoint-only
injectivity. Indeed, whenever `|X_D|` exceeds the number of canonical target
vertices, endpoint collisions follow by pigeonhole, and even below that
threshold no retrieved theorem gives the required per-key uniqueness.

### 2.4 Internal deterministic path PKE

Define `PathPKE=(KeyGen0,Enc0,Dec0)` with message space `X_D`:

```text
KeyGen0(1^lambda):
  (pp,E,W,P_N,Q_N) <- TrapCurveGen_ER(1^lambda)
  (theta,d,e)      <- SelectTrap(E,W,D,N)
  validate every public object and the trapdoor equations
  pk <- Encode(pp,E,P_N,Q_N)
  sk0 <- (pk,W)
  return (pk,sk0)

Enc0(pk,x):
  require canonical valid pk and x in X_D
  return PathEval(pk,x)

Dec0(sk0,c0):
  parse and validate pk and c0 canonically
  (theta,d,e) <- SelectTrap(E,W,D,N)
  derive theta(P_N),theta(Q_N) by evaluating W
  run the Séta recovery equations on
       (E,P_N,Q_N,E_c,phi_x(P_N),phi_x(Q_N))
  recover ker(phi_x), then the unique canonical x in X_D
  return x only if PathEval(pk,x) equals the received c0 byte for byte
  otherwise return bottom
```

The internal re-encryption check is semantic only through canonical bytes; the
IND-CCA challenge exclusion below is also exact byte equality, not endpoint
equality. `Dec0` is not public and its `bottom` is never exposed by the KEM.

### 2.5 Active KEM with uniform implicit rejection

This is exactly the HHK `U^not-bottom` pattern of Theorem 4 applied to the
deterministic `PathPKE`. `z` is an independent uniform member of `X_D` used
only for implicit rejection.

```text
KeyGen(1^lambda):
  (pk,sk0) <- KeyGen0(1^lambda)
  z <-$ X_D
  return (pk, sk=(sk0,z))

Encaps(pk):
  validate pk
  x <-$ X_D                         # exact uniform rejection sampling
  c0 <- Enc0(pk,x)
  K <- H_K(Encode("EigenX-v2/K",Hash(pk),c0,x))
  return (c0,K)

Decaps(sk,c_bytes):
  parse c_bytes canonically; on any error set x_prime=bottom
  otherwise x_prime <- Dec0(sk0,c_bytes)
  if x_prime != bottom and Enc0(pk,x_prime) is byte-equal to c_bytes:
      return H_K(Encode("EigenX-v2/K",Hash(pk),c_bytes,x_prime))
  else:
      return H_K(Encode("EigenX-v2/K",Hash(pk),c_bytes,z))
```

The mathematical API always returns `kappa` bits. Parse, validation, recovery,
and re-encryption should be implemented without a distinguishable failure path;
constant-time and fault-resistant implementation are not established here.
Malformed bytes are included length-delimited in the rejection hash. A wrong-
key ciphertext has the wrong `Hash(pk)` or fails re-encryption and takes the
same implicit-rejection branch.

### 2.6 Exact KEM game and conditional theorem

The target is single-user classical IND-CCA2 in the classical ROM. Generate
`(pk,sk)`, obtain `(c*,K0)<-Encaps(pk)`, sample uniform
`K1<-{0,1}^kappa` and `b<-{0,1}`, and give `(pk,c*,K_b)` to a PPT adversary.
It has adaptive classical `H_K` access and `Decaps(sk,.)` access before and
after the challenge, except on the exact byte string `c*`. Its advantage is
`abs(Pr[b'=b]-1/2)`.

HHK Theorem 4 applies only if `PathPKE` is `delta_1`-correct and OW-PCA
secure for the exact real key/message/ciphertext distribution. For at most
`q_D` decapsulation and `q_H` hash queries it gives an OW-PCA adversary `A`
of approximately the same running time and the bound

```text
Adv_IND-CCA_KEM(B) <= q_H / |X_D| + Adv_OW-PCA_PathPKE(A).
```

KEM correctness error remains `delta_1`. The source does not turn
`OW-PCA_PathPKE` into EndRing. For this deterministic public map, plaintext
checking can already be performed by re-evaluation, but one-wayness is still a
TCSSI/path-inversion-type assumption on the exact auxiliary-data distribution.

Random-oracle programming in the HHK simulator maintains a list for
`H_K(c,x)`. Decapsulation queries initially receive a random key indexed by
`c`; a later hash query is patched when the plaintext-checking oracle confirms
`x` for `c`. The challenge is hidden unless the adversary queries its
`(c*,x*)` pair; guessing contributes `q_H/|X_D|`. These are the exact
simulation resources; no quantum or QROM claim is made.

### 2.7 Optional KEM--DEM PKE syntax

One may define `Enc(pk,m,aad)` by encapsulating `(c0,K)` and returning
`(c0, DEM.Enc(K,m; aad||Hash(pk)||c0))`, with `Dec` first running `Decaps` and
then authenticated DEM decryption. Ciphertext equality is equality of the full
canonical pair. This packet does not select or inspect an exact DEM composition
theorem and therefore makes no PKE security claim for this optional syntax.
The scoped KEM obstruction already decides the batch candidate.

## 3. Correctness and failure accounting

For every accepted key and every `x in X_D`, assume `SelectTrap` returns the
same `(theta,d,e)` used by generation, Séta recovery terminates, and all
canonical encoders are correct. Lemma 3.1 gives uniqueness and Algorithm 1
recovers `ker(phi_x)` and hence `x`; re-evaluation returns the identical bytes.
Both parties query `H_K` on the same string, so

```text
Pr[Decaps(sk,c0) != K | (c0,K)<-Encaps(pk)] = 0
```

conditional on an accepted valid key and the required interfaces. The
unconditional error is bounded by

```text
epsilon_KG + epsilon_Select + epsilon_Recovery + epsilon_Encoding,
```

but none of these terms has a distribution-matched bound for
`TrapCurveGen_ER`. Therefore correctness is only a proposed conditional
discharge, not a completed O2/O3 theorem. Invalid ciphertexts yield an
implicit random-oracle key rather than `bottom`; guessing the secret rejection
seed is covered by the transform's finite-message-space term.

## 4. Why complete EndRing is not necessary

Let

```text
Compress_N(W)=(d,e,theta(P_N),theta(Q_N)).
```

Every step after key generation in `Dec0` uses only `Compress_N(W)`, public
data, and ciphertext torsion images. Séta Section 2.4 explicitly explains that
when its parameter `M=1`, only the action of `theta` on `E[N]` is needed to
compute the relevant kernels. Its Algorithm 1 then recovers the secret isogeny.
Consequently two full witnesses with the same `Compress_N` value, or a full
witness and that quotient alone, have identical accepted decapsulation
behavior.

This is stronger than merely observing that one endomorphism suffices: only a
finite torsion action of that element is consumed. No reduction from this
quotient to a saturated evaluable rank-four basis is supplied. Giving the
public sender `Compress_N(W)` would give it the same recovery operation and
destroy recipient asymmetry. Keeping it secret yields a Séta/TCSSI trapdoor,
not an EndRing-only mechanism.

## 5. Reduction boundary

The only complete conditional reduction is

```text
OW-PCA_PathPKE + HHK classical ROM -> IND-CCA EigenX-v2-Path-FO-KEM.
```

The desired arrow is absent:

```text
input:  exact complete-EndRing challenge E on the real KeyGen law
use:    successful IND-CCA attacker on the complete KEM view
output: saturated efficiently evaluable rank-four basis of End(E).
```

An attacker that recovers `x` solves a path/TCSSI instance. It does not reveal
`theta`, `Compress_N(W)`, or a full ring. Conversely, a supplied full ring may
be sufficient to derive a trap action or, under Page--Wesolowski Proposition
8.4 and GRH, to solve a bounded Isogeny instance. Both are attack directions
from EndRing knowledge to path recovery, not extraction of EndRing from a
scheme attacker. Page--Wesolowski Theorem 8.5 has the other problem-reduction
direction, `EndRing <= Isogeny`; neither statement supplies exact sender-path
recovery or the required scheme-attacker extractor.

## 6. Complete adversarial view and controls

The view contains `p`, field/model grammars, `D,N` and factorizations, every
path ordering rule, `E,P_N,Q_N`, public validation algorithms, both random-
oracle domain separators, every endpoint and two torsion images, exact raw
ciphertext bytes, every decapsulation answer except the exact challenge bytes,
and all timing/fault behavior if implementation security is later claimed.

Required controls and their disposition:

| Control | Exact mutation | Result in this packet |
| --- | --- | --- |
| Endpoint-only | Remove both torsion images. | No retrieved injectivity or polynomial exact-recovery theorem; collisions are forced when paths outnumber endpoints. |
| Finite quotient | Replace `W` by `Compress_N(W)`. | All accepted decapsulation behavior is unchanged; O4 is contradicted for this interface. |
| One evaluator | Retain only `theta` plus its evaluator. | More than sufficient; finite `N`-action already suffices. |
| Public recovery | Give `Compress_N(W)` to the sender/public. | The public can run the recipient recovery, so confidentiality/asymmetry fails. |
| Witness variation | Change the rank-four basis while preserving the selected torsion action. | Ciphertexts and decapsulation are unchanged; the observable does not identify the full ring. |
| Prescribed degree | Ask Page--Wesolowski's Isogeny solver for exactly `phi_x` of degree `D`. | Source theorem returns some bounded isogeny, not this exact path/kernel. |
| Dual/backtracking | Permit an immediate dual edge. | Produces a scalar multiplication component; canonical path grammar excludes it. |
| Malformed/alternate | Noncanonical field/point/curve, wrong order, wrong basis, infinity, wrong key, truncated/extended bytes. | Always take implicit rejection; no endpoint-equivalence exclusion. |
| CCA related | Modify any byte of `c*`, including a torsion image. | Query is permitted; re-encryption must fail or recover a matching different path. The output remains a pseudorandom implicit-rejection key. |
| Reverse arrow | Supply `W` and decrypt. | An attack route only; it is not an EndRing security reduction. |
| Known-false proof | Apply the EndRing argument to a secret finite lookup table implementing `Compress_N`. | Functionality still works while no full ring exists; any proof that still extracts a ring proves too much. |

Side channels, fault attacks, multi-user security, QPT/QROM adversaries, concrete
parameters, and malicious parameter generation are outside the claim and remain
open.

## 7. Algorithm and cost obligations

| Component | Required cost | Current status |
| --- | --- | --- |
| Curve/ring generation | Expected polynomial time with tail bound; complete evaluator bytes and saturation certificate. | Open. Séta's finite trapdoor generator is not the exact interface. |
| Full-ring transport | Construction, integral division/saturation, evaluator conversion, memory. | Open; no source-backed algorithm in the inspected packet. |
| Trap selection | Semantic-witness-independent `(theta,d,e)` selection and failure mass. | Open. |
| Encapsulation | `sum_i e_i` small-degree isogeny steps, two torsion-point transports, canonicalization, one hash. | Symbolically typed; no measured or concrete cost. |
| Decapsulation | Séta kernel recovery, smooth-order double-discrete-log work, degree-`N` evaluations, path decoding, re-encryption, one hash. | Source claims polynomial under its conditions; exact bit/operation/memory bounds for this key law are open. |
| Ciphertext | One endpoint, two `N`-torsion points, version/key binding and lengths. | Exact bit count depends on the unchosen field/point grammar. |
| Rejection | Full parse/validation/recovery schedule plus one hash. | Mathematical output is uniform-looking; constant-time implementation unbuilt. |

Cold-start cost includes parameter generation, curve/maximal-order translation,
complete-ring evaluator construction, selection, and validation. Only fixed
public parameters and hash setup are potentially reusable across keys; no
per-key trapdoor cost is amortized without an explicit workload count. There
are no measured costs in this zero-run task.

## 8. O1--O6 statuses

| Obligation | Status | Reason |
| --- | --- | --- |
| O1 exact hard problem | `open` | `OW-PCA_PathPKE` can be defined on the real law, but that law depends on unavailable `TrapCurveGen_ER`; it is a TCSSI/path assumption, not reduced to bare EndRing. |
| O2 honest algorithms | `open` | KEM syntax, bytes, validation and rejection are complete conditional interfaces; complete-ring generation/transport/selection and their costs are missing. |
| O3 quantified correctness | `proposed_discharge` | Conditional on accepted valid interfaces, Séta injectivity/recovery and byte re-encryption give zero error. Key-generation and interface failure probabilities remain unbounded. |
| O4 recipient mechanism | `contradicted` | The exact recipient operation factors through `Compress_N(W)`, a strict one-endomorphism finite-torsion quotient. |
| O5 correct-direction reduction | `open` | HHK reduces the KEM to path OW-PCA only. No IND-CCA-attacker-to-complete-EndRing extractor exists. |
| O6 complete view | `open` | The formal classical-ROM view is listed, but concrete encodings, side channels, multi-user/QROM scope and source-complete overlap remain open. |

No status is independently reviewed. In particular, `proposed_discharge` is
not `reviewed_discharge`.

## 9. Prior-art position and narrow conclusion

`dominated_by`: Séta Sections 2.4 and 3 already give the finite-torsion
trapdoor function, injectivity condition, inversion algorithm, OW-CPA PKE and
an OAEP active-security route. EigenX-v2 adds an unused complete-ring witness
and swaps in the HHK classical-ROM KEM shell.

`sota_delta`: no positive theorem or efficiency improvement. The packet adds a
typed modern KEM syntax and identifies the strict quotient, but it proves no
new hardness or security result.

SiGamal/C-SiGamal use a commutative isogeny action and an auxiliary point under
P-CSSDDH; their paper explicitly records CCA malleability. The inspected
supersingular UPKE uses SIDH/CSIDH update actions and hybrid encryption, not
complete-EndRing path inversion. LIT-SiGamal's retrieved abstract describes a
commutative LIT diagram with horizontal and vertical isogenies; its full-text
comparison is blocked. Exact provenance and limits are in
`source-overlap.yaml`.

The narrow conclusion is: **EigenX-v2-Path-FO-KEM is not admitted as an
EndRing-secure construction.** Resolving the sampler and selecting concrete
parameters would not fix O4. To revisit this exact interface, one needs either
(a) endpoint-only exact-path injectivity and a polynomial full-ring recovery
algorithm that provably cannot be replaced by a strict quotient, or (b) a
reduction from the finite torsion-action quotient to a complete evaluable
`End(E)` basis on the exact real-key law, followed by the correctly directed
IND-CCA-to-EndRing proof. Neither is supplied by the inspected sources.
