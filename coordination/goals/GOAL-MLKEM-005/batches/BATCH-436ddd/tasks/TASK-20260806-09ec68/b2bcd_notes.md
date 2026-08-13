# B2-B / B2-C / B2-D -- zero-new-compute carries

TASK-20260806-09ec68 / BATCH-436ddd / GOAL-MLKEM-005
Executor artifact. **Observations only.** No status change, no hypothesis
disposition, no claim about ML-KEM security or any FIPS 203 parameter set.

Every number and every quotation below comes from an artifact already committed
in `coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/` or from the ledger
records cited by ID. Nothing here was recomputed and nothing here was measured
by this task. Where I state a bound I state which lane it holds in, and where no
bound is sourceable I say that instead of supplying one.

---

## B2-B -- The C1 bound, stated separately for the two lanes the census separates

C1 asks for "a stated numeric bound, with derivation, on the `dbeta` -- and its
core-SVP bit value under one NAMED cost model -- attainable by best-of-M
selection at the M established in C2", and says in terms that
*"the attainable reduction is <= X bits, of which Y bits are model assumption,
and X may be 0"* satisfies it in full.

The census (`EV-MLKEM-d146a5`, rows in
`BATCH-a51f91/tasks/TASK-20260805-e6a153/census.json`) splits the deployment
surface in two, and **the two lanes do not admit the same kind of answer**. They
are therefore stated separately. Collapsing them into one number would be the
error the census exists to prevent.

### Lane A -- the normative single-use lane

**Sourced rows.** Firm: `R20` (SSH, draft-ietf-sshm-mlkem-hybrid-kex-10 Sec. 6,
*"generating an ephemeral key exchange keypair for ECDH and ML-KEM per
connection is REQUIRED by this specification"*) and `R21` (IKEv2,
draft-ietf-ipsecme-ikev2-mlkem-09 Sec. 3, *"Generating an ephemeral keypair and
ciphertext for each ML-KEM key exchange is REQUIRED by this specification"*).
Caveated: `R09` (MLS KeyPackage, single-use **SHOULD**, not MUST) and `R22`
(Signal PQXDH one-time prekey, single-use by construction, specified against
Kyber-1024 rather than FIPS 203 ML-KEM). Governing clauses in the same
direction: `R02` (SP 800-227 Sec. 4.2 RS6, ephemeral key pairs *shall* be used
for one execution) and `R04` (SP 800-57 Pt.1 Rev.5 Table 1 rows 15/16,
cryptoperiod *"One key-agreement transaction"*).

Per correction **CX-1** in `EV-MLKEM-d146a5` the firm count is **2 firm plus 2
caveated, not 6**: `R12` and `R14` state one ciphertext *per handshake* under a
governing clause (`R13`) that permits key reuse, so they are not single-use
rows. That correction is carried here rather than restated more favourably.

**The bound.**

```
M = 1
selection gain G  <=  log2 M  =  log2 1  =  0                (bits of choice)
best-of-M norm ratio c  =  min over 1 candidate  =  1        (exactly)
dbeta  =  beta*(c = 1) - beta*(c = 1)  =  0                  (exactly)
core-SVP value  =  0.292 * dbeta  =  0.000 bits              (exactly)
```

> **X = 0 bits exactly. Y = 0 bits of model assumption.**

**Why Y = 0, which is the part that matters.** The derivation never enters a
cost model. `c = 1` is arithmetic on `M`: the minimum of a one-element set is
its only element, so the selection changes no norm, so no norm ratio is fed to
any estimator, so no BKZ profile, no curvature `f''`, no `0.292` constant and no
`RC.MATZOV` readout is load-bearing. The `0.292 * 0 = 0` line above is written
only to show that the named cost model is applied and returns zero; **delete the
cost model entirely and X is still 0.** An f'' sensitivity table is therefore
*not required beside this figure* -- C1's f'' clause is conditional on the figure
depending on curvature, and this one does not. That is the strongest form in
which C1 can be answered, and it is available only because the lane's M is
pinned by normative text rather than estimated.

**Scope, stated as narrowly as the derivation warrants.** This bounds the
reduction attainable *by best-of-M selection* -- the mechanism GOAL-MLKEM-005 is
about -- at the M these specifications require. It is not a statement that no
multi-ciphertext attack helps: an attack that does not work by choosing the
smallest-error ciphertext is out of this bound's scope entirely, and `R20`/`R21`
are two deployment modes, not the deployment surface. Two rows carry a
REQUIRED; two more carry a SHOULD or a construction, and a SHOULD is not a
MUST. Non-conforming implementations are outside every row.

### Lane B -- the count-unstated lane

**Sourced rows.** Eight of the fourteen deployment-mode rows state no count in
either direction: `R06` (HPKE recipient key reuse explicitly permitted), `R10`
(MLS last-resort KeyPackage, reuse MAY be allowed, bounded only by a
rate-limiting SHOULD and a time window), `R15` (ECH, static key, rotation only
RECOMMENDED -- and Sec. 10.3 argues the other way: *"anonymity sets will
typically involve many connections even with fairly fast rotation intervals"*),
`R16` (X-Wing), `R17` (LAMPS X.509 profile, certificate validity only), `R18`
(CMS/RFC 9629, whose stated design intent is the opposite of a bound: the key
*"is expected to be carried in a long-lived certificate and used over and
over"*), `R19` (PKCS#11 v3.2 -- a token ML-KEM private key has no usage-counter
attribute at all), `R23` (PQXDH last-resort prekey, *"changes periodically"*).

**The bound, honestly:**

> **X is not a number in this lane, and no number can be sourced for it.**
> The attainable reduction is `<= log2 M` bits of choice, and `M` is fixed by
> nobody in the standards stack: it is a deployment-policy choice. Any X quoted
> here is a statement about an assumed policy, not about ML-KEM and not about
> the standards.

**The delegation chain terminates, and that is the finding, not a gap in the
search** (this is B2-C, stated there in full): `R13`
draft-ietf-tls-hybrid-design-16 Sec. 2 requires reusing implementations to
*"ensure that the number of reuses of a KEM public key abides by any bounds in
the specification of the KEM"*; the specification of the KEM is FIPS 203; `R01`
records that FIPS 203 fixes no lifetime, cryptoperiod, use counter or
decapsulation limit, and defers to SP 800-227; `R03` records that SP 800-227
Sec. 4.1 describes the static case as *"many connections from multiple parties
over a long period of time"* and attaches only an ownership requirement (RM3),
not a count; and `R24` (CFRG) endorses reuse for *"multiple incoming
ciphertexts"* without a count.

**The conditional form, with its model content named.** If, and only if, a
deployment *chooses* an M, the chain from M to a bit figure is:

```
M  ->  E[min of M error norms] / E[error norm] = c(M)  ->  dbeta = beta*(c) - beta*(1)  ->  0.292 * dbeta
```

Every arrow after the first is a **model readout**. `c(M)` needs a
distributional model of the projected error norm -- which is exactly what
criterion C3 is measuring, and which B2-A adjudicates for the tested cells only.
`beta*(c)` is the lattice estimator's discrete optimiser output and depends on
the BKZ profile through its curvature.

**The f'' sensitivity table, printed beside the curvature-dependent figures and
labelled a model readout, as C1 requires.** All rows are quoted from
`BATCH-a51f91/tasks/TASK-20260805-9672b3/results.json`
(`finite_difference_table` and `arm_b_d_not_reoptimised`), instrument
`primal_bdd` / `PrimalHybrid(zeta=0, mitm=False, babai=False)` under
**`RC.MATZOV`**, estimator pinned at commit `3e48ef42`, known-answer control
passing at exact equality. **These are MODELLED cost-model estimates, not
measurements, and no row of this table is a property of ML-KEM.**

| set | c | `dbeta` (m re-optimised) | `0.292 * dbeta` bits | estimator's own `dlog2(rop)` | `dbeta` (arm B, d NOT re-optimised) |
|---|---|---|---|---|---|
| Kyber512 | 0.99 | -1 | -0.292 | -0.2932 | -1 |
| Kyber512 | 0.98 | 0 | 0.000 | -0.5717 | 0 |
| Kyber512 | 0.95 | -6 | -1.752 | -1.6773 | -6 |
| Kyber512 | 0.90 | -12 | -3.504 | -3.4716 | -12 |
| Kyber768 | 0.99 | -2 | -0.584 | -0.5427 | -- |
| Kyber768 | 0.98 | -3 | -0.876 | -0.9718 | -- |
| Kyber768 | 0.95 | -9 | -2.628 | -2.4941 | -- |
| Kyber768 | 0.90 | -18 | -5.256 | -5.0066 | -- |
| Kyber1024 | 0.99 | -3 | -0.876 | -0.6952 | -- |
| Kyber1024 | 0.98 | -6 | -1.752 | -1.3763 | -- |
| Kyber1024 | 0.95 | -12 | -3.504 | -3.3444 | -- |
| Kyber1024 | 0.90 | -24 | -7.008 | -6.711 | -- |

Read the table for its **sensitivity**, which is the point of printing it:

* `dbeta` is an **integer** selected by a discrete search, so it is quantised
  and carries the optimiser's own selection noise. Kyber512 at `c = 0.98`
  returns `dbeta = 0` while `c = 0.99` returns `-1`: the sequence is **not
  monotone in c**. Any single row read alone would misstate the trend.
* The two conversion routes disagree at the same c -- Kyber512 `c = 0.98` gives
  `0.292 * dbeta = 0.000` bits but the estimator's own `dlog2(rop) = -0.572`
  bits. The gap is the `0.292` constant standing in for what the cost model
  actually prices, and it is 0.57 bits wide at a point where the core-SVP route
  says zero.
* Re-optimising `d` (hence `m`) moves `dbeta` by 0 in every Kyber512 row
  (`d_reoptimisation_worth_bits_at_baseline = 0.0088` bits) while moving `d`
  itself by up to 16, so the headline is insensitive to that knob and the
  dimension is not.
* Anomaly **A1** stands and is carried: `primal_bdd(..., optimize_d=False)`
  **silently ignores the kwarg**; only `cost_zeta(..., optimize_d=False)`
  actually disables it. Anyone controlling this estimator through `primal_bdd`
  kwargs may believe they disabled something they did not.

None of these figures is transported to Lane A, where they are not needed, and
none is subtracted from the in-repo `primal_bdd` margins of 2.80 / 6.04 / 1.28
bits.

### The objection C1 asks to be addressed: a cost model pricing only BKZ blocks does not price a multi-ciphertext attack

Stated plainly, and I do not think it is answerable in the model's favour.

`0.292 * beta` prices **one** BKZ-beta call on **one** lattice. An adversary
holding M ciphertexts under one encapsulation key is not running M such calls.
All M ciphertexts live in the **same** lattice -- same `A`, same `q`, same
secret -- so the reduction is done once and amortises over all M targets, and
what follows per ciphertext is a cheap lift (Babai / BDD), not a block. The
honest accounting of best-of-M selection is therefore

```
cost  =  one reduction  +  M * (cheap per-target lift)
```

and **neither term is what a `dbeta` figure measures**. A `dbeta` figure answers
a different question -- *by how much would the single reduction have to get
easier to be worth as much as the selection advantage?* -- which is a
**translation into familiar units, not a cost**. Three specific consequences:

1. **The M lifts are unpriced.** A model with no per-target term cannot
   distinguish M = 1 from M = 2^20 except through the norm ratio, which is
   precisely the quantity C3 is trying to establish and which B2-A bounds only
   at toy scale.
2. **Genuinely multi-target algorithms are outside the parameterisation.**
   Batch-BDD and multi-target sieving are not beta-parameterised in the way
   core-SVP assumes; a Delta-beta cannot express a speedup that changes the
   algorithm rather than the block size. Bernstein ePrint 2022/1580 footnote 19
   names the concrete question as *"not addressed by this paper's
   asymptotics"*, and it remains open (`EV-MLKEM-d146a5`, K2 adjudication).
3. **The direction of the error is not known.** The translation could
   understate or overstate; nothing in the retrieved record pins its sign.

In **Lane A this objection is moot**, because M = 1 and there is no
multi-ciphertext attack to price. It bites only in Lane B, where -- as stated
above -- there is no sourceable M to price it at either. **The two lanes fail to
produce a nonzero X for two different and independent reasons, and that
coincidence is worth stating explicitly rather than letting one lane's zero read
as the campaign's answer.**

---

## B2-C -- The normative dead end, as a first-class defensive finding

*Not a footnote, and not a report about a failed search. The four rows below are
sourced, retrieved and hashed in `TASK-20260805-e6a153/census.json`; this is a
property of the standards stack, not of our reading of it.*

### Statement

> **The one free parameter of the best-of-M mechanism -- M, the number of
> ciphertexts decapsulable under a single ML-KEM encapsulation key -- is bounded
> by nothing in the standards stack for the static/reusable deployment lane.
> The normative delegation chain that is supposed to bound it terminates without
> a value, and it terminates at the standard that defines the algorithm.**

### The chain, with all four rows

| # | Row | Document and section | What it says | Where it points next |
|---|---|---|---|---|
| 1 | `R13` | draft-ietf-tls-hybrid-design-16, Sec. 2 | Reuse permitted; implementations that reuse KEM public keys *"MUST ensure that the number of reuses of a KEM public key abides by any bounds in the specification of the KEM or subsequent security analyses"* | **the specification of the KEM** |
| 2 | `R01` | FIPS 203, announcement pt. 13; Sec. 3.3; Sec. 7.1 | **No** lifetime, cryptoperiod, use counter or decapsulation limit. Full-text search for `cryptoperiod`, `number of (queries\|decapsulations\|encapsulations\|ciphertexts\|uses)`, `multi-user`, `multi-target`, `at most 2`, `single use`, `one-time` returns no use-count bound. Sec. 3.3 defers: additional requirements *"are given in SP 800-227"* | **SP 800-227** |
| 3 | `R03` | NIST SP 800-227, Sec. 4.1; Sec. 4.2 RM3 | Describes the static case as *"Alice might then accept many connections from multiple parties over a long period of time, each initiated via ek_A"*. The only requirement attached is ownership assurance (RM3), **not a count** | **nowhere** |
| 4 | `R24` | draft-sfluhrer-cfrg-ml-kem-security-considerations-05, Sec. 4 | Endorses reuse without a count: *"It is secure to reuse a public key multiple times ... use it for multiple incoming ciphertexts, generating multiple shared secret keys"*, recommending fresh keypairs only for forward secrecy | **nowhere** |

`R18` (CMS, RFC 9629 + draft-ietf-lamps-cms-kyber-13) is the sharpest
corroborating row and points the same way from the opposite direction: it
requires that the KEM *"be secure when the public key is used many times ... a
KEM algorithm with a single-use public key is not appropriate, because the
public key is expected to be carried in a long-lived certificate and used over
and over."* The specification's stated design intent is unboundedness.

### Why this is defensive, and why it is first-class

* It is **actionable by an implementer today** and costs nothing to act on: a
  deployment in Lane B cannot cite a standard for its M, so it must choose one
  and write it down. That is a concrete gap in deployment guidance, in the
  direction of caution, derived entirely from public normative text.
* It is **the campaign's most transportable product**: it does not depend on any
  measurement, any cost model, any heuristic, or any toy-scale extrapolation,
  and so it survives every scope limitation that binds the rest of this goal.
* It is **falsifiable and cheap to falsify**: one sourced clause in FIPS 203, SP
  800-227, or a successor stating a decapsulation count would retire it. That is
  the correct standard for a finding of this kind, and it is the reason to state
  it as a finding rather than a complaint.
* It **inverts the usual asymmetry**. A missing bound is normally reported as
  our failure to find one. Here the absence is *sourced*: four documents were
  retrieved, hashed and searched, and the chain's own terminus says nothing.
  Under `docs/inventor-protocol.md` Sec. 4 the distinction is exactly the one
  between `unverified` and a property of the object -- and this side of it *is*
  a property of the object.

### What it is NOT

* **Not a vulnerability, and not an attack.** No ML-KEM break; session recovery,
  not key recovery. An unbounded M is not a demonstration that large M helps an
  attacker -- that is criteria C1 and C3, which are answered above and in
  `b2a_report.md`, and Lane A's answer is exactly zero.
* **Not a claim that FIPS 203 is deficient.** FIPS 203 Sec. 3.3 explicitly
  routes application requirements to SP 800-227. The observation is that the
  route, followed to its end, arrives at prose rather than at a number.
* **Not a census result about deployed M.** M in deployment is unmeasured. Eight
  of fourteen modes state no count; that is a statement about documents.
* **Not promotable to `knowledge/` in this batch.** AGENTS.md rule 12 is UNMET
  and UNWAIVED (`DEC-20260805-4823db`, `knowledge_promotion.not_warranted`).
  This write-up is the artifact a promotion would draw on, filed where a
  Coordinator can find it, and nothing more.

---

## B2-D -- OA-aggregator resolution step for the literature-acquisition path

### The defect being fixed

`BATCH-a51f91/tasks/TASK-20260805-cdee80/reads.md` Sec. 3.2 recorded
Duman-Hoevelmanns-Kiltz-Lyubashevsky-Seiler (CCS 2021 = ePrint 2021/1351) as
**UNOBTAINABLE** after a documented set of failed routes: ePrint landing 200 but
`eprint.iacr.org/2021/1351.pdf` **403** (Cloudflare, twice, including with a
browser UA), ACM DL PDF **403**, reader-proxy `r.jina.ai` 200-wrapper containing
a Cloudflare challenge, Wayback connection reset with availability API **429**,
no arXiv record, no institutional copy found.

**None of those routes is an open-access aggregator**, and the paper was
retrievable in two commands (`RT-20260806-d008e0` Sec. 4.1). Recorded as **CE-3**
and **CX-3**.

### The step to insert, before any "unobtainable" finding may be recorded

```
# 1. resolve the DOI through OpenAlex -> OA status and every known OA location
curl -s "https://api.openalex.org/works/doi:<DOI>"
#    read: is_oa, oa_status, best_oa_location.pdf_url, locations[].pdf_url

# 2. if OpenAlex is silent, ask Unpaywall (email is a required query parameter)
curl -s "https://api.unpaywall.org/v2/<DOI>?email=<contact>"

# 3. fetch the repository / institutional-repository URL the aggregator names,
#    NOT the publisher URL -- the publisher is usually the thing that 403'd

# 4. record for the retrieved file: HTTP status, Content-Type, byte length,
#    page count, sha256, and WHICH version it is
```

**Worked instance, verbatim from `RT-20260806-d008e0` Sec. 4.1.**
`curl -s https://api.openalex.org/works/doi:10.1145/3460120.3484819` returns
`is_oa: true`, `oa_status: gold`, and a repository location at
`https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf`, which returns
**HTTP 200, `application/pdf`, 1,832,736 bytes, 17 pages**, sha256
`2198eaf192cd58aa48fc272ebe18c66145476bfbe6a951fadb15dc6eb59bcb4c`. Elapsed:
about ninety seconds.

### The version caveat, which is part of the step and not a postscript

The retrieved file is the TU/e green-OA copy of the **CCS'21 published version**
(DOI `10.1145/3460120.3484819`). It is **not** the ePrint 2021/1351 PDF, and the
two may differ. Any acquisition record produced by this step **must name which
version was obtained**, because "the paper" is not a single object. The red team
asserted only what it read, and recorded the distinction; the step inherits that
discipline. `ePrint 2021/1351` itself remains **unretrieved**.

### The wording rule that goes with it

Per `docs/inventor-protocol.md` Sec. 4 and CE-3: **"unobtainable from N routes"
is a report about the search, whose honest status is `unverified`. It may not be
written as a property of the document.** Correct forms:

* `unretrieved -- N routes attempted, listed, aggregator step run and returned
  no OA location`
* `retrieved via <aggregator> -> <repository URL>, version <published|preprint>,
  sha256 <...>`

And the count must be the producers' own: `reads.md` Sec. 3.2 lists **eight**
route rows and the producers' own list has at least **seven** failed routes for
the body, so the Coordinator's "four routes" was wrong in its count as well as
in its framing (CE-3).

### Correction to this batch's acquisition table

> **`reads.md` Sec. 3.2, row (iii), Duman et al. CCS 2021 / ePrint 2021/1351:
> status `UNOBTAINABLE (full text)` is superseded.** The CCS'21 published
> version was retrieved on 2026-08-06 via OpenAlex ->
> `https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf`, HTTP 200,
> 1,832,736 bytes, 17 pages, sha256 `2198eaf1...`, and Bernstein's Appendix A.4
> quotations at page 3 and footnote 2 were checked against it at first hand and
> found accurate (`RT-20260806-d008e0` Sec. 4.2), which discharges the
> precondition `reads.md` Sec. 3.5 attached to the kill-(iii) verdict.
> **ePrint 2021/1351 itself remains unretrieved.** `reads.md` is immutable and
> is not edited; this note supersedes the row, per the program's correction
> convention.

Also carried forward unchanged, because it is a different failure and this step
does not fix it: the Ducas-Pulles material in `reads.md` Sec. 4 is
`unable_to_check` (DEF-9) and must not be cited downstream as archived.

---

## Provenance

| Claim class | Source |
|---|---|
| Census rows R01-R24, quotations, retrieval dates, source hashes | `BATCH-a51f91/tasks/TASK-20260805-e6a153/census.json`, `census.md` |
| CX-1 firm-count correction (2 firm + 2 caveated, not 6) | `EV-MLKEM-d146a5`, carried in `DEC-20260805-4823db` |
| Cost-model rows, `dbeta`, `dlog2(rop)`, arm B, anomaly A1 | `BATCH-a51f91/tasks/TASK-20260805-9672b3/results.json` |
| Acquisition failure routes | `BATCH-a51f91/tasks/TASK-20260805-cdee80/reads.md` Sec. 3.2 |
| OpenAlex retrieval, hashes, quotation check, CE-3 | `BATCH-a51f91/tasks/TASK-20260805-49acd8/report.yaml`, `notes.md` Sec. 4.1-4.2 |
| C1 wording, f'' clause, stop rule | `ledger/goals/GOAL-MLKEM-005.yaml`, `completion_criteria` |
| CE-1..CE-6, DF-1..DF-3, rule-12 status | `ledger/decisions/DEC-20260805-4823db.yaml` |

**Compute used by B2-B, B2-C and B2-D: none.** No script was run and no number
was recomputed for this file.
