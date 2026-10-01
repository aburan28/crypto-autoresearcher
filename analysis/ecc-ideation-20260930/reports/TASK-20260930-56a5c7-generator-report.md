# Generator report, lane L3 (AUXIN), TASK-20260930-56a5c7

Date: 2026-10-01. Idea generator (Claude Code subagent, `research-deep`
policy served by the session model; `fallback_used: true` per the handoff's
`inference` block). Advisory ideation only: no run, no status change, no
approval; a filed proposal is not a candidate for design until the
dispatching session commits it.

## Returned once (2026-10-01): prior_art.nearest schema fix

The dispatcher returned all three records because `prior_art.nearest[].ref`
entries pointed at ledger paths, IDEA/DEC ids or URLs, which
`tools/validate_ledger.py check_prior_art` does not accept (only KR-* rows
and KN-* entries resolve there). What changed, and nothing else:

- **Every `nearest[].ref` now resolves to a KN-*/KR-* id.** The displaced
  pointers (DEC-20260802-204/-208, the supply-audit idea, the Satoh,
  Kim-Cheon and Jao-Yoshida ePrint URLs) were moved into a free-form
  `prior_art.searched.ledger_records_positioned_against` list and remain in
  `citations` and `discriminated_from` with their original provenance.
- New `nearest` refs: 68326c -> KN-LIT-6501 (special_case), KN-LIT-6736
  (adjacent), KN-TECH-febb4f (adjacent), KN-LIT-6596 (adjacent);
  6bde2d -> KN-LIT-6501 (special_case), KN-LIT-5040 (generalizes),
  KN-TECH-febb4f (adjacent); 704e43 -> KN-LIT-6501 (special_case),
  KN-LIT-6736 (adjacent), KR-RHO-6239aa (generalizes). Each entry carries
  provenance `internal` (entry read in full this session), relation, and a
  quantitative delta. `rows_checked` lists are unchanged and all KR-*.
- **KN-LIT check for the ePrint papers.** A Grep of `knowledge/literature/`
  for `2009/058|2012/609|2009/221` returned no hit. The dispatcher's
  candidate ids were checked by title: KN-LIT-2008 (SST/AGM point
  counting), KN-LIT-93696f (Pollard rho on prime fields), KN-LIT-1378
  (division polynomials), KN-LIT-1175 (Elkies primes), KN-LIT-4202 (AES
  error detection), KN-LIT-7646 (ate pairing decomposition), KN-LIT-240
  (Brezing-Weng discriminants), KN-LIT-088 (Fermat quotients) -- none is
  Satoh, Kim-Cheon or Jao-Yoshida, so those three stay URL citations with
  `retrieved` provenance (abstracts fetched this session) and are not used
  as `nearest`. A title grep did find KN-LIT-6596 (Boneh-Boyen, "Short
  Signatures Without Random Oracles"), read in full; its abstract does not
  state the generic q-SDH bound, which therefore stays `recalled`.
- **The `IDEA-20260831-ccb587` reference is resolved, not removed.** The
  record exists at `ledger/ideas/IDEA-20260831-ccb587.yaml` (Glob
  `ledger/**/IDEA-20260831-ccb587*`), not under `ledger/proposals/`; it is
  the supply-audit idea that GOAL-AUXIN-a93442, H-AUXIN-6db354 and
  CORR-20260923-187ea3 already cite, and it was read in full this session.
  Every mention in the three records now carries the explicit path
  `ledger/ideas/IDEA-20260831-ccb587.yaml` (likewise
  `ledger/ideas/IDEA-20260831-df4197.yaml` for the census idea), including
  `source_refs`, so no reader can mistake it for a proposals-directory id.
- Added `citations` entries for KN-LIT-6501, KN-LIT-6736, KN-LIT-6596 (68326c),
  KN-LIT-6501 / KN-LIT-5040 / DEC-20260802-208 (6bde2d) and KN-LIT-6501
  (704e43) so every `nearest` ref also appears as a citation with its
  verification note. No claim, mechanism, prediction, threshold, cost or
  novelty_status changed.

## Ids used and unused

| id | used | file |
| --- | --- | --- |
| IDEA-20260930-68326c | yes | `ledger/proposals/IDEA-20260930-68326c.yaml` |
| IDEA-20260930-6bde2d | yes | `ledger/proposals/IDEA-20260930-6bde2d.yaml` |
| IDEA-20260930-704e43 | yes | `ledger/proposals/IDEA-20260930-704e43.yaml` |

No unused ids; no spare id requested. All three records carry
`added: '2026-10-01'` as instructed (overriding BRIEF.md section 3's example
date) and the lane's `id_allocation_provenance` sentence.

## Records read for overlap (all in full unless noted)

- `analysis/ecc-ideation-20260930/handoffs/TASK-20260930-56a5c7.yaml`,
  `BRIEF.md` (sections 0-6), `context/L3-AUXIN.md`,
  `context/frontier-map-generic-rho.md` (24 rows).
- `ledger/questions/RQ-AUXIN-f8d8c0.yaml` (verbatim in the context file);
  GOAL-AUXIN-a93442 head projection.
- Consumed proposals: `IDEA-20260905-830138`, `IDEA-20260906-3d57e8`,
  `IDEA-20260906-81648b`.
- Unopened lane ideas (under `ledger/ideas/`, not `ledger/proposals/`):
  `ledger/ideas/IDEA-20260831-ccb587.yaml` (supply audit),
  `ledger/ideas/IDEA-20260831-df4197.yaml` (divisor census).
- Hypotheses: `H-AUXIN-6db354`, `H-AUXIN-7c52b2` (full); the Stage 0
  identity hypotheses 269efd/52eb55/9bb701/d2f0bb/e73988 and 66e6fd/686282
  at title/status level from the context file.
- `experiments/EXP-AUXIN-339fb0/specification.yaml` lines 1-284 in full
  (definitions, D1 pins, D2 typed costs, D3 bins, D4 calibration) plus a
  targeted grep of the remainder (controls C-PLANT-M/P/PL, C-INERT, null
  arm, the "never execute Cheon's algorithms, never generate or consume any
  auxiliary power, never enter a protocol-supply stage" scope line).
- `DEC-20260930-224fc1`, `DEC-20260802-204`, `DEC-20260802-208`,
  `CORR-20260923-187ea3` (full).
- `agents/idea-generator.md`, `docs/inventor-protocol.md` sections 4-5,
  `docs/target-result-profile.md`, `templates/research-records.md` ("Prior
  art on ideas", "Citation provenance"), the form exemplar
  `IDEA-20260926-89886c`.
- Knowledge: `KN-LIT-6501` (Cheon 2006, bulk-seeded), `KN-LIT-5040` (Kim,
  multiple DLPwAI), `KN-LIT-6736` (Takenaka-Yasuda 160-bit solve),
  `KN-LIT-6596` (Boneh-Boyen short signatures), `KN-TECH-febb4f`
  (Cheon-friendly orders), `KN-TECH-6ead00` lines 45-84.
- Other proposals that mention Cheon, at claim level: `IDEA-20260920-73dc35`
  (static-DH oracle on EcGFp5; different oracle model),
  `IDEA-20260830-3e38ce`, `IDEA-20260904-982159`, `IDEA-20260926-d06324`
  (Cheon as a ruler or tag-tracing homonym only).

## Searches run

Corpus (Grep; the crypto-kb index was empty this session,
`CRYPTO_KB_QDRANT_URL=:memory:`, so no `kb` provenance anywhere):

- `knowledge/`: `Cheon|auxiliary.input|q-SDH|powers.of.tau|Phi_k|cyclotomic|Kim.Cheon|Satoh|Brown.Gallant|Jao.Yoshida|Kozaki|Kutsuma` -- 217 files, almost all
  false positives ("Satoh" point counting; "auxiliary input" in obfuscation /
  LPN / random-oracle titles). Relevant: KN-LIT-6501, KN-LIT-5040,
  KN-LIT-6736, KN-TECH-febb4f, KN-TECH-6ead00, KN-TECH-8ef4c3,
  KN-OPEN-cc1988, KR-RHO-38be82 (tag tracing homonym). NOT retrieved: any
  KN-LIT on Satoh's generalisation, Kim-Cheon 2012/609, Jao-Yoshida,
  Brown-Gallant, or any ceremony specification.
- `knowledge/literature/`: `2009/058|2012/609|2009/221` -- no hit; title
  grep for Satoh / Kim-Cheon / Jao-Yoshida / Brown-Gallant / Bowe-Gabizon-
  Miers / Kozaki -- hits only KN-LIT-6596 (Boneh-Boyen), KN-LIT-41fe5c and
  KN-LIT-5597 (static DH over extension fields; unrelated oracle model).
- `knowledge/{findings,open-problems,techniques}/`: `APR-206|auxiliary.input|DLPwAI|Cheon`
  -- KN-TECH-febb4f, KN-TECH-6ead00, KN-TECH-8ef4c3, KN-TECH-4409e1,
  KN-OPEN-cc1988; no KN-FIND carries the DEC-20260802-204 gate.
- `ledger/`: `powers.of.tau|q-SDH|Phi_k|cyclotomic|Kim.Cheon|Brown.Gallant|Jao.Yoshida|trusted setup|KZG|Groth16|BLS signature|Boneh.Boyen` -- 95 files; relevant
  hits only RQ-AUXIN-f8d8c0, GOAL-AUXIN-a93442, ledger/ideas/IDEA-20260831-ccb587
  and -df4197, H-AUXIN-66e6fd, RQ-PAIR-f2e31f (which, on a second grep for
  `q-SDH|Cheon|powers.of.tau|KZG|SDH`, returned no match). No ledger record
  pins a ceremony size or carries a k > 2 branch.
- `ledger/proposals/`: `AUXIN|Cheon` -- 16 files (listed above).
- `ledger/hypotheses/H-AUXIN-*`: ids, statuses, statements.
- Glob `ledger/**/IDEA-20260831-ccb587*` -> `ledger/ideas/IDEA-20260831-ccb587.yaml`.

Web (WebFetch / WebSearch):

- RETRIEVED (abstract or page summary read): eprint 2009/058 (Satoh, "only
  effective for k = 1, 2"); eprint 2012/609 abstract (Kim-Cheon,
  O~(sqrt(p/tau_f) + d)); eprint 2009/221 (Jao-Yoshida, p^{2/5+eps} time
  with p^{1/5+eps} queries); eprint 2004/306 (Brown-Gallant abstract);
  eprint 2017/1050 (Bowe-Gabizon-Miers abstract; no size, no Cheon);
  github.com/ethereum/kzg-ceremony-specs (G1 powers up to 2^12-1 ... 2^15-1,
  65 G2); github.com/ebfull/powersoftau (depth 2^21, BLS12-381);
  github.com/privacy-scaling-explorations/perpetualpowersoftau (2^29 - 1
  powers, BN254, archived 2026-08-19); datatracker draft-irtf-cfrg-bbs-signatures
  (pk = one G2 point; signature = (A, e)).
- FETCHED BUT NOT READ: the Cheon 2006 IACR-archive PDF and the Kim-Cheon
  2012/609 PDF (binary; no poppler in the container, so `Read --pages`
  failed). Theorem-level Cheon content is therefore cited through the
  internal records that read it (H-AUXIN-6db354, CORR-20260923-187ea3,
  TASK-20260923-635c5c).
- WebSearch "Boneh Boyen q-SDH generic group lower bound": links only; the
  bound stays `recalled`.
- NOT searched: Filecoin and Aztec ceremony sizes (left UNDETERMINED in the
  roster), Kozaki-Kutsuma-Matsuo, the Cheon-Kim-Song survey, RFC 9381, the
  BLS signature draft (all `recalled`).

## One-line summaries

- **IDEA-20260930-68326c** | class `measurement` | claim: deployed SRS
  ceremonies release [tau^i]G1 up to 2^k - 1 on curves chosen with
  2^k | r - 1 (FFT friendliness), so the Cheon r - 1 branch is applicable
  with d_max >= 2^{k-1} and the verdict against memory-charged rho is a
  constant-factor comparison R = 0.936 sqrt(d_max)/(a c_step) with the
  step-unit bracket fixed now; pre-registered: Ethereum KZG setups
  STEP_UNIT_DEPENDENT, Sapling and PPoT BELOW_RHO by 2^1.5-2^9 (exponent
  about 0.466-0.494 vs 0.4996, memory exponent 0 both) | novelty
  `unverified` | cost: implementation low, compute low (one session of
  artifact pinning) | first test: pin the six S1 artifacts and emit the
  zero-run R table at both bracket ends with the 2-adic lower bound
  labelled LOWER_BOUND.
- **IDEA-20260930-6bde2d** | class `control` | claim: under a supply cap
  q_max every polynomial-embedding branch (Cheon r +- 1, Satoh Phi_k,
  Kim-Cheon general f) has gain <= sqrt(q_max), so the family ceiling is
  e >= 1/2 - log_r(q_max)/2 (0.443 at 2^29); on 2-adic-saturated rows the
  r - 1 branch attains it within sqrt(2) so k > 2 is closed by arithmetic;
  on unsaturated rows the q-smooth parts of Phi_k(r) (k in {3,4,6,8,12},
  primes l = 1 mod k only) decide PHIK_NEVER_BEST vs PHIK_BEST at
  c_k in {1, k} beside a 200-prime null arm | novelty `adaptation` (Satoh
  and Kim-Cheon abstracts retrieved; nearest KN entries internal) | cost:
  implementation low, compute low (trial division to 2^30 in residue
  classes) | first test: the zero-run ceiling table plus C-K12 (k = 1, 2
  must reproduce the census lattices restricted to 2^30).
- **IDEA-20260930-704e43** | class `algorithm` | claim: on toy curves
  (40-64-bit r, planted 2^16 | r - 1, toy SRS of 2^16 powers) the
  memory-charged Cheon r - 1 branch (stage 1 as vOW parallel collision
  search with DPs, stage 2 as a kangaroo) has gain
  G = 0.936 sqrt(d)/(a c_step) within a factor 2 against rho measured on the
  same curve, with a in [1.0, 1.6] and c_step/log2 r in [1/8, 1.5]; a
  safe-prime null must give G <= 0.5 | novelty `unverified` | cost:
  implementation medium (about 600 lines), compute low (10-50 CPU-hours) |
  first test: construct the curves, run C-RHO and C-D1 (d = 1 through the
  Cheon pipeline) on all sizes before any planted number is read.

## Ranking rationale and the one recommended first test

Expected information gain per unit cost: 68326c first (one session, both
outcomes publishable, and it is the consumer that makes the queued census
interpretable); 704e43 second (it is the goal's completion criterion 4 and
decides 68326c's undecided band; its negative outcomes are as useful as its
positive); 6bde2d third (its deployed-parameter bearing is settled by
arithmetic on the only rows with supply; its open content is
hypothetical-supply). None moves an exponent; the lane's honest ambition is
a decisive, certificate-bearing verdict per (curve, supply) cell in group
operations, which is what RQ-AUXIN-f8d8c0 asks for. The exponent-first
record in the BRIEF's sense is 6bde2d, whose content is a method ceiling
for the whole family under supply.

**Recommended first test: IDEA-20260930-68326c's first deliverable** -- pin
the six S1 artifacts (four Ethereum setups, Sapling, PPoT) with hashes and
emit the zero-run R table at both bracket ends. It costs one session, runs
nothing, and already separates the roster into BELOW_RHO, INERT and
STEP_UNIT_DEPENDENT cells before any factoring or implementation; it is the
cheapest valid discriminator because the pre-registered verdicts are fixed
in the record and a single mismatch falsifies the priced claim.

## Honest accounting (docs/inventor-protocol.md section 5)

- Objects considered: (i) the typed supply tuple per deployed instantiation
  joined with the census's divisor lattice; (ii) the q-smooth part of
  Phi_k(r) restricted to primes l = 1 mod k; (iii) the constant pair
  (c_step, a) of the memory-charged implicit-group walk. Rejected as
  objects this session: a re-proposal of the untyped supply count
  (ledger/ideas/IDEA-20260831-ccb587.yaml already holds it); any
  ordinary-input acquisition interface (DEC-20260802-204 B032-C7 gate, out
  of this question).
- `dominated_by`: 68326c -- on the ordinary-input axis, parallel rho
  (KR-RHO-13bf67/825bca); on the auxiliary-input axis, Cheon's own rho/DP
  form (DEC-20260802-204 B032-C6, KN-LIT-6736), which it prices rather than
  improves; possible G_T index-calculus dominator on pairing curves named,
  unresolved. 6bde2d -- "n/a (no result claimed)"; k > 2 branches dominated
  on saturated rows by Cheon's r - 1 branch. 704e43 -- "n/a (no result
  claimed)"; dominated by rho at d = 1 by construction. All checked against
  every row of context/frontier-map-generic-rho.md.
- `sota_delta`: zero on every ECDLP exponent axis for all three; per-cell
  constant factors (estimated 2^1.5-2^9 at PPoT/Sapling, none at the
  Ethereum setups) are estimates from a declared bracket, not measurements.
- Enumerated closures: one, conditional and arithmetic -- on rows with
  v_2(r - 1) >= floor(log2 q_max) the Phi_k (k > 2) axis cannot add more
  than sqrt(2) under any supply cap (named obstruction: the family ceiling
  sqrt(d) <= sqrt(q_max) plus the r - 1 attainment; forward guidance:
  non-generic G_T algorithms are the remaining class). The recalled
  Boneh-Boyen generic bound would upgrade it to a generic sandwich and is
  flagged as a retrieval task, not asserted.
- Open directions for the next session: pin the Filecoin and Aztec
  ceremony transcripts; read Satoh's full paper for c_k and Kim-Cheon for
  tau_f <= deg f; file the Cheon 2006/2010 and Takenaka-Yasuda PKC 2012
  sources as KN-LIT records (RQ-AUXIN-f8d8c0 constraint 3 gates every
  design in this lane on it) and file KN-LIT entries for Satoh 2009/058,
  Kim-Cheon 2012/609 and Jao-Yoshida 2009/221 so later records can use them
  as `nearest`; price the S2 (query-derived) channel per deployment once an
  issuance bound can be cited; check whether TNFS in G_T on BLS12-381
  dominates any BELOW_RHO cell.

## Completion-gate self-check

- Deliverables exist and each proposal file has a single top-level `idea`
  mapping whose `id` equals the file name; list items and metric strings
  containing `": "` were quoted so no plain scalar parses as a nested
  mapping (checked by grep after writing).
- No path outside the write scope was written; no existing record was
  edited (the three proposal files were created by this task; the
  truncated first write of 68326c was replaced in full before anything
  else was written; the returned-once fix rewrote only the three proposal
  files and this report).
- Every number is re-derived in the record from a stated bracket or
  retrieved size and labelled estimate, or marked recalled/unchecked
  (the 2-adicities 32 and 28, the Sapling power count 2^22 - 1, the
  Filecoin/Aztec sizes, the G_T TNFS cost).
- Every citation carries provenance; `verified_by: null` exactly on the
  recalled entries; every `prior_art.nearest[].ref` is a KN-* or KR-* id.
- Each record states time and memory exponents against the memory-charged
  rho baseline of the same curve (KR-RHO-825bca constants, KR-RHO-7d93f6
  bound) and prices the kangaroo stage rather than assuming it.
