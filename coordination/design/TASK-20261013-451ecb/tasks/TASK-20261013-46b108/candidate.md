# EigenX-v3 Ring-Witness CCA PKE

Task: `TASK-20261013-46b108`  
Batch: `BATCH-5313dc`  
Goal: `GOAL-SSI-2fa82a`  
Question: `RQ-SSI-1946c9`

Status: **one fully typed conditional candidate; not an EndRing-only or practical
construction**. This artifact reports zero scientific, implementation,
formalizer, benchmark, and parameter-selection runs. It changes no ledger
status.

## 1. Result and boundary

This packet specifies exactly one candidate, **EigenX-v3-RW-NY-PKE**. Its
recipient operation is genuinely different from the rejected EigenX-v2
torsion-action mechanism: the core decryptor takes an accepted witness for the
NP relation `R_CER`, and every accepted `R_CER` witness is a complete,
saturated, efficiently evaluable rank-four basis of `End(E)`. A path, one
endomorphism, a finite torsion image, an abstract quaternion order, or any
strict suborder fails the relation.

The construction is nevertheless only conditional. It needs a new primitive,
**external-instance distributional extractable witness encryption**
(`EI-DXWE[R_CER,D_ER]`), plus a strong unbounded-simulation-sound NIZK. These
are separate assumptions. Ordinary witness-encryption soundness protects false
statements only; every honest public key here is a true statement. Bellare--
Hoang adaptive `XS` does not provide the uniform externally supplied challenge
interface needed by an EndRing solver. General auxiliary-input extractable WE
also has a published conditional implausibility result. None of these extra
assumptions is renamed EndRing hardness.

There is also an unresolved honest-generation obligation `K0`: no inspected
source constructs the exact efficient sampler that jointly outputs a
distribution-appropriate curve and the complete *evaluable* certificate used
below. Consequently this is a candidate with conditional functionality and a
correctly directed *conditional* reduction, not a secure scheme ready for
implementation.

## 2. Parameters, encodings, and the complete-ring relation

Let `lambda` be the security parameter, `p=p(lambda)>3` a prime with
`log2(p)=poly(lambda)`, and
`F_(p^2)=F_p[u]/g(u)` a fixed canonical representation. Public parameter bytes
fix the field polynomial, canonical curve model and point encodings, the map-
circuit grammar below, the fixed message length `mu(lambda)`, and polynomial
bounds `s_map(lambda)` and `b_deg(lambda)` on a certificate's size and on the
bit length of every syntactic degree bound.

All integers are minimally encoded signed big-endian values; field elements
are fixed-width reduced coefficients; curves and points have one canonical
encoding; lists and tuples use a versioned tag and fixed-width length prefixes.
Parsers reject nonminimal integers, noncanonical field/curve/point encodings,
duplicate fields, inconsistent lengths, trailing bytes, and inputs exceeding
the public polynomial length cap. Mathematical ciphertext equality is exact
byte equality.

### 2.1 Typed map circuits

A map circuit is a directed acyclic circuit with source and target curves on
every wire. Permitted gates are:

1. identity, negation, and binary scalar multiplication;
2. a normalized explicit isomorphism with its inverse;
3. a separable prime-degree isogeny with a certified kernel and normalized
   Velu output, where the prime and all explicitly represented extension
   degrees are polynomially bounded;
4. relative or absolute Frobenius with its source and coefficient-conjugate
   target written explicitly and a typed Verschiebung/dual descriptor;
5. composition of typed maps;
6. pointwise addition/subtraction of two maps with identical source and target.

The evaluator executes this grammar on points over a stated finite extension.
The grammar derives a dual circuit and a conservative integer upper bound
`DegUB(C)` recursively. For composition, bounds multiply; for addition,
`DegUB(A+B)=(ceil_sqrt(DegUB(A))+ceil_sqrt(DegUB(B)))^2`; identity,
scalars, Frobenius, isomorphisms and certified isogenies have their standard
bounds. Circuit size and `log DegUB` must meet the public bounds. An arbitrary
program or an abstract quaternion element is not a map circuit.

### 2.2 The torsion equality certificate

For a finite collection `Q` of asserted equalities `A_j=B_j`, let

```text
B_Q = max_j (ceil_sqrt(DegUB(A_j)) + ceil_sqrt(DegUB(B_j)))^2.
```

The verifier deterministically enumerates the first rational primes different
from `p` until their product `N_Q` satisfies `N_Q^2 > B_Q`. The witness gives,
for each such prime `ell`, an irreducible extension-field polynomial and two
canonical points `(P_ell,Q_ell)` on `E` of exact order `ell` whose Weil pairing
has exact order `ell`. The verifier checks the field certificate, curve
membership, exact orders, independence, and every equality in `Q` on both
basis points. The prime list is polynomial in `log B_Q`; each prime and the
needed extension degree are polynomially bounded. Their complete coordinates,
all equality evaluations, and all extension arithmetic are charged to witness
size and verification cost.

**Equality lemma.** If `A` and `B` are typed endomorphisms and agree on all
these bases, `delta=A-B` kills `E[N_Q]`. If `delta` were nonzero, the prime-to-
`p` subgroup `E[N_Q]` would force `N_Q^2 | deg(delta)`, while
`deg(delta)<=B_Q<N_Q^2`, a contradiction. Thus `A=B`. This suite is only a
certificate verifier; it is not decryption advice and is not published in the
public key.

### 2.3 Relation `R_CER`

The instance is

```text
x = CER-v1 || pp_curve || Enc(E),
```

where `E/F_(p^2)` is a canonical curve. A witness is

```text
W = (C_0,C_1,C_2,C_3, d_0,...,d_3,
     t_ij for 0<=i,j<4, a_ijk for 0<=i,j,k<4,
     torsion equality suite and certificates).
```

`C_i` are typed map circuits `E -> E`; `d_i` are claimed degrees; `t_ij`
are claimed reduced traces of `C_i compose C_j`; and `a_ijk` are integral
multiplication constants. Define `Verify_CER(x,W)` as follows.

1. Parse canonically; verify `p`, the field, and `E`. Run a deterministic
   polynomial-time point-counting/supersingularity check (`p` divides the
   Frobenius trace over `F_(p^2)`) and reject exceptional malformed models.
2. Type-check every circuit, size and degree bound. Require `C_0=id_E`.
3. Add to `Q` the norm equalities
   `dual(C_i) compose C_i = [d_i]`, with `d_i>=0`. This proves the claimed
   degrees rather than trusting metadata.
4. For every ordered pair `(i,j)`, add the closure equality
   `C_i compose C_j = sum_k [a_ijk] C_k`, and the trace equality
   `(C_i compose C_j)+dual(C_i compose C_j)=[t_ij]`. The pairs with
   `j=0` also certify the individual traces.
5. Verify the complete small-prime torsion suite for `Q` using Section 2.2.
6. Form the integer trace matrix `T=(t_ij)`. Require rank four over `Q` and
   `abs(det(T))=p^2`.
7. Accept exactly if every check accepts.

Steps 3--5 prove that the generated lattice
`O=sum_i Z C_i` is a unitary rank-four subring of `End(E)`. For a
supersingular `E`, `End(E)` is a maximal order in the quaternion algebra
ramified at `{p,infinity}`, and its order discriminant has absolute value
`p^2`. Since

```text
disc(O) = [End(E):O]^2 disc(End(E)) = p^2,
```

the index is one. Therefore `O=End(E)`. This is the saturation/maximality
certificate; no independent assertion of saturation is trusted.

The verifier is polynomial in the encoded instance and witness lengths under
the fixed circuit and torsion-suite bounds. The relation deliberately accepts
different bases of the same complete ring. Its solution representation is any
accepted basis and its checked evaluators, not a canonical basis.

## 3. Honest key generation: exact conditional interface `K0`

`TrapRingGen(pp)` must output `(x,W)` distributed as `D_ER(pp)` and
satisfy:

- `Verify_CER(x,W)=1` except with probability `delta_K0(lambda)`;
- expected polynomial time, with an explicit polynomial retry cap and
  `delta_K0` negligible;
- the public marginal of `x` exactly equals the declared EndRing challenge
  distribution `D_ER(pp)`; and
- after constructing `W`, it erases every path, ideal, orientation, kernel,
  sampler seed, division transcript, and alternative ring representation not
  explicitly included in `W`.

A plausible but **unproved** route is to start from a fixed curve with known
maximal order, sample a smooth-norm quaternion ideal and its isogeny, compute
the ideal's right order, conjugate its basis to the target curve, and use the
polynomial `Divide` operation of Page--Wesolowski Proposition 2.3 to obtain
typed target endomorphism circuits. The missing certificate is an end-to-end
polynomial algorithm proving that the sampled ideal/isogeny law, every rational
denominator division, the resulting succinct circuits, and `Verify_CER` all
match `D_ER` with the stated tail and erasure. This is obligation `K0`; it is
not assumed to follow merely from the existence of `End(E)`.

## 4. The separate core primitive: external-instance DXWE

`EI-DXWE` has algorithms

```text
ep <- DX.Setup(pp; rho)
c  <- DX.Enc(ep, x, m; r)
m' <- DX.Dec(ep, x, W, c)
```

with canonical encodings, fixed `mu(lambda)`-bit messages, deterministic
decryption/rejection, and correctness for every `Verify_CER(x,W)=1`.

Its required security property is relation- and distribution-specific. For
every uniform PPT distinguisher `D` in the externally supplied-instance game,
there is a uniform PPT extractor transformation `Ext[D]` such that, on the
*same* externally supplied `x` and allowed auxiliary string `aux`,

```text
Adv_DX(D; x,aux) <= L_X(lambda) *
  Pr[Verify_CER(x, Ext[D](1^lambda,ep,x,aux))=1] + nu_X(lambda).
```

Here `L_X` is an explicit polynomial and `nu_X` negligible. The probability
space samples `(x,W0)<-D_ER`, discards `W0`, independently samples the real or
simulated public setup used by the reduction, and supplies the exact
scheme-generated auxiliary distribution. `Ext[D]` receives no `W0`, path,
ideal, orientation, ring advice, sampler trapdoor, NIZK simulation trapdoor, or
nonuniform advice depending on the particular `x`. It must work uniformly
when an EndRing challenger supplies `x`; it may use the code and black-box
invocations of `D` as its definition states. Both the real-CRS and simulated-
CRS auxiliary distributions used in Section 7 must be covered.

This is stronger than ordinary WE, AS-WE, or the adaptive XS game as used in
the inspected source. It is also deliberately narrower than general auxiliary-
input EWE: only the exact `R_CER`, `D_ER`, and listed auxiliary distributions
are assumed.

### Conditional obfuscation realization

For each `(x,m)`, define a circuit

```text
F_(x,m)(w): if Verify_CER(x,w)=1 return m; else return bottom.
```

If an externally instantiable, relation-specific extractable differing-input
obfuscator is secure for pairs `(F_(x,m0),F_(x,m1))` under the exact auxiliary
distribution above, set `DX.Enc` to an obfuscation of `F_(x,m)` and `DX.Dec` to
evaluate it on `W`. Any distinguishing input is then an accepted `R_CER`
witness. This implication is syntactically sound, but the required xO itself is
a strong, uninstantiated assumption. The Garg--Gentry--Halevi--Wichs result
conditionally rules out *general-purpose* auxiliary-input EWE; it does not
prove this specific family impossible, and it prevents presenting the route as
a routine or standard realization.

## 5. Strong unbounded-simulation-sound NIZK

Let `N=(N.Setup,N.Prove,N.Verify,N.SimSetup,N.SimProve)` be a CRS NIZK for the
NP language `L_EQ` below. It must have perfect or quantified completeness,
adaptive multi-theorem zero knowledge, and **strong unbounded simulation
soundness**: after polynomially many adaptively selected simulated proofs, no
PPT adversary can create a new accepting proof for any false statement,
including a different proof for a previously simulated false statement.
“Unbounded” refers to no fixed a-priori bound on the polynomial number of
simulation queries, not an unbounded adversary.

For canonical `pk` bytes, the equality language is

```text
y=(pk_bytes,c_0,c_1) in L_EQ iff there exist (m,r_0,r_1) such that
  |m|=mu(lambda),
  c_0=DX.Enc(ep_0,x_0,m;r_0), and
  c_1=DX.Enc(ep_1,x_1,m;r_1),
```

where `(x_0,ep_0,x_1,ep_1,crs)` is parsed from exactly `pk_bytes`. Equality of core
ciphertexts is exact canonical byte equality. The proof binds the complete
public key, message length, and both component bytes.

## 6. EigenX-v3-RW-NY-PKE algorithms

### `Setup(1^lambda)`

Deterministically generate or validate and return
`pp=Frame("EX3-PP",version,p,g,curve_grammar,map_grammar,s_map,b_deg,mu,
algorithm_ids)`. If parameter validation fails, return `bottom`. There is no
secret global trapdoor and no hidden setup output.

### `KeyGen(pp)`

1. Parse and validate `pp`. Independently run
   `(x_i,W_i)<-TrapRingGen(pp)` for `i=0,1`. If a
   capped sampler fails or `Verify_CER(x_i,W_i)=0`, return key-generation
   failure. The two independent EndRing instances are the two core public
   keys needed by the Naor--Yung simulation.
2. Independently sample `ep_i<-DX.Setup(pp;rho_i)` for `i=0,1`.
3. Sample `crs<-N.Setup(pp;sigma)`.
4. Set
   `pk=Frame("EX3-PK",version,x_0,ep_0,x_1,ep_1,crs)` and
   `sk=Frame("EX3-SK",version,pk_bytes,W_0,W_1)`.
5. Erase `rho_0,rho_1,sigma` and every `TrapRingGen` auxiliary value required
   by `K0`'s erasure contract. Return `(pk,sk)`.

### `Enc(pk,m)`

1. Canonically parse and validate `pk`; require `|m|=mu(lambda)`, else return
   `bottom` and no ciphertext.
2. Draw independent uniform coins `r_0,r_1` from the core domains and compute
   `c_i=DX.Enc(ep_i,x_i,m;r_i)`. If either core encryption fails, return `bottom`.
3. Let `y=(pk_bytes,c_0,c_1)` and
   `omega=(m,r_0,r_1)`. Draw fresh prover coins and compute
   `pi=N.Prove(crs,y,omega)`.
4. Return `Frame("EX3-CT",version,pk_bytes,c_0,c_1,pi)`. Embedding `pk_bytes`
   prevents cross-key substitution; an implementation may replace it by a
   collision-resistant digest only under an additional named assumption.

### `Dec(sk,c)`

1. Parse `sk`, reparse the embedded canonical `pk`, and require
   `Verify_CER(x_i,W_i)=1` for both `i`. Parse `c` under the public polynomial
   length cap.
2. Require the ciphertext's embedded `pk_bytes` to equal the secret key's
   exact bytes and `N.Verify(crs,(pk_bytes,c_0,c_1),pi)=1`. Otherwise return
   `bottom`.
3. Compute `m_i=DX.Dec(ep_i,x_i,W_i,c_i)` for both components. If either is
   `bottom`, has the wrong length, or `m_0 != m_1` byte-for-byte, return
   `bottom`; otherwise return `m_0`.

Every branch is deterministic after the secret key and ciphertext are fixed.
The formal model exposes only `m` or the single symbol `bottom`; timing,
allocation, power, cache, fault, and erasure side channels are excluded.

## 7. Correctness and classical IND-CCA2 theorem

Let `epsilon_DX` bound each core correctness error, `epsilon_N` NIZK
completeness error, and `delta_K0` the probability that capped KeyGen does not
return a valid key. For every `mu(lambda)`-bit message,

```text
Pr[Dec(sk,Enc(pk,m))=m] >=
  1 - 2 delta_K0 - 2 epsilon_DX - epsilon_N.
```

For every returned valid key the conditional bound omits `2 delta_K0`. It is
perfect if the three primitives are perfect and `TrapRingGen` returns a key.
This recovers the actual selected message, not an invariant or orbit.

The IND-CCA2 game gives a classical PPT adversary the canonical `pk`, accepts
two equal-length messages in the fixed message space, returns an encryption of
one, and answers adaptive decryption queries before and after challenge except
the **exact challenge ciphertext bytes**. No endpoint or component-equivalence
class is excluded.

Under the standard Naor--Yung hybrids, for constructed algorithms
`D_0,D_1,S_0,S_1,F` with comparable polynomial running time and at most the
adversary's `q_D` decryption queries,

```text
Adv_IND-CCA2_EX3(A)
 <= Adv_EI-DXWE(D_0) + Adv_EI-DXWE(D_1)
    + Adv_ZK(S_0) + Adv_ZK(S_1)
    + Adv_sUSS(F).
```

The idealized canonical parser and validators are deterministic, so their
proof error is zero; any probabilistic or implementation-level validation
would add its own separately measured `q_D*epsilon_parse` term.

Strong unbounded simulation soundness is used to reject a fresh accepting
proof for a false equality statement, including alternate proof bytes for the
simulated challenge statement. Canonical framing and full-key binding make the
challenge exclusion exact. A decryption query with a true equality statement
can be answered with the independently sampled other component's witness in
the relevant hybrid; a false statement is rejected except with the `sUSS`
advantage. This is why one curve with two setup strings would be insufficient
for the standard simulation: the reduction would know no witness for either
component.

Applying the external-instance extractors on the **same** challenge `x_i` gives
EndRing solvers `B_0,B_1` and the conditional bound

```text
Adv_IND-CCA2_EX3(A)
 <= L_X(lambda)*(Succ_EndRing(B_0)+Succ_EndRing(B_1))
    + 2 nu_X(lambda) + Adv_ZK(S_0)+Adv_ZK(S_1)
    + Adv_sUSS(F).
```

Each `B_i` receives an external `x_i<-D_ER`, samples the other independent
pair `(x_(1-i),W_(1-i))<-TrapRingGen`, samples public DXWE/NIZK parameters,
embeds the exact external `x_i`, answers valid decryption queries using
`W_(1-i)` in the corresponding hybrid, runs uniform `Ext[D_i]`, and outputs
the accepted `R_CER` witness for `x_i`. The independently sampled other
witness is not correlated advice about the challenge. By Section 2, the
extractor output is a complete evaluable saturated rank-four basis of
`End(E_i)`.
This is the requested attacker-to-EndRing direction.

The theorem is conditional on `EI-DXWE` and NIZK properties, not EndRing
alone. No inspected primary source proves this exact generic theorem for this
core, so the displayed hybrid is a proposed proof artifact for independent
review, not a cited reviewed theorem.

## 8. Full-ring necessity and controls

The strongest honest statement supported by the syntax is **witness-level
necessity**: `DX.Dec` accepts the decryption witness only after
`Verify_CER(x,W)`, whose soundness forces `W` to describe all of `End(E)`.
The conditional xO realization likewise differs only on accepted complete-ring
witnesses.

That is not yet a representation lower bound on every possible decoder. A
smaller circuit might reproduce `DX.Dec` without presenting an accepted
witness, and the current assumptions do not rule it out. The extraction
property proves that a successful privacy distinguisher yields a complete
witness; it does not prove that every correct decryption implementation stores
one. Therefore the exact “no strict quotient implements decryption” claim
remains open.

Controls:

| mutation with identical public bytes | required result |
|---|---|
| Give only one endomorphism, a path, finite torsion images, or an abstract order. | `Verify_CER` rejects: rank/closure/evaluator/discriminant checks fail. |
| Give a full-rank strict suborder. | Its discriminant is `[End:O]^2 p^2`, so the `p^2` test rejects. |
| Change to another basis of the same complete ring. | Accept and decrypt identically; the solution is a ring, not canonical basis bytes. |
| Publish `W`. | Everyone decrypts; this is an attack control, not a security proof. |
| Replace `EI-DXWE` with ordinary WE/AS-WE. | Honest `x` is in the language, so secrecy is unsupported. |
| Let the DXWE sampler choose its own `x`. | The external EndRing challenge cannot be embedded; the reduction stops. |
| Supply witness-correlated auxiliary advice to the extractor. | The assumption becomes circular and is rejected. |
| Omit or weaken the equality proof. | Component splicing/malleability reaches the decryption oracle; CCA proof stops. |
| Permit alternate encodings of challenge components/proofs. | Exact-byte exclusion can be bypassed; canonical parsing or strong `sUSS` must stop it. |

## 9. Cost and deployment boundary

Every key charges: `TrapRingGen`, ideal/path and right-order work if used,
all `Divide` calls, eight circuit encodings across two keys, both complete
equality suites and their
verification, two independent DXWE setups, one NIZK CRS, all validation,
serialization, retries, erasure, and peak memory. Encryption charges two DXWE
encryptions plus one NIZK proof; decryption charges parsing, a full
`Verify_CER` (or an equivalently validated cached result), NIZK verification,
two DXWE decryptions, and comparison. Public-key size includes both `x_i`,
both core parameters and CRS. Secret-key size includes both complete evaluable
ring witnesses.
Ciphertext size includes a full public-key binding, two core ciphertexts and a
proof.

No concrete DXWE, xO, or NIZK for this relation is selected; no byte count,
operation count, retry tail, memory measurement, parameter set, implementation,
or practical claim exists. General NP NIZKs/obfuscation would be enormous even
if assumed. Cold-start and amortized costs are therefore symbolic and cannot
support deployment language.

## 10. Classical versus quantum scope

The proposed theorem is classical and in the CRS standard model. A quantum
claim would additionally require: `D_ER` EndRing hardness against QPT
algorithms; a QPT external-instance DXWE distinguisher-to-witness extractor for
the exact quantum auxiliary interface; post-quantum adaptive zero knowledge
and strong unbounded simulation soundness; and a quantum-valid Naor--Yung
hybrid with no unjustified classical rewinding or state cloning. None is
provided. There is no QROM claim.

## 11. Obligation ledger

| obligation | producer status | strongest honest statement |
|---|---|---|
| O1 exact problem/distribution | `open` | `R_CER` and the conditional `D_ER` output law are exact, but efficient real-law sampler `K0` is unresolved. |
| O2 honest algorithms | `open` | Complete conditional syntax and byte grammar exist; `TrapRingGen`, EI-DXWE, and suitable NIZK lack concrete instantiations and total costs. |
| O3 correctness | `proposed_discharge` | Actual-message correctness is quantified by `2 delta_K0+2 epsilon_DX+epsilon_N`, conditional on the named primitives. |
| O4 functionality | `proposed_discharge` | Public DXWE encryption and private complete-witness decryption are typed; strict-decoder-quotient impossibility remains open. |
| O5 directed reduction | `proposed_discharge` | The conditional classical chain is `IND-CCA2 adversary -> EI-DXWE distinguishers -> accepted R_CER witness -> complete EndRing`; all extra assumptions remain separate. |
| O6 adversarial view | `open` | Formal CRS/CCA view, exact exclusion, parsing, malformed rejection and controls are listed; concrete primitive encodings, setup realizations, side channels, multi-user and quantum views remain open. |

No obligation is independently reviewed in this producer artifact.

## 12. Strongest conclusion and next gate

EigenX-v3-RW-NY-PKE is a coherent **conditional full-ring-witness recipient
mechanism**. It escapes the specific finite-torsion factorization of EigenX-v2
and supplies the correct conditional reduction direction. It is not EndRing-
only: `EI-DXWE`, strong unbounded-simulation-sound NIZK, and `K0` are essential
and currently uninstantiated. The first discriminating next step is independent
review of `R_CER` polynomial verification, external-instance extraction and
the Naor--Yung oracle simulation; only a surviving review may decide whether
the candidate advances.

