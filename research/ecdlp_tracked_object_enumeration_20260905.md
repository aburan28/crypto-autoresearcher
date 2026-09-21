# ECDLP tracked-object enumeration -- sourcing report

Task: `TASK-20260905-f8563d` (coordinator -> idea-generator). Deliverable 1 is
`knowledge/techniques/KN-TECH-ee6696.md`; this file is deliverable 2. Date
2026-09-05. Corpus reads only; no web search, no compute, no ledger status
change, no new identifiers, no candidate object proposed, no existing file
edited.

## 1. What was read

### 1.1 Handoff inputs, all read in full

| path | what it supplied |
|---|---|
| `knowledge/open-problems/KN-OPEN-019.md` | the question, its three outcomes, its four-family sketch labelled possibly wrong |
| `knowledge/techniques/KN-TECH-056.md` | component 7 form (object, operation, obstruction, forward guidance); the closure standard |
| `docs/inventor-protocol.md` | sections 1, 2, 4, 5 -- object-first generation, lossy-projection test, closure standard, honest-accounting block |
| `docs/object-frame-ideation.md` | the frame table of committed results; the F1-F7 off-limits restatement; the note that this task is the enumeration it waits on |
| `ledger/proposals/IDEA-20260802-002.yaml` | the F1-F7 family list with each family's tracked object named; the `(L, b)` meter; `no_power_against` blind spots |
| `ledger/proposals/IDEA-20260806-c5d183.yaml` | orbit argument (A); trichotomy (B) with per-class cost obligations; honest prior naming objects that are not instance projections (advice string) |
| `ledger/proposals/IDEA-20260807-df906f.yaml` | congruence form of rigidity; escapes E1-E4; E3 placing lossy objects on `E[ell]`; E4 naming rho |
| `ledger/proposals/IDEA-20260815-f558e4.yaml` | Cauchy-Davenport strict-rate zero; Vosper bridge as declared debt; quantifier-order statement that a uniform majority ceiling is false |
| `ledger/proposals/IDEA-20260901-863e36.yaml` | block-system classification (C1); translation slice (C2); orbit partitions (C3); generic `c_can` bound (C4); morphism-induced forms (C5); open cell (C6) |
| `ledger/hypotheses/H-TLD-f4c8ba.yaml` | the typed generator; baseline embedding "F1-F7 typed by hand once" |
| `knowledge/findings/KN-FIND-ffe1df.md` | Theorem C and the sentence recording its validator confirmation; the entry's own promotion-chain gap; item 2 on the dlog-interval pullback and the cost clause |
| `knowledge/open-problems/KN-OPEN-020.md` | bounded-degree scoped negative; open classes; "formal complexity class" as required next result |
| `knowledge/open-problems/KN-OPEN-003.md` | representation question for decomposition cost |
| `ledger/questions/RQ-ECDLP-623a32.yaml` | R1/R2/R3 representation classes; Kummer-line closure at model lever 1 |
| `knowledge/README.md` | frontmatter schema |
| `agents/idea-generator.md` | search bias 6, including the sentence "Index calculus lives in the branching class" |

### 1.2 Additional committed records consulted, and how each was found

Found by Glob/Grep over `knowledge/` and `ledger/` for the family names, then
read (in full unless noted). Each was consulted because a handoff input cited
it or because a table row needed a committed obstruction the inputs did not
carry.

| record | found via | read | used for |
|---|---|---|---|
| `KN-TECH-00f082` | handoff (frontmatter model) | full | frontmatter shape only |
| `KN-TECH-001`, `KN-TECH-006`, `KN-TECH-031`, `KN-TECH-005`, `KN-TECH-030` | title grep `Pollard|rho|BSGS|generic group` | full | F1 object, operation, obstruction |
| `KN-FIND-007`, `KN-TECH-003`, `KN-OPEN-001` | title grep `factor base|index calculus|Semaev` | full | F2 obstruction and open items |
| `KN-FIND-002`, `KN-FIND-b7e091`, `KN-OPEN-005` | cited in c5d183 / 863e36 | full | F2 incidence overhead; F6 simulability findings; Class III openings |
| `KN-TECH-032`, `KN-FIND-3a7d42` | title grep `MOV|pairing|embedding degree` | full | F4 |
| `KN-TECH-033`, `KN-TECH-059`, `KN-TECH-06bb4e`, `KN-TECH-73630e`, `KN-OPEN-3417fc` | title grep `anomalous|p-adic|formal group`; then the records those cite | full (`73630e` to line 70, which is its end of substantive text) | F5 |
| `KN-TECH-018` | title grep `automorphism|GLV` | full | F6 |
| `KN-LIT-013`, `IDEA-20260806-3b91c7` | cited in `KN-TECH-005` and in c5d183's `dominated_by`; `3b91c7` read lines 1-60 plus a grep for `preprocess|S*T^2` | partial | F7 |
| `IDEA-20260727-005` | cited in c5d183 `discriminated_from` | lines 1-82 (claim and start of mechanism) | exit-map classes E1/E2/E3 placed against F4, F5, F3, F6 |
| `IDEA-20260807-053a55`, `IDEA-20260807-631e80` | named in df906f escape E3 | `053a55` claim block (lines 13-82); `631e80` title only | F3 object, operation, obstruction |
| `RQ-JMV-001` | grep `ISADV` in `ledger/` surfaced it (the KN-LIT-013 pointer); title grep for Jao-Miller-Venkatesan in `knowledge/` returned nothing | lines 1-45 | F3 open item |
| `KN-TECH-3b593f`, `KN-FIND-61347e` | title grep `isogen`; `61347e` from the rho title grep | `3b593f` full; `61347e` lines 1-45 | F3 obstruction column |
| `KN-OPEN-010`, `EV-TRA-001` (file `ledger/EV-TRA-001.yaml`) | c5d183 forward guidance cites the transfer-operator lane | full | F1 branching relative |
| `H-PROP-c95932` | cited in 863e36 | full | E2 exact/probabilistic split |
| `KN-OPEN-011`, `KN-OPEN-018` | cited in KN-OPEN-019 | titles only (from grep) | the HNP sketch item, not tabulated |
| `KN-LIT-7594`, `KN-LIT-7595`, `KN-LIT-7601` | cited in KN-OPEN-019 / KN-TECH-056 | existence verified by Glob; content taken as quoted in those two entries | cautions |
| `IDEA-20260806-071255`, `RQ-ECDLP-002`, `RQ-TORS-8c7b79`, `RQ-PROP-24458b`, `EV-FBG-001`, `DEC-20260724-007`, `EV-GGM-001`, `DEC-20260726-007`, `EV-GGM-79e710`, `DEC-20260804-3b4258` | existence verified by Glob because a cited entry names them | not read | cited only as the provenance a finding states for itself |
| `tools/build_knowledge_index.py` | completion gate | full | confirmed the parser: `yaml.safe_load` of the frontmatter, `tags` joined as a list, quoted title required because of embedded colons |

Ids deliberately **not** cited because they were not verified or their
content was not read: `KN-LIT-084/085/086/087/088/089` (relayed inside the
technique entries), `DEC-20260902-4c82fd` and `DEC-20260901-d599ae` (named
in `KN-FIND-61347e`), `EXP-TLD-0a6b4d` and `EXP-PROP-ba2e44` (directories
exist but their specifications were not read), `KN-LIT-6935a1`, `KN-TECH-025`,
`KN-TECH-026`, `KN-LIT-764`, the `ECDLP-IDEA-*` legacy ids, and the
`ideas/catalogue-20260805/*` pre-ledger files.

## 2. How each row was sourced

Columns: object / operation / discards / trichotomy / obstruction / open.

- **F1.** Object and family label verbatim from `IDEA-20260802-002`; walk
  state and step from `KN-TECH-001`, `KN-TECH-006`; BSGS equality test from
  `KN-TECH-031`. "Discards nothing" is the reading that the projection is the
  identity on `G`, with `IDEA-20260807-df906f` E4 supplying the sentence that
  rho tracks a collision, not a congruence. Class "none because injective"
  follows from `IDEA-20260806-c5d183` (A). Obstruction: `KN-TECH-005`
  (established), `KN-TECH-006`, `KN-TECH-031`, and the frontier of
  `IDEA-20260806-3b91c7` (proposal). Open: `EV-TRA-001` numbers (`L = O(1)`,
  `delta = 0.0195`, `preliminary`, `x`-interval partitions, `n <= ~4200`) and
  `KN-OPEN-010`; c5d183 guidance (a).
- **F2.** Object from `IDEA-20260802-002` and `KN-TECH-003`. Operation:
  c5d183's Class I sentence "propagates deterministically only under
  translation by FACTOR-BASE elements". Class: partial-action per c5d183, with
  the `agents/idea-generator.md` bias-6 discrepancy recorded. Obstruction:
  `KN-FIND-007` at its stated tier (`derivation`, `toy`, `N <= 2^18`, `m = 3`,
  headroom `<= 1.582`), `KN-OPEN-001`, `KN-OPEN-020` (`confidence:
  unverified`), and c5d183's CM-lane residue. Open: `KN-OPEN-020` open
  classes, `KN-FIND-007`'s own "what this does not say", `KN-OPEN-003`,
  `KN-FIND-002` incidence overhead.
- **F3.** Object from `IDEA-20260802-002` (graph-level) and
  `IDEA-20260807-053a55` (A) (point-level transported instance); operation
  from `053a55` and the title of `IDEA-20260807-631e80`. Discards: the
  kernel-or-injective dichotomy `053a55` (B) and df906f E3. Class: none
  because injective, with the curve-level caveat taken from c5d183's honest
  prior. Obstruction: `053a55` (B)-(C) (proposal), `IDEA-20260727-005` (C3)
  (proposal), `KN-FIND-61347e` (finding, derivation), `KN-TECH-3b593f`
  (derivation). Open: `RQ-JMV-001` G1-G3; `631e80` mixing constant.
- **F4.** Object from `IDEA-20260802-002` and `KN-TECH-032`. Operation: the
  pairing is a homomorphism (`KN-TECH-032`), then finite-field index calculus.
  Discards nothing: `KN-FIND-ffe1df` Theorem C plus non-degeneracy
  (`KN-TECH-032`). Class: none because injective; `IDEA-20260727-005` E2.
  Obstruction: `KN-TECH-032` (established; Balasubramanian-Koblitz relayed
  from a secondary restatement, as that entry says), `KN-FIND-3a7d42`
  (`k ~ N/2`), `IDEA-20260727-005` (C3). Open: `KN-TECH-032` screening rule;
  `IDEA-20260727-005` falsifier (a).
- **F5.** Object from `IDEA-20260802-002`, `KN-TECH-059`, `KN-TECH-033`.
  Operation: formal logarithm as homomorphism and its convergence domain
  (`KN-TECH-059`). Discards nothing group-theoretically: `KN-TECH-73630e`.
  Class: coordinate-dependent, c5d183 Class III names "p-adic lifts"
  verbatim. Obstruction: `KN-TECH-033`/`KN-TECH-059` (established),
  `IDEA-20260727-005` E1 (proposal), `KN-TECH-06bb4e` faces
  (literature-derived), `KN-TECH-73630e` (derivation). Open:
  `KN-OPEN-3417fc`; `KN-TECH-06bb4e` F5 face and F4a analogue.
- **F6.** Object from `IDEA-20260802-002` and `IDEA-20260901-863e36`
  (`object_first_candidate`). Operation and discards from `863e36`
  (`mechanism`, `lossiness`, `propagation`). Class: partial-action, `863e36`
  (C1)/(C3); its `discriminated_from` names it an E4 inhabitant. Obstruction:
  `KN-TECH-018` (established), `863e36` (C4)-(C5) (proposal, conditional on
  `KN-TECH-005`), `IDEA-20260727-005` (C1) (proposal), `KN-FIND-002` and
  `KN-FIND-b7e091` with the three-defects caveat `863e36` records. Open:
  `863e36` (C6).
- **F7.** Object from `IDEA-20260802-002`, `IDEA-20260806-3b91c7` (B),
  `KN-LIT-013`. Operation from `3b91c7` (B). Discards / class: c5d183's
  honest prior sentence about "the preprocessed advice string" -- not
  placeable. Obstruction: `KN-LIT-013` (reported, abstract-relayed) as
  recorded in `KN-TECH-005`; `3b91c7` frontier (proposal). Open:
  `KN-LIT-013`'s non-generic clause.

## 3. Gaps found in the corpus

Each is a place where the enumeration wanted a committed record and found
none, or found two that disagree. Written as gaps; none is filled here.

1. **F3 has no `KN-*` obstruction for the plain isogeny-walk family.** The
   corpus closes two higher-dimensional mechanisms (`KN-TECH-3b593f`), the
   cross-genus embedding (`KN-FIND-61347e`), and the abelian-variety exit
   class at proposal tier (`IDEA-20260727-005`), and states the kernel-or-
   injective dichotomy at proposal tier (`IDEA-20260807-053a55`). The
   Jao-Miller-Venkatesan random self-reduction on ordinary prime-field
   curves -- the family `KN-OPEN-019`'s own sketch means by "paths in an
   isogeny graph" -- has a research question (`RQ-JMV-001`) and research
   notes under `research/JMV*`, but no `KN-*` record naming what stops it or
   confirming that within-level dlog cost is constant. **This is the largest
   single gap**: it is the one family whose obstruction column rests entirely
   on proposal-tier and adjacent-lane records.
2. **F7 does not fit the trichotomy.** The advice string is not a projection
   of a group element; `IDEA-20260806-c5d183` says so in its own honest prior
   and suggests a fourth bucket it does not define. No committed record
   supplies that bucket, and no record names a non-generic advice object or
   its obstruction (`KN-LIT-013` only says one would have to beat
   `S*T^2 ~ N`).
3. **F2's trichotomy class was stated two ways -- RESOLVED 2026-09-05.**
   `IDEA-20260806-c5d183`: partial-action (Class I). `agents/idea-generator.md`
   search bias 6, as read at the start of this session: "Index calculus lives
   in the branching class." The discrepancy was found by this synthesis and
   resolved by the coordinator on 2026-09-05 by correcting bias 6, its mirror
   in `.claude/agents/idea-generator.md`, and `docs/object-frame-ideation.md`
   to match `IDEA-20260806-c5d183` (confirmed by re-reading all three); the
   two-step reading -- deterministic propagation of the relation vector under
   the partial action, existence of a decomposition as the branching event the
   `(L, b)` meter prices -- is kept as the reconciliation.
4. **The frame's spine is validator-confirmed in only one of its forms.**
   `KN-FIND-ffe1df` Theorem C is confirmed; the orbit argument, the
   congruence form, the block-system classification and the Cauchy-Davenport
   bound are all `proposed` with novelty `unverified`. Outcome 2 is therefore
   supported at proposal tier, and no committed review has raised it.
5. **`KN-FIND-ffe1df`'s promotion chain is absent** by its own statement
   (`proof_status: derivation`, no `EV`/`DEC` record). The one
   validator-confirmed statement in the enumeration therefore sits in a
   finding whose lifecycle provenance is itself recorded as a gap.
6. **No committed record defines "efficiently computable" for projections.**
   `IDEA-20260815-f558e4`, `KN-FIND-ffe1df` item 2 and `KN-OPEN-020` each say
   the restriction is load-bearing and each says it is not a theorem. Outcome
   3 cannot be attempted without it.
7. **Evidence-id mismatch.** `ledger/EV-TRA-001.yaml` has internal id
   `TRA-EV-001` and hypothesis id `TRA-H-001`; the file sits at the top of
   `ledger/` rather than under `ledger/evidence/`. Its numbers are quoted in
   the entry with this caveat. Not repaired here (no edits permitted, and the
   record is immutable).
8. **The HNP/lattice item of `KN-OPEN-019`'s sketch has no F-row.** It is
   confined to the leakage model (`KN-OPEN-011`, `KN-OPEN-018`) and is not
   named as an ECDLP family by `IDEA-20260802-002`; the entry notes it and
   does not tabulate it.
9. **`IDEA-20260901-863e36` was not machine-parsed at authoring** (its own
   `yaml_parse_disclosure`). It was read here as text; whether it validates
   under `tools/validate_ledger.py` was not checked in this session.
10. **Several established-tier obstructions are relayed from unread
    sources.** `KN-TECH-032`, `KN-TECH-033`, `KN-TECH-005` and `KN-LIT-013`
    each state that their primary papers were not read in full. The entry
    labels them `(est.)` as their frontmatter does and does not upgrade them.

## 4. Completion-gate self-check

- Frontmatter carries `id`, `type: technique`, quoted `title`, flat `tags`
  list, `confidence: reported`, `complexity`, `applicability`, `source_refs`
  list, `added: 2026-09-05`, `superseded_by: null`. The body contains no line
  that the `yaml.safe_load(text.split("---", 2)[1])` call in
  `tools/build_knowledge_index.py` would see, because the split is capped at
  two. The builder was **not executed** in this session (no shell available
  to this role); parseability is asserted from the parser's source, which was
  read, not from a run.
- Every table row and every argument step cites at least one record id
  resolved in this session by Glob, Grep or Read (section 1.2 lists the
  resolution route).
- The entry names outcome 2 as supported, at proposal tier, for the six
  point-level families; names outcome 3 only as a requirement list; claims no
  closure; proposes no candidate object.

## 5. Honest-accounting block (docs/inventor-protocol.md section 5)

- **object(s) considered:** the seven tracked objects of families F1-F7 as
  named by `IDEA-20260802-002` -- walk state with representation `aP + bQ`;
  relation vector over a factor base; vertex/walk in an isogeny graph
  (point-level: the transported instance); image in `F_{q^k}^*`; lift into a
  formal group; orbit representative (`Gamma`-orbit label); precomputed
  advice string -- each paired with the operation set it must survive. No
  object of this session's own.
- **depth of verified structure:** the enumeration is a reading of committed
  records, verified only in the sense that every cited id was resolved and
  every quoted statement was read from its source. Of the rigidity results
  the enumeration rests on, one (`KN-FIND-ffe1df` Theorem C) is
  validator-confirmed at derivation tier; the rest are proposal-tier
  derivations with novelty unverified. Nothing probabilistic was measured;
  nothing deterministic was re-derived. Tier: **synthesis of committed
  records; no new structure verified.**
- **dominated_by:** "n/a (no result claimed)". No point on any ECDLP cost axis
  is occupied. Stated after reading the frontier rows the cited records carry
  (`KN-TECH-005`, `KN-TECH-006`, `KN-TECH-018`, `KN-TECH-031`, `KN-LIT-013`,
  `IDEA-20260806-3b91c7`); none is challenged.
- **sota_delta:** "no attack; methodological synthesis only". Zero on time,
  memory and data/queries. The methodological delta, stated exactly:
  `KN-OPEN-019` moves from "the enumeration has never been written down" to
  "an enumeration exists with a per-family named obstruction at a stated
  tier"; it does not move to any closure.
- **enumerated closures:** none claimed. The entry closes no class, no
  family, and no cell beyond what the cited records already state at their
  own tiers; the only cell any cited record calls closed (lossy and
  fully-translation-deterministic) is closed there, not here.
- **open directions:** the nine forward-guidance classes of the entry --
  (representation, operation set) pairs of search bias 6; the branching class
  under the `(L, b)` meter; the `KN-OPEN-020` open factor-base classes; Class
  III objects surviving simulability at non-constant overhead, including
  `KN-OPEN-3417fc` and the function-field face; F6 arithmetic selectors; F3
  within-class cost variance (`RQ-JMV-001`); F7 non-generic advice; escapes
  E3 and E4 of `IDEA-20260807-df906f`; and, prior to any outcome-3 attempt, a
  formal cost class for projections. For the next session specifically: the
  largest gap (item 1 of section 3) is a curation target, not a research
  target -- a `KN-*` record for the isogeny-walk family's obstruction on
  ordinary prime-field curves, sourced from `RQ-JMV-001`'s lane, would let F3
  carry an obstruction at the same tier as the other rows.
