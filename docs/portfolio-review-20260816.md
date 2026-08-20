# Portfolio review, 2026-08-16

A read of the whole research state — ledger, experiments, proposals, the
`ideas/` tree, and the knowledge corpus — made to decide where a new batch of
proposals should go. Written alongside the batch catalogued in
`ideas/catalogue-20260816/README.md`.

Every count below was produced by a script run against this checkout at commit
time and is reproducible from the committed records. Where a number comes from
parsing, the parse failures are reported rather than dropped. Nothing here is a
research claim: this is an inventory and an argument about allocation.

## 1. The state, in numbers

| corpus | count |
| --- | ---: |
| research questions (`ledger/questions/`) | 101 (99 `active`, 2 `open`) |
| hypotheses (`ledger/hypotheses/`) | 292 |
| proposals (`ledger/proposals/`) | 920, all parsing |
| evidence (`ledger/evidence/`) | 419 files, 416 parsing into an `evidence:` record |
| coordinator decisions (`ledger/decisions/`) | 582 |
| handoffs (`ledger/handoffs/`) | 951 |
| experiment directories (`experiments/`) | 539 |
| — with a parsing `specification.yaml` | 486 |
| — with a `specification.yaml` that does **not** parse | 13 |
| — with no `specification.yaml` at all | 40 |
| run directories under `experiments/*/runs/` | 2407, in 275 experiments |
| knowledge: literature / techniques / findings / open problems | 7852 / 93 / 73 / 31 |
| `ideas/` tree: rejected / deferred / active / reviews | 366 / 27 / 20 / 127 |

Experiment contract statuses: `approved` 187, `review_required` 141, `draft`
130, `completed` **15**, `paused` 6, plus six one-off strings
(`approved_execution_withheld`, `draft_review_required`,
`frozen_awaiting_execution`, `invalid`, `running`, one null).

## 2. What the program has actually established

Evidence records, by direction: `neutral` 217, `supports` 80, `contradicts` 19,
`weakens` 17, `mixed` 17, `inconclusive` 12. By strength: `preliminary` 201,
`inconclusive` 43, `replicated` 37, `n/a` 36, `moderate` 25, `strong` 24.

By claim tier: `toy` 268, `theory` 50, `not_applicable` 37, `medium` 13, and
**`crypto` 3** — `EV-MLKEM-002`, `EV-MLKEM-003`, `EV-SSI-0c529c`. By proof
status: `derivation` 138, `empirical_only` 134, `not_applicable` 121, and
**`certificate` 9**.

That last pair of numbers is the honest summary of the program's epistemic
position. Nearly everything measured is toy-scale, and almost nothing carries a
certificate that an independent verifier could re-check. This is not a failure —
`docs/claims-and-verification.md` is what forces the tiers to be stated at all,
and a program that labelled its toy results `crypto` would be worse. But it does
mean the corpus is overwhelmingly *scoping* work: measurements that bound what a
direction could be, rather than results about deployed objects.

### 2.1 What is established

The strongest committed content is negative-space work done well — theorems and
measurements that bound a direction rather than attacks that advance one. On
prime-field ECDLP:

- **Decomposition-yield conservation** (`KN-FIND-007`): summed over targets the
  yield is `C(B+m-1, m)` exactly, so factor-base geometry *redistributes* yield
  and cannot create it.
- **Semaev summation-cover monodromy** is `(Z/2)^{m-2}` universally — every
  curve, field and characteristic, arithmetic equal to geometric, with no
  exceptional locus (`KN-FIND-a8990a`, `KN-FIND-a1f3c2`, `KN-FIND-c41ea9`). On
  the factor-base locus the fibre splits completely at every `m`, so a
  Chebotarev-style census is constant exactly where relation search lives.
- **Newton polytopes of target-sectioned Semaev systems are box-saturated at
  `m ≤ 6`**, making BKK a proved constant — `(m+1)/2`, about 3.3× at
  cryptographic scale — and never an exponent.
- **ECDLP cost is invariant across an `F_p`-isogeny class** up to transport
  cost, with a proved zero-variance family; the surface/anomalous/MOV route is
  closed unconditionally by the Tate isogeny theorem.
- **Exact lossy propagation on a prime-order subgroup is impossible**: every
  exactly-propagating projection is injective or constant. This is the group-law
  rigidity theorem, and its four named escapes are what the taxonomy work since
  has been navigating.
- **Augmented oracles are GGM-simulable** (`KN-FIND-002`): jet and endomorphism
  oracles at `O(1)` overhead, elliptic-net and incidence oracles at non-constant
  overhead — closing those families at exponent 1/2.

Adjacent lanes produced real findings too: a genuine wolfSSL ML-KEM
ciphertext-comparison defect, found and closed; a 93–117 bit dynamic-range
deficit in archived `Pwrong` data; an anti-correlated HQC block-failure law; and
a corrected concrete cost interval for the Wesolowski `p^{1/3+o(1)}`
endomorphism-ring attack, which is memory-infeasible at `2^92.5` entries.

### 2.2 What the program's own instruments refuted

x-oracle MITM yield gains; Elkies factor-base augmentation; structured, AP and
endomorphism-invariant factor bases; the xedni and canonical-lift routes
(`alpha = 3` exactly, and CM moves height in the *defender's* direction);
fixed-curve preprocessing amortization; learned models on point coordinates;
belief propagation on the double-and-add graph (the graph is a chain, hence a
tree, so BP is exact and carries no gain); subresultant state collapse; and
roughly 700 archived cross-field algorithm transplants, whose common failure is
that the imported transform consumes the source-labelled object it was supposed
to produce.

Each of these is a named obstruction with an argument, which is the
`docs/inventor-protocol.md` §4 standard — not a fatigue report.

## 3. The binding constraint is execution, not ideation

920 proposals have produced 539 experiment directories, of which 15 are
`completed`. The median contract has zero runs; 2407 run directories exist but
are concentrated, with `EXP-IC-001` (748), `EXP-REPL-1d1287` (373),
`EXP-FCP-002` (144) and `EXP-MTBK-306bdb` (95) accounting for over half.

Proposal `status` is the same fact stated in one field: of 920 proposals, 638
are `proposed`, 280 carry no status at all, and **2 are `selected`**.

The `ideas/` tree is the sharper version again: 366 canonically rejected records
plus 293 pre-ID drafts, 97 retired contracts, 12 active contracts — and, by its
own README, **zero experiments ever ran from any of them**.

A related pattern the survey names is *instrument recursion*: campaigns that
spent dozens of batches repairing protocols which never executed (INSTR v4–v12,
ECTD v3–v7, seven SYC successors), leaving roughly 60 evidence records whose
strength is `protocol_integrity_only`. Effort was spent, and what it bought was
a better-specified contract rather than a measurement.

**This bears directly on the batch filed alongside this review.** Adding 300
proposals raises the proposal-to-completion ratio, and it is worth saying so in
the same document that files them rather than in a later post-mortem. Two things
mitigate it and neither dissolves it: every new proposal ships *with* a draft
contract, so the design work a Coordinator would otherwise have to do is already
done and the proposal cannot hide behind under-specification; and §5 below ranks
the batch so the queue is not flat. The allocation judgement — how many of these
to approve, and in what order — is the Coordinator's, and nothing in this batch
presumes it.

## 4. Where the coverage actually is

Proposals per research question is extremely skewed. `RQ-ECDLP-002` alone
carries 101. Meanwhile **22 research questions carry zero proposals**:

`RQ-SHAONE-081e3a`, `RQ-SHATWO-f196c7`, `RQ-SHATHREE-cd2cb2`,
`RQ-MDFIVE-6870c1`, `RQ-BLAKE-584719`, `RQ-ASCON-2dfd8b`, `RQ-POLYMAC-7c89e4`,
`RQ-SIMSPK-f6a6c0`, `RQ-MCE-3f7c02`, `RQ-MCE-b38a8b`, `RQ-MCE-f8fca0`,
`RQ-SNFS-005666`, `RQ-RSA-d46f02`, `RQ-FRODO-a2dbe2`, `RQ-FBG-001`,
`RQ-ALR-001`, `RQ-ALR-002`, `RQ-ALPF-001`, `RQ-ALECF-001`, `RQ-ALISO-001`,
`RQ-ALMIG-001`, `RQ-PMA-001`.

The pattern is legible. August 2026 accounts for 859 of the 920 proposals, and
six large single-session batches — 08-05 (162), 08-07 (178), 08-08 (131), 08-09
(115), 08-13 (51) and 08-15 (105) — account for 742 of those on their own. The
most recent wave (2026-08-15, 105 records) is almost entirely *self-audit*: the
program's own cost models, control
adequacy, instrument validity, certificate discipline, and literature-marking
integrity. That work is good and several of those records are among the sharpest
in the corpus. But it is why the primitive-level questions the program itself
opened went unstaffed — the questions exist, they are detailed, several state
their own `targets` list precisely enough to generate from, and nobody wrote a
proposal against them.

Proposal `class` distribution across all 920 confirms the shape: `measurement`
235, `control` 208, `mechanism` 167, `algorithm` 60. `novelty_status` is
`unverified` 577, `adaptation` 254, and — correctly, given that no external
source is reachable from this environment — `novel` never.

## 5. Where the new batch went, and why

The batch filed with this review targets the zero- and thin-coverage side
deliberately: 30 disjoint buckets, each anchored on an existing question, each
generated against an anti-duplication blacklist drawn from the survey above.

Symmetric and hash (`SHATWO`, `SHATHREE`, `SHAONE`, `MDFIVE`, `BLAKE`, `ASCON`,
`POLYMAC`, `SIMSPK`, `AEADC`, `ARGON`); code-based and multivariate (`MCEGOP`,
`HQCX`, `CODESD`, `MULTIV`); lattice (`NTRUL`, `FALCON`, `HAWKL`, `FRODOFO`,
`LATDUAL`); hash-based (`SLHDSA`); factoring (`SNFS`, `RSAPI`); prime-field
ECDLP (`FBG`, `ALR`, `ALPF`); quantum (`ALECF`); algebraic (`PMA`); and
`FHEX`, `ZKARG`, `SIDECH`.

Three bucket choices need justifying because they are not obvious. `FBG`, `ALR`
and `ALPF` are ECDLP buckets in a batch otherwise aimed away from ECDLP: they
are there because all three questions carry zero proposals *despite* `ALPF`
carrying 32 hypotheses — the lane was executed and never re-ideated, which is a
different failure from neglect. `SIDECH` has no research question at all; that
absence is itself the finding, since leakage and fault assumptions are used
throughout the portfolio and are nowhere stated as measurable predicates. And
`PMA` is included because its small cases are finite and exhaustively
computable, which makes a definite answer reachable — rare in this repository.

## 6. What this review found that the batch does *not* cover

The survey surfaced openings after the generation buckets were already
committed. They are recorded here rather than quietly folded in, and they are
the recommended starting point for the next batch:

**Whole primitives with no question and no hypothesis.** BIKE (the third
quasi-cyclic code-based KEM, while HQC has one question and Classic McEliece has
four). Stateful hash-based signatures XMSS and LMS/HSS. The code-equivalence and
rank-metric signatures — LESS, CROSS, PERK, RYDE, Mirath. Wave. LPN,
regular-syndrome LPN, and PCG/VOLE as hardness objects. Arithmetization-oriented
hashes (Poseidon, Rescue, Griffin, Anemoi, MiMC). Polynomial commitments (KZG,
IPA, FRI). OPRFs and PAKE (OPAQUE, CPace, SPAKE2). VRFs. Group-action
equivalence beyond MCE — Permuted Kernel, ALTEQ, tensor isomorphism. Drinfeld
modules. National standards: GOST/Streebog, SM2/SM3/SM4, ARIA, SEED, Camellia.
Stream ciphers as standalone objects. KDFs and non-polynomial MACs.

**Classical ECDLP territory the program skipped.** Hyperelliptic and genus-2/3
Jacobian DLP with Gaudry–Thomé–Thériault/Diem index calculus — exactly one
`specification.yaml` in the corpus mentions "hyperelliptic". Weil descent / GHS
and cover attacks. Anomalous (trace-one) curves and the Smart/Satoh–Araki/Semaev
p-adic lift. Point counting as a cost object (SEA, Schoof, Satoh–AGM,
Elkies/Atkin splitting). Index calculus for `E(F_{q^n})` at small fixed `n`, as
distinct from prime-field Semaev. DLP with auxiliary input (Cheon-style).

**Method families entirely absent from the experiment corpus.** No
`specification.yaml` mentions boomerang, impossible differential, or division
property. No contract measures a lattice reduction *profile* (Gram–Schmidt
log-norm sequence, root-Hermite δ₀, GSA slope) as its primary object. No FHE
contract exists at all. No contract measures a real cache-timing, power, or EM
side channel. Distribution-fit measurement appears in roughly 14 primary metrics
corpus-wide, all Dickman-family.

**Reversals nobody has taken.** `docs/inventor-protocol.md` §4 requires an
obstruction to be read twice — as a block *and* as a resource — and the
`obstruction` / `resource_check` fields exist for exactly that. **Zero of the
416 parsing evidence records carry an `obstruction` block at all**, so zero
carry a `resource_check`; and zero `COST-*` concrete-cost records exist
anywhere in the ledger. The machinery designed to convert a measured obstruction
into the next hypothesis has never been used once. The survey named specific
candidates: the elliptic-net oracle
measured GGM-simulable at `O(log N)` overhead (a lower bound for non-constant
simulation overhead is open); the x-oracle's `oracle_marginal_ratio = 3.754` read
as a query-redirection primitive rather than a defect; the canonical-height floor
used as a lower-bound ingredient rather than as a defeat.

## 7. Two operational defects worth a Coordinator's attention

**13 `specification.yaml` files do not parse**, and are therefore invisible to
every tool, survey and validator sweep that loads them: `EXP-DREG-001`,
`EXP-DREG-002`, `EXP-EQJ-001`, `EXP-FB-001`, `EXP-FB3-001`, `EXP-ICI-001`,
`EXP-P13-NC2b`, `EXP-P13-NC2d`, `EXP-REP-001`, `EXP-REP-002`, `EXP-SIG-001`,
`EXP-SIG-004`, `EXP-SIG-005`. `validate_ledger.py` passes because these are
grandfathered, which is correct for immutability but means their content is
silently absent from every downstream count — including §1 of this document,
where they are reported rather than absorbed. Several belong to lanes that are
still active.

**A further 40 experiment directories have no `specification.yaml`.** They are
not defects on their own — a directory can hold artifacts — but a contract-less
experiment directory is indistinguishable from a lost contract without opening
each one.

**The literature corpus knows less than its metadata claims.** Of 7852 entries,
**7481 carry `citation_verified: read`** — and **7427 point at a `downloads/`
tree that does not exist in this checkout**. This is already recorded as
`KN-OPEN-3f7a21` (which counted 7457 of 7666 when it was written; the corpus has
grown since). It matters beyond bookkeeping: `citation_verified: read` is the
marking that would let a record support `novelty_status: known` or `adaptation`,
and 254 proposals carry `adaptation` today. The template shape is visible too —
the survey reports 7420 of the entries sharing one of six relevance paragraphs.

None of these is a research finding and none is fixed here: repairing an
immutable record requires a superseding record under Coordinator authority
(AGENTS.md rule 2), not an edit.

## 8. Scope of this review

This is a survey of committed state, not an audit of correctness. It did not
re-run any experiment, re-derive any result, or verify any citation — and it
could not have: no external source is reachable from this environment, which is
also why every proposal in the accompanying batch is `novelty_status:
unverified`. Where the survey reports what a record says, it is reporting the
record, not endorsing it.

The counts in §1, §2 and §4 were re-derived directly rather than taken from the
survey agents that first reported them; the qualitative readings in §2, §6 and
§7 rest on those agents' reads of records they name.
