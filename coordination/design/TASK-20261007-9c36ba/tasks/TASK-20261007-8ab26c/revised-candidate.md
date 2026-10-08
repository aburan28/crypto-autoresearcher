# Gap-fed revision: RWCT-PKE scoped obstruction packet

Task: `TASK-20261007-8ab26c`  
Goal: `GOAL-SSI-2fa82a`  
Question: `RQ-SSI-1946c9`  
Batch: `BATCH-65c2dd`

## Claim boundary and outcome

This packet attempts a materially different repair of the single-evaluator
construction in the frozen gap packet.  Instead of using one hidden
endomorphism, it compiles noncommutative words in all four elements of a
complete evaluable basis of `End(E)` and uses every compiled word in each
ciphertext.  The resulting **ring-word compiled transfer PKE** (`RWCT-PKE`) has
an exact selected-message correctness identity for valid keys.

It does **not** yield an EndRing-based security claim.  The attempt exposes a
scoped obstruction for the polynomial-size compiled-word family:

1. decryption factors through a finite tuple of restricted word evaluators,
   so its transcript does not functionally require a complete ring;
2. a bare curve-only EndRing challenge does not let a reduction sample the
   real public key; and
3. an arbitrary valid EndRing output is not aligned with the planted basis
   used by the public word descriptors.

The missing maps are named below.  No experiment was run, no primary source
was read in this task, and no security, novelty, deployability, or universal
impossibility claim is made.  `novelty_status: unverified`.

## Exact attempted family

Let `lambda` be the security parameter and `L=L(lambda)` the selected-message
length.  Public parameters specify:

- a finite field and canonical encodings for supersingular curves and points;
- a polynomial number `t=t(lambda)` of transfer slots and a polynomial
  straight-line-program bound `d=d(lambda)`;
- a random oracle
  `H_RWCT : {0,1}* -> {0,1}^L`, with domain separator `RWCT-PKE-v1`;
- a joint key distribution `D_pair(lambda)` over `(E,B)`, where
  `B=(beta_1,...,beta_4)` is an ordered, complete, evaluable `Z`-basis of
  `End(E)`; and
- prime torsion orders `N_j` for which exact-order points used below have
  canonical encodings.

`D_pair` is part of the attempted family, not an available theorem or
implemented sampler.  Its curve marginal is denoted `D_curve(lambda)`.

A ring word is a noncommutative straight-line program over variables
`X_1,...,X_4`, integer scalar multiplication, addition, negation, and
composition.  Every word used by this attempt contains every variable at
least once and has at most `d` operations.  For a valid secret basis `B`,
`w(B)` denotes the resulting evaluable endomorphism.

### `Setup(1^lambda)`

Return the parameter record above, including `L,t,d`, canonical encoders, the
admissible torsion-order rule, and the random-oracle domain.  Failure to
instantiate `D_pair` or the torsion rule is a setup failure, not evidence
against the mathematical idea.

### `KeyGen(pp)`

1. Sample `(E,B) <- D_pair(lambda)`.
2. Independently sample canonical word descriptors `w_1,...,w_t`, each of
   length at most `d` and containing all four basis variables.
3. For each `j`, choose an admissible prime `N_j`, sample a canonical point
   `P_j` of exact order `N_j`, compute
   `gamma_j = w_j(B)` and `A_j = gamma_j(P_j)`, and reject this trial if
   `A_j` does not also have exact order `N_j`.
4. Return
   `pk=(E,((w_j,N_j,P_j,A_j))_{j=1}^t)` and `sk=B`.

The bounded expected runtime of the sampling and rejection loop is open.  On
a supplied valid `(E,B)` and accepted slot list, word compilation and point
evaluation are polynomial in the declared evaluable-basis representation,
`t`, and `d`.

### `Enc(pk,m)`

Parse `pk` canonically; verify the curve, word bounds, point membership, and
exact orders.  Reject if parsing or validation fails.  Require
`m in {0,1}^L`.

For every `j`, sample `r_j` uniformly from `Z/N_j Z`, compute

```text
R_j = [r_j] P_j
Z_j = [r_j] A_j .
```

Let

```text
T = Encode(pp, pk, ((R_j)_{j=1}^t))
K = H_RWCT("RWCT-PKE-v1" || T || Encode((Z_j)_{j=1}^t))
C = m XOR K .
```

Return the canonical ciphertext `ct=((R_j)_{j=1}^t,C)`.

### `Dec(sk,ct)`

Canonically parse `ct` and reject with `bottom` unless every `R_j` is a
canonical point in the declared exact-order subgroup.  Recompile
`gamma_j=w_j(B)` from the word in the associated public key and compute

```text
Z'_j = gamma_j(R_j)
K'   = H_RWCT("RWCT-PKE-v1" || T || Encode((Z'_j)_{j=1}^t))
m'   = C XOR K' .
```

Return `m'`.  A structurally valid ciphertext under a wrong key need not be
rejected; it can decrypt to an unrelated `L`-bit string.  Consequently this
packet does not claim CCA security or ciphertext authenticity.

## Actual-message correctness

For every valid output `(pk,sk)` of `KeyGen`, every
`m in {0,1}^L`, and every encryption coin vector `(r_1,...,r_t)`,
endomorphisms commute with scalar multiplication, so for every slot

```text
Z'_j = gamma_j(R_j)
     = gamma_j([r_j]P_j)
     = [r_j]gamma_j(P_j)
     = [r_j]A_j
     = Z_j .
```

The sender and recipient therefore query the random oracle at the identical
canonical string and `Dec(sk,Enc(pk,m))=m`.  The conditional correctness error
is zero.  This recovers the selected plaintext, not an endpoint, orbit,
invariant, or merely an encapsulated key.  The unconditional key-generation
success and expected-runtime bounds remain open because `D_pair` and its
rejection tail are not supplied.

## Why the complete-ring repair fails

### Quotient/factorization audit

For slot `j`, decryption calls `gamma_j` only on the cyclic set
`<P_j>`.  Define the restricted evaluator

```text
q_j(B) = (w_j(B) restricted to <P_j>)
Q(pk,B) = (q_1(B),...,q_t(B)).
```

The complete decryption map factors exactly as

```text
B --Q(pk,.)--> finite restricted-evaluator tuple --Dec_Q--> plaintext.
```

If two planted bases give the same `Q` for the fixed public word descriptors,
then every valid decryption transcript in this family is identical.  The
algorithm uses neither a multiplication table nor evaluations away from the
listed cyclic subgroups after compilation.  Thus syntactically placing all
four basis variables in every word does not make complete-ring extraction a
functional consequence of breaking confidentiality.

This factorization is a scoped statement about this compiled-word interface.
It does not prove that obtaining `Q` is easy, that `Q` can never determine a
ring under additional hypotheses, or that all EndRing-based PKE is impossible.
It does show that an EndRing reduction must prove a nontrivial
`RestrictedEvaluatorsToCompleteRing` theorem; this packet has no such theorem.

The natural unbounded-word repair does not fix the interface.  If `Enc` asks
for a fresh word not represented in the polynomial public table, it needs the
secret basis and ceases to be public encryption.  If the public key exposes
composable evaluators sufficient to evaluate every fresh word on ciphertext
points, the identical public-data operation performs recipient recovery and
the claimed asymmetry disappears.

### Basis-alignment audit

The ordinary EndRing output required here is **any** complete evaluable basis
`B'` spanning exactly `End(E)`.  The public descriptors `w_j` instead refer to
the planted ordered variables of `B`.  Given `B'`, decrypting requires an
additional polynomial algorithm

```text
BasisAlign(B', pk) -> (w_j(B))_{j=1}^t
```

or equivalent evaluators matching all `(P_j,A_j)` pairs.  No such algorithm,
uniqueness statement, or failure bound is available.  Defining the EndRing
challenge to demand the original planted basis would create a separately
named planted-basis recovery problem; it would not be bare EndRing.

### Real-distribution and extraction map

```mermaid
flowchart LR
    K[Real PairSample: E,B] -->|compile words| P[Real pk: E,w_j,N_j,P_j,A_j]
    P --> C[IND-CPA challenge ciphertext]
    C --> A[attacker bit]
    A -. missing RestrictedEvaluatorsToCompleteRing .-> O[complete evaluable End(E) basis]
    E[Bare EndRing challenge: E only] -. missing real-pk sampler .-> P
    O -. missing BasisAlign to planted B .-> D[recipient evaluators w_j(B)]
    D -->|correctness identity| M[selected plaintext]
```

The two challenge-embedding options both fail at a named arrow:

- From a bare challenge `E`, the reduction cannot compute the real
  `A_j=w_j(B)(P_j)` without the hidden planted basis.  Replacing them by
  independent random points needs an unproved distribution compiler and need
  not leave any consistent secret key.
- Supplying `(E,w_j,N_j,P_j,A_j)` as auxiliary challenge data defines
  `Aux-RWCT-EndRing`.  It matches the real view only by assumption, has no
  supplied reduction from bare EndRing, and still does not turn an IND bit
  into a complete basis.

The only direct security object exposed by the algorithms is a hashed
multi-transfer game: distinguish
`H_RWCT(T,([r_j]A_j)_j)` from uniform given the real public key and
`([r_j]P_j)_j`.  Call it `HRT-RWCT`.  A standard one-time-pad hybrid can turn
an IND-CPA attacker of advantage `epsilon` into an `HRT-RWCT` distinguisher of
advantage `epsilon/2`, equivalently
`Adv_IND-CPA <= 2 Adv_HRT-RWCT`, with comparable polynomial time and the same
random-oracle access.  `HRT-RWCT` is a separate, scheme-shaped assumption; no
reduction from it to bare EndRing is supplied, and it is not renamed EndRing.

## Frozen-control results (symbolic only)

| Control | Result in this attempted family |
| --- | --- |
| Leaked-plaintext known false | If `m` is appended to `ct`, an attacker wins independently of `E`.  Any transcript-only extractor claiming that every IND advantage yields a complete ring fails at the extraction step unless it already solves EndRing. |
| Public recovery known false | Publishing the restricted evaluators `q_j`, or a public operation evaluating every `w_j(B)` on `R_j`, computes every `Z_j`; recipient asymmetry vanishes. |
| Distribution bridge | Bare `E` lacks the `A_j` values correlated with a planted basis.  The bridge is open; an auxiliary-data problem is strictly named instead of being called EndRing. |
| Quotient control | Replacing `B` by the tuple `Q(pk,B)` leaves all decryption behavior unchanged.  Complete-ring necessity is therefore not established. |
| Actual-message | The correctness identity returns the exact selected `m`; this control passes conditionally on a valid key. |
| Wrong key / malformed ciphertext | Noncanonical and out-of-subgroup inputs return `bottom`; a canonical wrong-key ciphertext can yield an unrelated message.  Only IND-CPA is considered. |
| Prior-failure regression | No `SecretLift`, `EndpointLift`, C-star operation, target-frame reconstruction, evaluator reconstruction, admission decoder, digit-loop tie rule, or ER-McE residual decoder is invoked.  `BasisAlign` and `RestrictedEvaluatorsToCompleteRing` are explicitly open rather than assumed. |

## O1--O6 scorecard

| Obligation | Status | Result |
| --- | --- | --- |
| O1 exact hard problem | `open` | Bare EndRing is stated with curve marginal `D_curve` and exact complete-basis output, but the real public-key distribution needs a planted basis. `Aux-RWCT-EndRing` is separate and has no reduction from bare EndRing. |
| O2 honest algorithms | `open` | The interfaces and encodings are exact.  Efficient valid-key encryption/decryption are conditional on an evaluable basis; an efficient `D_pair` sampler and bounded rejection tail are missing. |
| O3 quantified correctness | `proposed_discharge` | Perfect selected-message correctness holds for every valid key, message, and coin vector by the displayed identity.  It has not been independently reviewed. |
| O4 functionality mechanism | `proposed_discharge` | Sender scalar transfer and private ring-word evaluation meet exactly, but recipient behavior factors through `Q`; complete-ring sensitivity is not discharged. |
| O5 correctly directed reduction | `contradicted` for this transcript-only compiled-word route | The real-key embedding, basis alignment, and attacker-to-complete-ring extraction arrows are missing.  The only stated bound targets separate `HRT-RWCT`, not EndRing. |
| O6 complete adversarial view | `proposed_discharge` | The public data, challenge, random-oracle queries, parsing, repetition, alternate encodings, wrong-key behavior, and excluded side channels are listed below; no independent review exists. |

## Complete adversarial view

The IND-CPA adversary receives the public parameters, field and curve `E`, all
word descriptors, torsion orders, bases `P_j`, public images `A_j`, canonical
encoding rules, and random-oracle access.  It may generate arbitrarily many
honest ciphertexts itself and retains their complete query histories.  It
chooses equal-length `m_0,m_1`, receives one challenge containing all `R_j`
and `C`, and outputs one bit.  There is no decryption oracle.

Noncanonical curve, point, word, public-key, or ciphertext encodings are
rejected; mathematical re-encodings are not silently identified with the
challenge encoding.  Exact subgroup validation is required.  Repeated
`r_j=0` is allowed by the written algorithm and makes that slot's transfer
point public; simultaneous zero/repeated coins can only weaken confidentiality
and must be included in any concrete analysis.  Ciphertext and key collisions,
word collisions, scalar words, zero word values, and correlated slot images
are not assumed negligible; KeyGen rejects only the stated order failure, and
their probabilities remain an O1/O2/O6 parameter obligation.

Timing, power, fault, cache, and memory-disclosure channels are excluded from
this mathematical IND-CPA model.  A constant-time implementation claim would
need separate evidence.  No concrete parameters or bit-security estimate are
supplied; asymptotic EndRing hardness cannot be converted into concrete
security by this packet.

## Scoped obstruction and forward guidance

**Exact scope.** Polynomial-size public keys that precompile finitely many
basis-dependent ring words to point-image slots and whose ciphertext points
remain scalar multiples of those slot bases.

**Failed arrow.** `IND-CPA attacker on the real RWCT distribution -> complete
evaluable End(E) basis` fails to follow from the available transcript because
the transcript factors through `Q`, while `E -> real pk` and
`arbitrary EndRing basis -> planted word evaluators` also lack algorithms.

**What remains open.** A different construction could escape this obstruction
by giving a basis-independent, publicly samplable trapdoor map for which any
valid complete EndRing output enables inversion and for which a successful
IND adversary yields the complete ring rather than a finite evaluator
quotient.  Such a proposal must provide the sampler, inversion algorithm,
distribution proof, and extraction theorem explicitly.  This packet does not
show that no such map exists.

**Decision-changing next action.** Before another PKE syntax is built, supply
one exact candidate map
`Trap_E : X_E -> Y_E` with (i) public sampling/evaluation from bare `E`,
(ii) polynomial inversion from any complete evaluable basis of `End(E)`,
(iii) a proof that inversion does not factor through a declared smaller
witness, and (iv) a black-box or non-black-box route from selected-message
IND advantage to a complete basis.  Failure of any one item should be kept as
the next scoped obstruction rather than patched with a renamed assumption.

## Inventor-protocol accounting

- **Object studied:** polynomial tables of compiled noncommutative ring-word
  evaluators used as a PKE trapdoor interface.
- **Depth of verified structure:** symbolic, unreviewed correctness and
  factorization derivations only; no measurement.
- **dominated_by:** `n/a (no secure construction or attack claimed)`.
- **sota_delta:** `0` security improvement and `0` measured attack
  improvement; contribution is one exact correctness shell and one scoped
  interface obstruction.
- **Closure mechanism:** finite compiled words factor through restricted
  evaluators; dynamic words either make `Enc` secret-dependent or publish the
  recipient operation.
- **Open direction:** a basis-independent public trapdoor map meeting all four
  properties in the decision-changing next action.

## Internal sources actually read

- `coordination/design/TASK-20261007-9c36ba/tasks/TASK-20261007-79e571/gap-packet.yaml`
  (`internal`; complete frozen gap packet).
- `research/ssi-endring-pke/2026-10-07-candidate-funnel/methodology.md`
  (`internal`; complete frozen method).
- `docs/scheme-construction-contract.md` and
  `templates/scheme-construction-contract.yaml` (`internal`; complete O1--O6
  contract and drafting template).
- `AGENTS.md`, `agents/idea-generator.md`, and
  `docs/inventor-protocol.md` (`internal`; task-governance instructions).

