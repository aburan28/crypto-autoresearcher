# Draft defensive finding: the ML-KEM deployment normative-count-bound gap

- Task: `TASK-20260806-3b0337` | Batch: `BATCH-5a4656` | Goal: `GOAL-MLKEM-005`
- Role: executor. **Write-up only.** No new literature retrieval, no new
  census rows were performed for this task; every row and quotation below
  traces to `BATCH-a51f91` artifacts, cited with path and hash in
  `receipt.json`.
- Role authority: `agents/executor.md` / `docs/agent-runtime-core.md`.

## Status of this document — read before anything else

**THIS IS A DRAFT, NOT AN APPROVED KNOWLEDGE-CORPUS ENTRY.**

- AGENTS.md rule 12 (the review/promotion gate for knowledge-corpus entries)
  is **UNMET and UNWAIVED**, inherited unchanged from GOAL-MLKEM-003/004 and
  restated in `EV-MLKEM-d146a5.yaml`. This task does not create or promote a
  `KN-FIND` entry. Only the Coordinator may mint or promote a `KN-*` record,
  and only once rule 12 is satisfied.
- No status change is made to any `EV-MLKEM-*` record or any `KN-*` entry by
  this document.
- This is a candidate write-up the Coordinator may, at its own discretion and
  after independent Validator/Red Team review of this batch, promote to a
  `KN-FIND` entry in a future, separate archive action. Until that happens it
  has the standing of an executor work product only.
- Role: executor, **observations and a sourced compilation only**. No
  hypothesis is supported, rejected, or closed here; no heuristic is declared
  validated or refuted; nothing here changes the direction of
  `EV-MLKEM-d146a5` or of `GOAL-MLKEM-005`.

## What this finding is

No retrieved ML-KEM specification or Internet-Draft states a bound — in
either direction — on `M`, the number of ciphertexts decapsulable under one
static ML-KEM encapsulation key, in any of eight surveyed deployment modes
where a key can legitimately be reused. The one normative attempt in the
standards stack to delegate such a bound (the TLS hybrid-design reuse
clause) delegates it to FIPS 203, which does not state one. This is an
absence of a stated ceiling and an absence of a stated floor alike; it is not
a demonstration that any deployment is unsafe.

## 1. CX-1's corrected row classification, restated in full

Source: `ledger/evidence/EV-MLKEM-d146a5.yaml`, `corrections_to_this_batch`
item `CX-1` (raised independently by RT-20260806-d008e0 OBJ-2 and
VAL-20260806-bb0559 DEF-6, verified by the Coordinator directly against the
`m`, `key_role` and `m_derivation` fields of the named rows in
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/tasks/TASK-20260805-e6a153/census.json`,
sha256 `a3aa39f41bea081a58e056e4fd72fff08f52afbd64dd27d666287624d8469507`).

The census's own one-sentence summary ("6 of 14 fix M = 1... the remaining 8
state no count bound at all") is defective at the level of that single
sentence: the row table itself is honest and carries every qualifier below,
but the compressed six-row "M = 1" bucket is heterogeneous and must be split
into three groups of fourteen deployment-mode rows:

1. **Two firm normative single-use modes** — a per-key `M = 1` **REQUIREMENT**
   specific to ML-KEM, with no caveat:
   - **R20 — SSH** (`draft-ietf-sshm-mlkem-hybrid-kex-10`, Sec. 6): "generating
     an ephemeral key exchange keypair for ECDH and ML-KEM per connection is
     REQUIRED by this specification."
   - **R21 — IKEv2** (`draft-ietf-ipsecme-ikev2-mlkem-09`, Sec. 3): "Generating
     an ephemeral keypair and ciphertext for each ML-KEM key exchange is
     REQUIRED by this specification."

2. **Two single-use modes with a named caveat**:
   - **R09 — MLS KeyPackage `init_key`** (RFC 9420 Sec. 10, Sec. 16.8): a
     **SHOULD**, not a MUST — "KeyPackages are intended to be used only once
     and SHOULD NOT be reused except in the case of a 'last resort'
     KeyPackage" — and R11 (scope note, same census) records that RFC 9420 as
     published registers **no ML-KEM cipher suite at all** (Sec. 17.1 lists
     only DHKEM suites; full-text search for "ML-KEM"/"MLKEM" returns zero
     hits). The KeyPackage mechanism is real; a standardised ML-KEM MLS
     deployment of it is not.
   - **R22 — Signal PQXDH one-time prekey** (Signal PQXDH spec, Sec. 2.5,
     3.2): single-use by definition ("each used in a single PQXDH protocol
     run"), but the retrieved specification text names "Crystals-Kyber-1024,"
     not FIPS 203 ML-KEM, as the pqkem parameter — a deployed-KEM-profile
     caveat carried in the row itself.

3. **Two rows stating one ciphertext per handshake under a clause that
   permits key reuse**, not a single-use requirement:
   - **R12 — TLS 1.3 hybrid `X25519MLKEM768`** (`draft-ietf-tls-ecdhe-mlkem-05`,
     Sec. 4.1–4.2): `m` = "1 per handshake," structural (one ServerHello
     ciphertext per offered client share), governed by the reuse-permitting
     clause at R13/CX-2 below.
   - **R14 — TLS 1.3 standalone ML-KEM key agreement**
     (`draft-connolly-tls-mlkem-key-agreement-05`, Sec. 4.2, 6.2): same
     structure; `key_role` is recorded verbatim in census.json as "ephemeral
     (client-generated), reuse permitted."

4. **Eight deployment-mode rows stating no count bound at all**, in either
   direction:
   - **R06 — HPKE recipient key** (RFC 9180 Sec. 9.2.3, 9.7.4): "a KEM key
     pair belonging to a sender or recipient works with all modes, it can be
     used with multiple modes in parallel" — recipient-key reuse is
     explicitly permitted with no count.
   - **R10 — MLS last-resort KeyPackage** (RFC 9420 Sec. 16.8;
     `draft-ietf-mls-extensions-10` Sec. 6.4): reuse explicitly permitted
     ("An application MAY allow for reuse... in order to prevent
     denial-of-service attacks"), bounded only by a rate-limiting SHOULD and a
     LeafNode Lifetime time window.
   - **R15 — TLS Encrypted Client Hello (ECH) config key**
     (`draft-ietf-tls-esni-25` Sec. 4, 10.3, 10.10.5): a static key with a
     rotation RECOMMENDATION and no count — and the one surveyed mode whose
     own privacy goal actively rewards a *larger* `M`: "Rotating too
     frequently limits the client anonymity set."
   - **R16 — X-Wing hybrid KEM** (`draft-connolly-cfrg-xwing-kem-10` Sec. 1.4,
     6, 6.1): "unrestricted (general-purpose IND-CCA KEM)"; no key lifetime,
     rotation rule, or use counter stated.
   - **R17 — LAMPS X.509 certified ML-KEM decapsulation key**
     (`draft-ietf-lamps-kyber-certificates-11` Sec. 1.1, 5, 9): bounded only
     by certificate validity, never by a decapsulation count; Sec. 9 refers
     key-reuse questions out to R24 below.
   - **R18 — CMS `KEMRecipientInfo`** (RFC 9629 Sec. 7;
     `draft-ietf-lamps-cms-kyber-13` Sec. 2.3): unbounded by explicit design
     intent — "the KEM algorithm MUST explicitly be designed to be secure
     when the public key is used many times... expected to be carried in a
     long-lived certificate and used over and over."
   - **R19 — PKCS#11 v3.2 token object** (OASIS PKCS#11 v3.2 Sec. 6.68): no
     usage-counter attribute exists in the API at all; full-text search for
     `CKA_USAGE`/"usage count"/"usage limit" returns zero matches.
   - **R23 — Signal PQXDH last-resort prekey** (Signal PQXDH spec, Sec. 2.5,
     3.2): "changes periodically," with the actual use count set by prekey
     demand versus one-time-prekey supply, neither of which the specification
     fixes. Same Kyber-1024-vs-ML-KEM caveat as R22.

So the count supporting an `M = 1` reading is **two firm plus two caveated**,
not the six the census's own summary sentence stated; splitting the bucket
this way makes the deployment record **more open**, not less, and it is the
producer's own row-level qualifiers (never edited by this correction) that
support the split. Per `census.json` `row_counts`, the underlying totals are:
24 rows total, 14 deployment-mode, 8 governing-clause, 2 scope-note; of the
14 deployment-mode rows, 6 are `m_class: one` (which this correction splits
2+2 above, plus R12/R14's structural "1 per handshake" reads separately) and
8 are `m_class: count_unstated`.

## 2. The normative delegation chain

Quoted with section numbers, and matching the direction Wesolowski-adjacent
work in this campaign does not touch (Rule 4/6 scope discipline — this is a
standards-text finding, not a cryptanalytic one):

1. **`draft-ietf-tls-hybrid-design-16` Sec. 2** ("Key encapsulation
   mechanisms") states, verbatim (source:
   `census.json` row R13, source_sha256
   `3a5148cb2e56854d6e0b3cbb88cc0fbf43e01da6d6ec8f35a2faff0df1b55081`; also
   quoted in `EV-MLKEM-d146a5.yaml` `what_is_established`):

   > "TLS 1.3 does not require that ephemeral public keys be used only in a
   > single key exchange session; some implementations may reuse them...
   > While it is recommended that implementations avoid reuse of KEM public
   > keys, implementations that do reuse KEM public keys MUST ensure that the
   > number of reuses of a KEM public key abides by **any bounds in the
   > specification of the KEM or subsequent security analyses**."

   This same clause is repeated verbatim in
   `draft-connolly-tls-mlkem-key-agreement-05` Sec. 6.2 (census.json row R14).

2. **The first limb — "the specification of the KEM" — terminates at FIPS
   203, which states none.** Source: `census.json` row R01, source_sha256
   `fe1f12f32a7e44ec9fdebbf400cda843a40b506dee676725234dc6f7923b6cac`:
   "FIPS 203 fixes no lifetime, cryptoperiod, use counter or decapsulation
   limit for a (ek, dk) pair." A negative full-text search for
   `cryptoperiod`, use-count terms, `multi-user`, `multi-target`, `at most
   2`, `single use`, `one-time` returns no bound in the retrieved PDF.

3. **The second limb — "or subsequent security analyses" — is `EV-MLKEM-d146a5`
   CX-2** (raised by VAL-20260806-bb0559 DEF-6): the census's own
   `census.md` quotes the whole sentence, so nothing is concealed, but the
   census's structural finding ("terminates without a value") dropped this
   limb from its own summary. The second limb's candidate landing point,
   pursued in this same batch's T4, is **Bernstein, ePrint 2022/1580**
   (`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/tasks/TASK-20260805-cdee80/reads.md`
   Sec. 1, sha256 `39b05faa650e0c479c729d1514188a4f089e16edfb33a64d7eacc47f9acb0947`,
   citing artifact sha256 `7b0e27261f4f9abcd7aa02fc9e3ed441b1f2d5b2ae3d7b5352f47e325e04f970`
   for the paper itself). That paper's **footnote 19**, quoted in `reads.md`
   Sec. 1.3, states explicitly:

   > "The concrete question — not addressed by this paper's asymptotics; see
   > Section 1.3 — is then the extent to which security is damaged by
   > variations in the effective size of (b, d)."

   Bernstein's own paper is asymptotic (analysis in terms of `n`, with
   `o(1)` terms) and gives Kyber-error-distribution-specific *constants*
   (`0.56984…` at η=3, `0.54668…` at η=2, `reads.md` Sec. 1.3) but **no
   concrete ML-KEM bit figure**. So the second limb of R13's delegation
   addresses asymptotics, not a concrete FIPS 203 bound — the chain
   terminates without a usable number by either limb.

## 3. The two "many uses, no count" clauses already sourced in BATCH-a51f91

- **NIST SP 800-227 Sec. 4.1** ("Static versus ephemeral key pairs"), the
  static-case language: "Alice might then accept **many connections** from
  multiple parties **over a long period of time**, each initiated via ek_A...
  In this scenario, Alice's encapsulation key is said to be static." Source:
  `census.json` row R03, source_sha256
  `41e427a461c1ae0ceed2a68dc29507400983d1d495c35631306d0f4803ca4614`. A
  negative full-text search of SP 800-227 for use-count terms and
  `cryptoperiod` returns zero matches — the document supplies no count and no
  time bound for the static case.
- **`draft-sfluhrer-cfrg-ml-kem-security-considerations-05` Sec. 4** (the
  CFRG draft R24, which is where R17's Sec. 9 deferral for the LAMPS
  certificate profile also lands), endorsing reuse for "multiple incoming
  ciphertexts" without a count: source `census.json` row R24, source_sha256
  `f6709454ab99802d7a4dd31e575a77a6ba01f0e1a6027a5143f7d9aff1134ff4`:

  > "It is secure to reuse a public key multiple times. That is, instead of
  > Alice generating a fresh public and private keypair for each exchange,
  > Alice may generate a public key once, and then publish that public key,
  > and use it for **multiple incoming ciphertexts**, generating multiple
  > shared secret keys. While this is safe, it is recommended that... they
  > should generate a fresh keypair each time... to obtain Perfect Forward
  > Secrecy."

  A negative full-text search of this draft for "number of," "limit," and
  "2^" returns no per-key use bound.

## 4. What a bound would look like, if one were added — a suggestion, not an analysis

The program has no attack demonstrated against ML-KEM at any deployment
count and must not manufacture urgency it cannot support. This is offered as
a standards-facing suggestion only:

- A specification that wishes to close this gap would state one of two
  things at the point where `draft-ietf-tls-hybrid-design-16` Sec. 2 (or an
  equivalent per-mode clause) currently delegates to "any bounds in the
  specification of the KEM":
  1. **A stated maximum reuse count** `M_max` for a static ML-KEM
     encapsulation key, analogous to the transaction-count cryptoperiods
     already used elsewhere in the standards stack for other algorithms
     (e.g. NIST SP 800-57 Part 1 Rev. 5 Sec. 5.3.6 Table 1's "One
     key-agreement transaction" language for ephemeral keys, `census.json`
     row R04, source_sha256
     `cc32391022c1382ac7c91490f6bcc8838e0f889925270da23ef4e800e2ecb7ad`); or
  2. **A mandatory rotation policy tied to a stated security parameter** —
     i.e., a rule that ties the certificate-validity or cryptoperiod window
     already present in some of these clauses (R05, R17) to an assumed or
     measured decapsulation rate, rather than leaving the conversion from a
     time bound to a count bound unstated as it is today (`census.md`,
     "Counts" section: "Converting any of the time bounds into a count would
     require a decapsulation rate that no retrieved specification
     supplies... inventing one and reporting it would be an estimate
     presented as a source, which AGENTS.md rule 9 forbids").
- FIPS 203 itself is the single point where such a bound, if it were placed
  at Sec. 3.3 or Sec. 7.1, would close the delegation chain in Sec. 2 above
  for every mode that currently defers to "the specification of the KEM."
- **This program does not have, and does not attempt to supply, the specific
  number `M_max` or the specific security parameter such a rotation policy
  would use.** That determination requires a concrete multi-target cost
  analysis this campaign's own C1 task (`TASK-20260806-4810e2`, run in
  parallel in this same batch) explicitly declines to complete in full,
  pricing only the lattice-reduction term. Any number offered here would be
  a deployment-policy assumption presented as a finding, which this task's
  own constraints forbid.

## 5. What this finding does NOT claim

Stated explicitly, per the task's own required content, and not hedged away:

- **No vulnerability is demonstrated in any of the eight count-unstated
  modes (R06, R10, R15, R16, R17, R18, R19, R23), or in any other mode
  censused.** No attack, no distinguisher, no adversary construction, no
  measured or modeled attack cost against any live deployment appears
  anywhere in this document or in the batches it draws from.
- **The gap is an absence of a stated bound, not evidence that reuse is
  unsafe at any particular count.** `census.md`'s own words, restated here
  because they remain exactly correct: "None of the 8 count-unstated modes
  forbids one either. The absence is an absence of a stated number in both
  directions; it is not a sourced ceiling and must not be read as one."
- **No numeric ceiling `M_max`, no `log2 M`, no `G`, and no bit figure appears
  anywhere in this document.** Those are out of scope for the census this
  finding restates and out of scope for this write-up task.
- **AGENTS.md rule 12 is UNMET and UNWAIVED.** No status change is made to
  any `EV-MLKEM-*` record or `KN-*` entry by this task. This document is not
  itself a `KN-FIND` entry and must not be cited as one until a Coordinator
  archive action promotes it after satisfying rule 12.
- **No ML-KEM break is claimed.** This is defensive vetting of the ML-KEM
  deployment standards stack, not a cryptanalytic result. Per the inherited
  `rule12_status` on this task's dispatch card: "This is defensive vetting of
  FIPS 203. Session recovery, not key recovery" is the framing that governs
  every prior producer in this campaign that this write-up draws from, and
  none of that framing changes here — indeed this task performs no
  measurement of any kind, cryptanalytic or otherwise.
- **Nothing here asserts a decapsulation rate, a rotation interval, or a
  concrete cost for any deployment.** Section 4 above names the *shape* a
  bound could take without asserting the number it should be.
- **No claim is made about whether any named implementation actually reuses
  a key beyond what its governing specification permits.** This finding is
  about what the specifications state (or fail to state), not about observed
  deployment behavior.

## 6. Follow-up needed, not performed here (write-up-only scope)

This task's scope forbids new literature retrieval or new census rows; the
following gaps were visible while assembling this write-up but are reported
rather than acted on:

- The census (`census.json` "Acquisition failures") records NSA CNSA 2.0
  guidance as an acquisition failure (HTTP 403 from `media.defense.gov` and
  `nsa.gov`, twice), not as a specification stating no bound. CNSA 2.0
  guidance may or may not address ML-KEM reuse counts; this remains unknown
  and is flagged as a genuine open item rather than assumed either way.
- `TASK-20260806-9918cd` (running in parallel in this same batch) documents
  an open-access-aggregator retrieval step and corrects the acquisition
  table for a different, unrelated paper (ePrint 2021/1351 / CCS'21). It has
  no bearing on the CNSA 2.0 gap above, which used a different failure mode
  (origin-level 403, not a paywall) and is not addressed by that task either.
- The eight count-unstated deployment modes were sourced from the documents
  the census retrieved; whether any deployment-specific profile document not
  yet in this census (e.g., a vendor-specific HSM profile beyond PKCS#11, or
  a national profile) states a bound is not determinable from this record
  and would require new retrieval outside this task's write-up-only scope.

## 7. Traceability

Every row, quotation, and hash cited above traces to a `BATCH-a51f91`
committed artifact; the complete cross-reference with sha256 values is in
`receipt.json` alongside this file.
