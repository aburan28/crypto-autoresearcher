# Draft finding: no retrieved ML-KEM specification bounds the number of ciphertexts decapsulable under one static encapsulation key

**Status: UNPROMOTED DRAFT.** This document is a candidate write-up for a
future `KN-FIND-*` knowledge-corpus entry. It is **not** an approved corpus
entry, has not cleared AGENTS.md rule 12 (independent `review-breakthrough`
at `max` effort), and carries no evidentiary status beyond what is already
recorded in `EV-MLKEM-d146a5.yaml`. AGENTS.md rule 12 is **UNMET and
UNWAIVED** for this campaign, inherited from GOAL-MLKEM-003/004. Promotion to
the knowledge corpus, if it happens, is a Coordinator act performed after
independent review; nothing in this document performs that act.

- Task: `TASK-20260806-3b0337` ("B2-C") | Batch: `BATCH-5a4656` | Goal:
  `GOAL-MLKEM-005`
- Role: executor. **Write-up only.** No new measurement, no new literature
  retrieval, no new census row. This task reduces zero uncertainty
  mathematically; it converts an already-established observation (BATCH-a51f91,
  corrected by `EV-MLKEM-d146a5.yaml` CX-1/CX-2) into a form suitable for a
  standards-facing audience.
- No status change to any `EV-MLKEM-*` record or `KN-*` entry is made or
  implied by this document.

---

## 0. Claim, stated precisely

**No specification or Internet-Draft retrieved by BATCH-a51f91 states a
maximum number of ciphertexts decapsulable under one static ML-KEM
encapsulation key, in any of the eight deployment modes census row
`TASK-20260805-e6a153/census.json` classifies as `m_class: count_unstated`.**
Where a normative document *does* delegate the question to another document,
the delegation chain has been traced to its end, and it terminates without a
number.

This is a **documentation-absence finding**, not a security finding. Section
7 below states explicitly what is not claimed.

---

## 1. CX-1's corrected row classification, restated in full

BATCH-a51f91's own one-sentence summary in `census.md` §"Distribution" said
"6 fix M = 1 ... and the remaining 8 state no count bound at all." Both
independent reviewers of that batch — `RT-20260806-d008e0` (OBJ-2) and
`VAL-20260806-bb0559` (DEF-6) — found this "6" bucket heterogeneous, and the
Coordinator's correction CX-1 (`ledger/evidence/EV-MLKEM-d146a5.yaml`,
`corrections_to_this_batch[0]`) split it into four groups. Restated here in
full, with the row-level source for each group being
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/tasks/TASK-20260805-e6a153/census.json`
(sha256 `a3aa39f41bea081a58e056e4fd72fff08f52afbd64dd27d666287624d8469507`,
confirmed identical to the blob committed at snapshot `7983a474`) unless noted
otherwise:

### 1.1 Two firm normative single-use modes (M = 1 by a REQUIRED clause)

| Row | Mode | Section | Quoted clause |
| --- | --- | --- | --- |
| **R20** | SSH PQ/T hybrid key exchange with ML-KEM (`draft-ietf-sshm-mlkem-hybrid-kex-10`) | Sec. 6 "Security Considerations" | "generating an ephemeral key exchange keypair for ECDH and ML-KEM per connection is REQUIRED by this specification." |
| **R21** | IKEv2 post-quantum key exchange with ML-KEM (`draft-ietf-ipsecme-ikev2-mlkem-09`) | Sec. 3 "Security Considerations" | "Generating an ephemeral keypair and ciphertext for each ML-KEM key exchange is REQUIRED by this specification." |

Both carry a normative, per-key, ML-KEM-specific single-use rule expressed as
a "REQUIRED" clause. `M = 1` in these two modes by the specification text
itself, not by inference. (Source: `census.json` rows R20, R21.)

### 1.2 Two single-use modes with a named caveat

| Row | Mode | Section | Quoted clause | Caveat |
| --- | --- | --- | --- | --- |
| **R09** | RFC 9420 (MLS) `KeyPackage` `init_key` | Sec. 10 "Key Packages"; Sec. 16.8 "KeyPackage Reuse" | "KeyPackages are intended to be used only once and SHOULD NOT be reused except in the case of a 'last resort' KeyPackage" | This is a **SHOULD**, not a MUST, and carries an explicit last-resort exception (see R10 below). Census row R11 additionally records that RFC 9420 as published registers **no ML-KEM cipher suite at all** (Sec. 17.1; full-text search for "ML-KEM"/"MLKEM" in RFC 9420 returns no match) — R09/R10 describe the KeyPackage *mechanism* an ML-KEM MLS cipher suite would inherit, not a standardised ML-KEM deployment as of the retrieved RFC text. |
| **R22** | Signal PQXDH one-time prekey `PQOPK_B` | Sec. 2.5 "Post-Quantum Key Encapsulation Keys"; Sec. 3.2 "Publishing keys" | "a set of signed one-time prekeys (PQOPK_B1, PQOPK_B2, ...) which are also signed with IK_B and each used in a single PQXDH protocol run." | PQXDH's `pqkem` parameter "is specified as 'a post-quantum key encapsulation mechanism that has IND-CCA post-quantum security (e.g. Crystals-Kyber-1024)'. The retrieved specification text names Kyber-1024, not FIPS 203 ML-KEM." Included as a deployed KEM profile whose M-bounding *mechanism* is the object of interest; not to be read as an ML-KEM conformance statement. |

(Source: `census.json` rows R09, R11, R22; the R22 caveat is the row's own
`caveat` field.)

### 1.3 Two per-handshake rows under a reuse-permitting governing clause

| Row | Mode | Section | Quoted clause |
| --- | --- | --- | --- |
| **R12** | TLS 1.3 hybrid `key_share`, X25519MLKEM768 (`draft-ietf-tls-ecdhe-mlkem-05`) | Sec. 4.1 "Client share"; Sec. 4.2 "Server share"; Sec. 6 "Security Considerations" | "the client's key_share carries one ML-KEM-768 encapsulation key and the server's key_share carries exactly one ciphertext, so one handshake yields one decapsulation. The draft itself imposes no freshness rule; its Sec. 6 defers to draft-ietf-tls-hybrid-design and to NIST SP 800-227." |
| **R14** | TLS 1.3 standalone ML-KEM key agreement (`draft-connolly-tls-mlkem-key-agreement-05`) | Sec. 4.2 "Transmitting encapsulation keys and ciphertexts"; Sec. 6.2 "IND-CCA" | "Same structure and same delegation as R12/R13: one server ciphertext per client encapsulation key, and Sec. 6.2 repeats verbatim that reusing implementations 'MUST ensure that the number of reuses of a KEM public key abides by any bounds in the specification of the KEM'." |

Both rows' own `m` field reads **"1 per handshake"** — a **structural** count
(one ServerHello ciphertext per offered client share), not a normative
single-use *rule*. Both rows' `key_role` records the key as reusable: R14's
reads "ephemeral (client-generated), reuse permitted." The governing clause
that licenses reuse of these keys is R13 (`draft-ietf-tls-hybrid-design-16`
Sec. 2), the subject of Section 2 below. (Source: `census.json` rows R12,
R13, R14.)

### 1.4 Eight modes stating no count bound at all

| Row | Mode | Section | Quoted bounding mechanism |
| --- | --- | --- | --- |
| **R06** | RFC 9180 (HPKE), recipient KEM key pair, base/PSK modes | Sec. 9.2.3 "KEM Key Reuse"; Sec. 9.7.4 "Forward Secrecy" | "Since a KEM key pair belonging to a sender or recipient works with all modes, it can be used with multiple modes in parallel." The only "MUST NOT reuse" clauses in RFC 9180 bind `ikm` and `Encap` randomness — the **sender** side — never the number of ciphertexts a **recipient** key may decapsulate. |
| **R10** | RFC 9420 (MLS) + `draft-ietf-mls-extensions-10`, last-resort `KeyPackage` | RFC 9420 Sec. 16.8; `draft-ietf-mls-extensions-10` Sec. 6.4; RFC 9420 Sec. 7.2 | "An application MAY allow for reuse of a 'last resort' KeyPackage in order to prevent denial-of-service attacks"; the extension marks KeyPackages "that MAY be used more than once". Bounded only by a rate-limiting SHOULD on the Delivery Service and the LeafNode Lifetime `not_before`/`not_after` window — no count. |
| **R15** | TLS Encrypted Client Hello, `ECHConfig` HPKE key (`draft-ietf-tls-esni-25`) | Sec. 4; Sec. 10.3 "Client Tracking"; Sec. 10.10.5 "Maintain Forward Secrecy" | "However, the window of exposure is bound by the key lifetime. It is RECOMMENDED that servers rotate keys regularly." Sec. 10.3 pushes the other way: "Rotating too frequently limits the client anonymity set ... anonymity sets will typically involve many connections even with fairly fast rotation intervals." The one surveyed mode whose own privacy goal *rewards* a larger `M`, and it still states no number. |
| **R16** | X-Wing hybrid KEM (`draft-connolly-cfrg-xwing-kem-10`) | Sec. 1.4 "Not an authenticated KEM"; Sec. 6 "Security Considerations"; Sec. 6.1 "Binding properties" | "it fixes no key lifetime, no rotation rule and no use counter." Full-text search of the draft for "reuse", "once", "number of", "static" and "limit" returns no per-key use bound. |
| **R17** | LAMPS PQ certificate profile, ML-KEM in X.509 (`draft-ietf-lamps-kyber-certificates-11`) | Sec. 1.1; Sec. 5 "Key Usage Bits"; Sec. 9 "Security Considerations" | "Certificate validity only. ... it states no decapsulation count, and Sec. 9 refers key-reuse questions out to draft-sfluhrer-cfrg-ml-kem-security-considerations (R24)" (see Section 4 below). |
| **R18** | CMS `KEMRecipientInfo` (RFC 9629) with ML-KEM (`draft-ietf-lamps-cms-kyber-13`) | RFC 9629 Sec. 7 "Security Considerations"; `draft-ietf-lamps-cms-kyber-13` Sec. 2.3 | "the KEM algorithm MUST explicitly be designed to be secure when the public key is used many times. For example, a KEM algorithm with a single-use public key is not appropriate, because the public key is expected to be carried in a long-lived certificate and used over and over." Unbounded **by design**, and the design intent is stated, not merely absent. |
| **R19** | PKCS#11 v3.2 (OASIS) ML-KEM mechanisms | Sec. 6.68 "ML-KEM"; `C_DecapsulateKey`; `CKA_TOKEN`, `CKA_DECAPSULATE` | "An ML-KEM private key object with `CKA_TOKEN = CK_TRUE` persists in the token across sessions, and `CKA_DECAPSULATE` is a plain boolean gating `C_DecapsulateKey`. There is no usage counter attribute." Full-text search for "CKA_USAGE", "usage count" and "usage limit" returns 0 matches. |
| **R23** | Signal PQXDH signed last-resort prekey `PQSPK_B` | Sec. 2.5; Sec. 3.2 "Publishing keys" | "Bob has a signed last-resort post-quantum prekey PQSPK_B, which he changes periodically". It is consumed "when one-time pqkem prekeys are not available ... when the number of prekey bundles downloaded for Bob exceeds the number of one-time pqkem prekeys Bob has uploaded." Two quantities are named (download rate, one-time-prekey supply); neither is fixed by the specification. Carries the same Kyber-1024-vs-FIPS-203 caveat as R22. |

(Source: `census.json` rows R06, R10, R15, R16, R17, R18, R19, R23.)

**Total check.** 2 (§1.1) + 2 (§1.2) + 2 (§1.3) + 8 (§1.4) = 14, matching
`census.json`'s `row_counts.deployment_mode: 14`. The corrected classification
accounts for every deployment-mode row; none is dropped or double-counted.

**Reading these together (own analysis, not a repeated source quote):** the
structural pattern the census surfaces is that every retrieved static/reused
row bounds its key in **time** (certificate validity, cryptoperiod, a
rotation *recommendation*) or by a **rate-limiting SHOULD**, and never by a
**count** of ciphertexts. Converting a time bound into a ciphertext count
would require a decapsulation rate that no retrieved specification supplies;
`census.json`/`census.md` explicitly decline to manufacture one, citing
AGENTS.md rule 9. This document does the same and manufactures no rate,
anywhere.

---

## 2. The normative delegation chain

The one place a numeric bound is *pointed to* rather than stated directly is
TLS's governing reuse clause, row R13 of `census.json`
(`draft-ietf-tls-hybrid-design-16`, "the reuse clause governing R12 and
R14"). Quoted in full, with section number, from `census.json` row R13
(`bounding_mechanism` field):

> **`draft-ietf-tls-hybrid-design-16` Sec. 2, "Key encapsulation mechanisms":**
> "TLS 1.3 does not require that ephemeral public keys be used only in a
> single key exchange session; some implementations may reuse them ... While
> it is recommended that implementations avoid reuse of KEM public keys,
> implementations that do reuse KEM public keys **MUST ensure that the number
> of reuses of a KEM public key abides by any bounds in the specification of
> the KEM or subsequent security analyses.**" (bold emphasis added here; not
> present in `census.json`'s plain-text field)

This sentence has **two limbs**, and CX-2 in `ledger/evidence/EV-MLKEM-d146a5.yaml`
(`corrections_to_this_batch[1]`) records that BATCH-a51f91's own structural
finding ("the delegation terminates without a value," `census.json` row R13's
`m_derivation` field) is correct about the **first** limb only and silent
about the **second**:

> CX-2 (verbatim): "`draft-ietf-tls-hybrid-design-16` Sec. 2 delegates to
> 'any bounds in the specification of the KEM OR SUBSEQUENT SECURITY
> ANALYSES'. The second limb does not terminate. The census quotes the whole
> sentence, so nothing is concealed; the summary drops the limb, and the
> dropped limb is where this very batch's T4 read lives."
> (`ledger/evidence/EV-MLKEM-d146a5.yaml`, `corrections_to_this_batch[1].correction`)

Tracing both limbs to their end, using only BATCH-a51f91's own retrieved
sources:

**Limb 1 — "any bounds in the specification of the KEM."** The KEM
specification is FIPS 203. `census.json` row R01 (`bounding_mechanism`
field, quoted in full):

> "NONE. FIPS 203 fixes no lifetime, cryptoperiod, use counter or
> decapsulation limit for a (ek, dk) pair. Sec. 3.3 states that 'Additional
> requirements, including requirements for using ML-KEM in specific
> applications, are given in SP 800-227', and Sec. 7.1 says only that dk
> 'shall remain private'."

`EV-MLKEM-d146a5.yaml`'s own `what_is_established` block records that this
negative was independently re-verified: "the validator's independent negative
full-text search returned zero hits for cryptoperiod, 'number of
queries/decapsulations/encapsulations/ ciphertexts/uses', multi-user,
multi-target, 'single use', 'single-use', 'one-time', 'limit the number',
'use count', 'usage count', lifetime, rotate, rotation and 'how many' ...
after positive controls, and with seven terms the census had not declared."
Its verdict, quoted in full: "The negative reproduces and is stronger than
stated." Limb 1
terminates at zero.

**Limb 2 — "or subsequent security analyses."** This is where
`TASK-20260805-cdee80/reads.md` (T4's literature-read record) is the relevant
source, per CX-2. `reads.md` §1 reads Bernstein, *Multi-ciphertext security
degradation for lattices*, ePrint 2022/1580, in full (55 pp, v2023-03-17;
retrieved from `cr.yp.to/papers/lprrr-20230317.pdf`, sha256
`7b0e27261f4f9abcd7aa02fc9e3ed441b1f2d5b2ae3d7b5352f47e325e04f970` per
`reads.md` §1.0). This is the closest thing among the retrieved corpus to a
"subsequent security analysis" of multi-ciphertext-per-key security for
lattice KEMs of ML-KEM's family, and `reads.md` §1.3 states plainly what it
does and does not give:

> "It does bound the asymptotic effect, and it gives Kyber-specific
> constants ... It does not give a concrete ML-KEM/Kyber bit figure, and says
> so." (`reads.md` §1.3, section heading and lead sentence)

The paper's own footnote 19, attached to its Kyber-specific asymptotic
constants table, quoted in full from `reads.md` §1.3:

> "A full analysis of Kyber would also have to account for the rounding in
> Kyber ciphertexts, which complicates single-target and multi-target
> attacks. This rounding is mostly in the C component but also a little in
> the B component, slightly increasing the effective size of d. The latest
> Kyber documentation claims that the rounding in the latest version of
> Kyber-512 gains several bits of security for attacks against the
> ciphertexts. **The concrete question—not addressed by this paper's
> asymptotics; see Section 1.3—is then the extent to which security is
> damaged by variations in the effective size of (b, d).**"
> (Bernstein, ePrint 2022/1580, footnote 19, as transcribed in `reads.md` §1.3)

`reads.md` §1.3 additionally reproduces the paper's own framing of what its
asymptotics can and cannot support (its "Caveats," §1.3 of the paper): a
concrete question is explicitly named as **not addressed**, error-prone
heuristic reliance is flagged, and the paper's Appendix B gives its one
concrete numeric example against **FrodoKEM-640**, not ML-KEM — a distinction
`reads.md` §1.3 states must not be transported.

**The chain, end to end:** `draft-ietf-tls-hybrid-design-16` Sec. 2 → limb 1,
"bounds in the specification of the KEM" → FIPS 203, which states none
(`census.json` R01, independently re-verified) → **dead end**. Limb 2, "or
subsequent security analyses" → the retrieved corpus's closest candidate,
Bernstein ePrint 2022/1580 → an asymptotic, heuristic result that names the
concrete ML-KEM question as unaddressed by its own footnote 19 → **no
concrete FIPS 203 bound results**. Both limbs of the one normative pointer to
a numeric `M` terminate without a number, on the retrievable record.

This is stated as a property of **the retrieved record**, exactly as T4's own
verdict on the adjacent DHKLS kill condition was stated (`reads.md` §3.4-3.5):
a claim about what could be found, not a claim that no bound exists anywhere
in the literature this environment did not retrieve.

---

## 3. SP 800-227 Sec. 4.1's static-case language

NIST SP 800-227 is the document FIPS 203 itself points to for
application-specific requirements (`census.json` R01: "Additional
requirements ... are given in SP 800-227"). Its treatment of the static case
is `census.json` row R03 (`bounding_mechanism` field, quoted in full):

> **NIST SP 800-227, Sec. 4.1 "Static versus ephemeral key pairs"; Sec. 4.2
> requirement RM3:** "Explicitly unbounded in count: 'Alice might then accept
> many connections from multiple parties over a long period of time, each
> initiated via ek_A. ... In this scenario, Alice's encapsulation key is said
> to be static.' The only requirement attached to the static case (RM3) is
> ownership assurance, not a use count."

Row R03's `m_derivation` field records that this is checked, not merely read:
"Full-text search of SP 800-227 for 'number of
(queries|decapsulations|encapsulations|ciphertexts|uses)', 'multi-user',
'multi-target', 'limit the number' and 'cryptoperiod' returns zero matches,
so this document supplies no count and no time bound for the static case."
By contrast, SP 800-227's *ephemeral*-case requirement RS6 (`census.json` row
R02) is a normative single-use "shall": "the key pair shall be used for only
one execution of key-establishment via a KEM and shall be destroyed as soon
as possible after its use." The document distinguishes the two cases sharply
and states a count for one of them and none for the other.

## 4. The CFRG draft's endorsement of reuse without a count

`draft-ietf-lamps-kyber-certificates-11`, the LAMPS X.509 profile
(`census.json` row R17), defers key-reuse questions to
`draft-sfluhrer-cfrg-ml-kem-security-considerations-05` ("Sec. 9 refers
key-reuse questions out to draft-sfluhrer-cfrg-ml-kem-security-considerations
(R24)"). That document is `census.json` row R24
(`bounding_mechanism` field, quoted in full):

> **`draft-sfluhrer-cfrg-ml-kem-security-considerations-05`, Sec. 4 "ML-KEM
> Security Considerations":** "Reuse endorsed without a count: 'It is secure
> to reuse a public key multiple times. That is, instead of Alice generating
> a fresh public and private keypair for each exchange, Alice may generate a
> public key once, and then publish that public key, and use it for
> **multiple incoming ciphertexts**, generating multiple shared secret keys.
> While this is safe, it is recommended that ... they should generate a
> fresh keypair each time ... to obtain Perfect Forward Secrecy.'" (bold
> emphasis added here; not present in `census.json`'s plain-text field)

Row R24's `m_derivation` field: "This is where R17's Sec. 9 deferral lands,
and it too terminates without a number. Full-text search of the draft for
'number of', 'limit' and '2^' returns no per-key use bound." This is the
CFRG's own affirmative security judgment about reuse — it says reuse "is
secure" and "is safe" — issued with no attached count in either direction.
Row R24 is a `governing_clause` row rather than one of the fourteen
`deployment_mode` rows tallied in Section 1, but it is the specific document
that R17 (one of the eight count-unstated deployment modes) names as its own
authority on the question, so it is included here as the terminus of that
row's own deferral.

---

## 5. What the corrected classification and the delegation chain together establish

Putting Sections 1-4 together, restated as an observation about the
retrievable record and nothing beyond it:

- Two deployment modes (SSH, IKEv2) carry a specification-level REQUIRED
  clause fixing `M = 1`. This is a real, sourced, per-mode ceiling — but it
  is a ceiling on two modes, not on the standard.
- Two modes (MLS `KeyPackage`, Signal one-time prekeys) are single-use by
  design but carry a named caveat (a SHOULD with an exception; a
  non-FIPS-203 KEM instantiation) that weakens how much weight the M = 1
  reading should carry.
- Two modes (TLS hybrid `key_share`, TLS standalone ML-KEM) impose one
  ciphertext per handshake as a **structural** fact of the message format,
  while their own governing clause **permits** reuse of the underlying key
  across handshakes and delegates any reuse-count bound to "the
  specification of the KEM or subsequent security analyses" — a delegation
  this write-up has traced to its end in Section 2, where it terminates
  without a number on both limbs.
- Eight modes (HPKE recipient keys, MLS last-resort `KeyPackage`s, ECH
  configs, X-Wing, LAMPS X.509 certified keys, CMS recipient keys, PKCS#11
  token objects, Signal last-resort prekeys) state **no count bound in
  either direction**. In several of these (CMS, the CFRG draft) reuse is not
  merely permitted but is the document's own explicit design intent — "used
  over and over," "secure to reuse a public key multiple times."
- The one document that both (a) governs the two ephemeral-but-reusable TLS
  modes and (b) explicitly names where a numeric bound *would* have to come
  from (`draft-ietf-tls-hybrid-design-16` Sec. 2) points at two places, and
  neither retrieved document supplies a number: FIPS 203 states none, and
  the retrieved "subsequent security analysis" (Bernstein ePrint 2022/1580)
  is explicit that its own asymptotics do not address the concrete ML-KEM
  question (footnote 19).
- SP 800-227's static case is qualitatively described ("many connections ...
  over a long period of time") with no count, in sharp contrast to its own
  ephemeral-case normative "shall" limiting `M` to 1.
- The CFRG's own security-considerations draft affirmatively endorses reuse
  for "multiple incoming ciphertexts" and supplies no count.

No document in the retrieved corpus states a number, in either direction,
for any of the eight count-unstated modes, nor for the two reuse-permitting
TLS modes once the delegation is followed to its end.

---

## 6. Recommendation for a standards-facing reader

This is offered as a **suggestion for what a standards body or protocol
designer might consider adding**, not as this program's own security
analysis. The program has run no attack against ML-KEM in a reuse setting
and has no measured or estimated cost figure that would motivate a specific
number (`EV-MLKEM-d146a5.yaml` records C1, the attainable-bound criterion,
as `UNTOUCHED` in this batch and only reachable, if at all, at zero new
compute by a sibling task in this same dispatch — see B2-B,
`TASK-20260806-4810e2`, whose own bound.md is the load-bearing analysis if a
number is wanted). Consistent with that limit, this recommendation names the
**form** a bound would take, not a value:

1. **A stated maximum reuse count, if a static-use mode is meant to be
   bounded by a count at all.** Where a specification already bounds a key
   in time (a cryptoperiod, a certificate validity period, a rotation
   recommendation — as SP 800-227 Sec. 5.3.6/Table 1, `census.json` R05, and
   the LAMPS profile's certificate-validity dependency, R17, both do), the
   time bound alone does not answer "how many ciphertexts." Either state a
   count directly, or state the decapsulation-rate assumption that converts
   the time bound into a count, explicitly and as an assumption rather than
   leaving the conversion to the deployer.
2. **Or, a mandatory rotation policy tied to a security parameter of the
   KEM**, analogous to how SP 800-227's requirement RS6 ties the ephemeral
   case to "one execution" rather than a raw ciphertext count — i.e., a
   *structural* bound (tie rotation to a protocol-level event) rather than a
   raw numeric one, where a raw number would be hard to justify without a
   concrete-cost analysis.
3. **Where a governing clause delegates the bound to "the specification of
   the KEM," the KEM specification (FIPS 203, or a companion document such
   as SP 800-227) should be the place that actually states it**, rather than
   the delegation terminating silently. `draft-ietf-tls-hybrid-design-16`'s
   own text already anticipates this need ("abides by any bounds in the
   specification of the KEM or subsequent security analyses"); at present
   there is nothing at the end of that pointer to abide by.
4. **Any such bound, if added, should itself state the cost model and
   heuristics it rests on** (per this program's own target-result-profile
   discipline, `docs/target-result-profile.md`), since the one retrieved
   analysis that comes closest to motivating a concrete number (Bernstein
   ePrint 2022/1580) is explicit that its results are asymptotic, heuristic,
   and do not address the concrete ML-KEM ciphertext-encoding question
   (footnote 19, quoted in Section 2 above).

This program takes no position on what number, if any, is appropriate. That
determination requires a concrete-cost multi-target attack analysis this
batch has not performed (see Section 7) and that no retrieved specification
has performed either.

---

## 7. Explicit non-claims

Stated plainly and not hedged:

- **No vulnerability is demonstrated in any of the eight count-unstated
  modes, or in the two reuse-permitting TLS modes.** This document reports
  an absence of a stated bound in the retrieved specification text. It does
  not report, measure, or estimate an attack, a cost, or a probability of
  compromise at any reuse count.
- **The gap is an absence of a stated bound, not evidence that reuse is
  unsafe at any particular count.** A specification's silence on a count is
  not equivalent to that count being unsafe, and this document does not
  treat it as such. Several of the surveyed documents (RFC 9629/CMS, the
  CFRG considerations draft) affirmatively state that reuse at scale is a
  *design intent*, and this document does not contest that judgment; it only
  observes that no accompanying count is stated.
- **No FIPS 203 parameter set is affected or cleared by this finding**,
  consistent with `EV-MLKEM-d146a5.yaml`'s `scope_statement`.
- **No number from this document, or from any source it cites, is a
  measured or estimated attacker cost.** Where Bernstein ePrint 2022/1580 is
  quoted (Section 2), it is quoted for what it says about the *scope of its
  own applicability* to ML-KEM, not for any cost figure; no constant, bit
  figure, or block-size reduction from that paper is repeated or transported
  here. `EV-MLKEM-d146a5.yaml`'s own scope note applies without exception:
  nothing measured in this campaign, at any scale, is claimed against
  ML-KEM's standardised parameters.
- **This document asserts nothing about ML-KEM's security in either
  direction.** It is a documentation-gap observation about the standards
  corpus this environment could retrieve, scoped exactly to the sources
  cited above and no further.
- **This document is not a completed C1/C2/C3 adjudication for
  GOAL-MLKEM-005.** C2 (the census) was met in BATCH-a51f91, as corrected by
  CX-1/CX-2; this write-up restates that correction and traces one governing
  clause to its end. It does not touch C1 (the bound) or C3 (the tail
  measurement), which are the subject of sibling tasks in this batch
  (`TASK-20260806-4810e2`, `TASK-20260806-b51ac8`).

---

## 8. Scope, follow-ups, and what this task did not do

- **No new literature retrieval was performed.** Every quotation above
  traces to a file already committed in BATCH-a51f91's snapshot (commit
  `7983a474be82684cca63ffd79495a3a50e582e62`): `census.json`, `census.md`,
  and `reads.md`. Where the task's own launch instructions described a
  source as living in `reads.md` and this write-up found it instead in
  `census.json` (SP 800-227 Sec. 4.1 and the CFRG draft's endorsement, both
  in Sections 3-4 above), the correction is recorded here rather than
  silently followed: both quotations are BATCH-a51f91 primary-source
  material either way, and citing the file that actually contains them is
  what AGENTS.md rule 9 requires. This is a citation-precision note, not a
  scope expansion — no new source was consulted to resolve it.
- **No new census row was created and no existing row was altered.** Every
  row quoted above is reproduced verbatim from `census.json`/`census.md` as
  committed.
- **Follow-up, not attempted here (out of this task's scope):** whether a
  standards body has, since the 2026-08-05 retrieval date, published a
  revision that adds a numeric bound to any of the eight count-unstated
  modes, to R12/R14's TLS delegation, or to `draft-ietf-tls-hybrid-design-16`
  itself, is unchecked. A future task could re-run BATCH-a51f91's T1/T4
  retrieval procedure against current draft revisions to see whether any of
  the eight rows or the TLS delegation chain have changed. That is new
  literature retrieval and is explicitly out of this write-up task's scope;
  it is named here as a follow-up rather than attempted.
- **Follow-up, not attempted here:** whether NSA CNSA 2.0 guidance states a
  reuse count is unknown — `census.md`'s "Acquisition failures" table
  records that both attempted URLs for the CNSA 2.0 advisory returned HTTP
  403, so CNSA 2.0 is **absent from the census as an acquisition failure,
  not as a specification that states no bound**, and this write-up preserves
  that distinction rather than treating the silence as a fifteenth
  count-unstated row.
