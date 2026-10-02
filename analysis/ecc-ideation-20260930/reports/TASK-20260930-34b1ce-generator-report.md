# Generator report, lane L2 (ENDO), TASK-20260930-34b1ce

Date 2026-10-01. Idea-generator session on branch `claude/elliptic-curve-goals-3bfz9x`
at `5cd61253a`. Proposals only; no run, no status change, no existing record
edited. No shell was available: every number below is a count of files returned
by the Grep tool or a quantity re-derived in the record that carries it, and the
three YAML files were not machine-parsed by this session (block scalars were used
for every long value; the dispatcher's `tools/validate_ledger.py` is the parse
check).

## Returned once (2026-10-01)

The dispatcher returned all three records for one schema fix: every
`prior_art.nearest[].ref` must resolve to a KR-* row or a KN-* entry; IDEA-*,
CORR-* and similar ids belong in `citations` / `discriminated_from` /
`source_refs`. What moved, with no change to any claim, mechanism, prediction,
threshold, cost or novelty_status:

- **IDEA-20260930-39ad61**: `nearest` entries `IDEA-20260811-b3a355` and
  `IDEA-20260807-a127ab` removed (both were already in `citations` and
  `discriminated_from`; their citation notes now say so). Replaced by
  `KN-LIT-013` (Corrigan-Gibbs--Kogan, retrieved; relation adjacent) and
  `KR-RHO-46c2c6` (multi-target amortisation; adjacent). New `nearest` refs:
  KR-RHO-ea34b8, KN-LIT-013, KR-RHO-46c2c6, KR-RHO-755e35.
- **IDEA-20260930-5b9e0d**: `nearest` entry `IDEA-20260808-fa1d80` removed
  (already in `citations` and `discriminated_from`; citation note updated).
  Replaced by `KN-TECH-026` (Kani glue-and-split; adjacent, carrying the
  degree-is-the-secret delta). New `nearest` refs: KR-IC-081a58,
  KN-TECH-febb4f, KN-TECH-026, KR-RHO-13bf67.
- **IDEA-20260930-655544**: `nearest` entries `IDEA-20260815-a5a19f`,
  `IDEA-20260807-1c14d7`, `CORR-20260810-6e4fa7` removed; a5a19f and 1c14d7
  added to `citations` (internal, with what was read), CORR already there;
  1c14d7 added to `discriminated_from`. Replaced by `KN-TECH-056` (inventor
  protocol: controls before belief / closure standard; adjacent) and
  `KN-OPEN-019` (saturation claims are claims about the search; adjacent);
  both added to `source_refs`. `frontier_map: not_applicable` kept with its
  reason extended. New `nearest` refs: KN-TECH-056, KN-OPEN-019.

Every replacement id was confirmed to exist by Glob before writing
(`knowledge/frontiers/ecdlp/generic-rho/KR-RHO-46c2c6.yaml`,
`knowledge/literature/KN-LIT-013.md`, `knowledge/techniques/KN-TECH-026.md`,
`knowledge/techniques/KN-TECH-056.md`, `knowledge/open-problems/KN-OPEN-019.md`,
plus the KR rows already cited). `rows_checked` lists are unchanged and KR-only.
The dispatcher's own count (277 proposals / 159 hypotheses across the goal's
fifteen lane questions) supersedes this session's nine-lane tally as the
corpus-wide figure; the nine-lane numbers in 655544 are left as stated because
they are the quantity that record claims and the dispatcher's count includes the
five lanes the extract did cover.

## Identifiers

| id | used | filed under | class |
| --- | --- | --- | --- |
| IDEA-20260930-39ad61 | yes | RQ-MTGT-2cabee | composition |
| IDEA-20260930-5b9e0d | yes | RQ-GGMB-6eaabc | mechanism (oracle-class classification) |
| IDEA-20260930-655544 | yes | RQ-INSTR-f8faa0 | tooling |

No spare id was requested. All three ids were pre-minted by the dispatching
session (BRIEF.md section 5) and none was minted here.

## One-line summaries

- **IDEA-20260930-39ad61** (composition, RQ-MTGT-2cabee). Claim: the transport
  step of the one-table-per-class attack has its own preprocessing axis -- a
  Bernstein-Lange distinguished-point table on the crater torsor lowers the
  per-curve path-finding charge from sqrt(h) = p^{1/4} (b3a355, 48b364) to
  sqrt(h/S_c), i.e. p^{1/6} at S_c = p^{1/6}, on a composite frontier
  (S_g T_g^2 = N) x (S_c T_c^2 = h) whose class-side term binds only when
  S_g > L^2 N^{1/2} S_c; per-target exponent unchanged (Corrigan-Gibbs--Kogan);
  crater oracle generic-group-action simulable. novelty_status unverified.
  Cost: implementation medium, compute low. The one open number is the merge
  exponent alpha of a hash-directed walk on a Cl(O_K)-torsor against stored
  endpoints, measured against relabelled Z/hZ, wrong-walk, random-vertex,
  identity and alpha-mixture controls.
- **IDEA-20260930-5b9e0d** (mechanism, RQ-GGMB-6eaabc). Claim: for the rational
  cyclic kernel Gamma = <(P, Q)> in E x E, the quotient VARIETY is (E/G) x E for
  every k (one unipotent automorphism), so every isomorphism invariant is a
  constant oracle -- cell (a) of IDEA-20260807-5876b8, simulable, closed at 1/2;
  the quotient MAP on any product model returns [uk]R on (R, 0) for a known
  unit u, is a static Diffie-Hellman oracle, non-simulable, cell (c), and
  cascades through Cheon to about 1.9 N^{1/3} C^{1/3}, so any o(N^{1/2})
  evaluation of a prime-order cyclic quotient of an abelian surface from its
  generator is a sub-sqrt ECDLP on Cheon-friendly N; the known cyclic-kernel
  floor (Velu O(N), square-root Velu O~(N^{1/2}) in dimension 1) exactly ties
  rho, and the Kani route needs deg [k] = k^2, which is the secret.
  novelty_status unverified. Cost: implementation medium, compute low.
  Exponent-first in ambition (the conditional N^{(1+c)/3} is stated), honest
  expected outcome a method ceiling.
- **IDEA-20260930-655544** (tooling, RQ-INSTR-f8faa0). Claim: the lane-context
  extract `context/L2-ENDO.md` lists zero proposals and zero hypotheses for
  nine of the goal's fourteen lanes while the ledger holds 141 proposals and
  76 hypotheses with `question_id` in those nine (grep this session; per-lane
  counts in the record), so the brief's "several lanes with no proposal at all"
  was an instrument false negative; specify the extractor as a literal reader
  of the goal head's `question_ids` with planted / null / exact-regression /
  baseline controls. novelty_status unverified. Cost: low / low.

## Recommended first test

**IDEA-20260930-655544, Stage 0**: re-run the stated grep at the base commit and
compare with the nine per-lane counts, then check extract-versus-grep equality on
the five explicitly named lanes. It is zero-compute, it either confirms or
corrects a number that every overlap_review on this goal now depends on, and it
should precede any ranking of the other two records (whose overlap reviews were
done by literal grep precisely because the extract could not be trusted). Of the
two research records, the cheapest valid discriminator is **IDEA-20260930-5b9e0d
Stage 2** (Cheon with a cheating map-level oracle must recover k at the predicted
cost; with the variety-level oracle it must fail): minutes of compute, both
directions of the RQ-INSTR-f8faa0 control in one run, and it fixes the C3
classification of a new oracle class regardless of outcome.

## Ranking rationale (expected information gain versus cost)

655544 first: near-zero cost, and its outcome changes what the next ideation
round on this goal may claim. 5b9e0d second: low cost, a C3 deliverable either
way, and it names the exact algorithmic event (sub-sqrt cyclic-kernel evaluation
in dimension 2) that would move an exponent, with the obstruction that blocks the
only known route. 39ad61 third: medium implementation cost, and its exponent
claim lives on the per-curve transport axis, which claim (C) of the record shows
is lower-order at the standard Bernstein-Lange operating point; its toy
measurement (does a torsor walk merge like a group walk?) is nonetheless the only
quantity in the goal's T5 reachability lane that has never been measured.

## Lane choices and why

The card asked to prefer lanes the extract shows as empty. The extract shows nine
lanes empty; a literal grep shows all nine populated (MTGT 17, CLGP 18, TORS 13,
EWALK 16, VOLC 21, EQIC 12, EQLA 13, CANL 16, MODEL 15 proposals). Two candidates
drafted on the extract's guidance were dropped as verbatim duplicates found only
by grep:

- TORS: the Hom(Z/N, ell-primary module) = 0 closure of point-dependent torsion
  data, with the composite-order Pohlig-Hellman positive control -- this is
  IDEA-20260807-6eab6a and its specified hypothesis H-TORS-9851f8 (read in full);
  the follow-on observation that the ell-fibre product over E[ell]-translates is
  affine in x([ell]P) is the "torsion-translate norm factors through [ell]" claim
  of IDEA-20260905-809a81 / -b0d6bb.
- MTGT: one Bernstein-Lange table per isogeny class with mode-B pull of the two
  targets -- IDEA-20260807-a127ab verbatim; the DP-store-does-not-transport half
  is IDEA-20260807-e0ddc6 and IDEA-20260830-3e38ce.

A third candidate, a product-surface bridge for RQ-CLGP-b99df5, was found to have
a neighbour (IDEA-20260808-fa1d80, Lagrangian split-quotient certificate) and was
rewritten as the oracle-class classification 5b9e0d under RQ-GGMB-6eaabc, with the
delta against fa1d80 stated in the record (rational cyclic kernel; variety level
provably k-free; k located in the map as a static DH oracle; Cheon threshold).

The remaining lanes were screened at title level and found dense: EWALK (16;
ebcae6 states the sqrt(|Aut|) ceiling as a theorem, 18d2f7 the quotient ladder,
506ba2 the (m, kappa) tradeoff, 06cc5d multiplier mixing); VOLC (21; 7b8856 depth
as one public scalar, 48b364 depth as a discount, cbe8c1 torsion versus level);
EQIC (12; 5dfe4a and 45a69f close the rank and non-unit cases); EQLA (13; 9ecc6f
commutant closure, 0e4d83 informative rank); CANL (16; dbb250 p-adic heights
vanish, cfe576, 6533fd); MODEL (15; dadcd2 deck-group law, fe0934 model existence
varies by level, a22049 B(i)); RQ-ECDLP-912694 (5 proposals, 6 hypotheses;
882739 and c49409 answer the exit question). No restatement of any of these was
filed.

## Records read for overlap (beyond the context file)

In full or claim section: IDEA-20260807-a127ab, IDEA-20260811-b3a355,
IDEA-20260901-48b364, IDEA-20260807-0e8977, IDEA-20260807-e0ddc6,
IDEA-20260807-5876b8, IDEA-20260808-fa1d80, IDEA-20260806-0c9de1 (claim A-C),
IDEA-20260905-809a81, IDEA-20260807-df906f (claim A-D), IDEA-20260801-007,
IDEA-20260807-4f43ac (lines 298-313), IDEA-20260806-c5d183, IDEA-20260901-863e36,
IDEA-20260802-002, IDEA-20260926-89886c (form exemplar), H-TORS-9851f8,
KN-FIND-b7e091, KN-FIND-ffe1df, KN-TECH-018, KN-TECH-061, KN-TECH-febb4f,
KN-TECH-026 (header and method), KN-TECH-056 (header), KN-LIT-6501 (header),
KN-LIT-013 (header), EV-IT-511f3d, EV-ENDO-001, KN-OPEN-003/005/019/020,
DEC-20260913-515d80 (lines 28-62), DECOMPOSITION.md, docs/object-frame-ideation.md,
docs/inventor-protocol.md, agents/idea-generator.md, templates/research-records.md
(prior-art and citation sections), both frontier maps, all fourteen lane question
records. At title level: all 141 proposals under the nine lanes, the 104
proposals and 77 hypotheses in the context file.

## Searches run

Corpus (Grep): `question_id: RQ-(TORS|CLGP|MTGT|VOLC|EQIC|EQLA|EWALK|CANL|MODEL)-...`
over ledger/; `Kummer (map|cocycle|sequence|theory)|division field|ell-division|Tate
pairing...`; `(precomput|preprocess).{0,160}(isogen|transport)` and converse;
`Kani|E x E|abelian surface|unipotent|gluing`; `graph of [k]|(P, Q) in E x E|E x E
...(kernel|quotient|glu)|Kummer surface|abelian surface...(ECDLP|discrete log)`;
`Cheon|static DH|static Diffie|strong Diffie|k^i P`; `(distinguished|precomput|
preprocess|advice|table).{0,120}(crater|class[- ]group|vectori[sz]|isogeny path)`
and converse; title extractions per lane by explicit file lists; `Kummer|cocycle|
H^1` over the TORS/VOLC hits. The crypto-kb index was empty (BRIEF section 0) and
was not called. On return: Glob existence checks for every replacement
`nearest` id.

Web (WebFetch, abstracts read): eprint 2017/1113 (Corrigan-Gibbs--Kogan, S T^2 =
Omega~(eps N)); eprint 2012/458 (Bernstein--Lange, 1.77 l^{1/3} online after
1.24 l^{2/3}); eprint 2020/341 (Bernstein--De Feo--Leroux--Smith, O~(sqrt(ell))
cyclic-kernel evaluation); eprint 2004/312 (Jao--Miller--Venkatesan, random
reducibility under GRH). Two guessed ids returned unrelated papers (2006/193,
2005/069) and were not used. No WebSearch was run; the group-action-preprocessing
and torsion-point-attack literatures are cited as recalled only.

## Honest accounting (docs/inventor-protocol.md section 5)

- **Objects considered.** (i) The basin map of a hash-directed walk on the crater
  torsor paired with Sigma = {oriented small-prime step, group-side transport}:
  Class I partial action, lossy, open number = merge exponent (39ad61). (ii) The
  isomorphism class of (E x E)/<(P, Q)> and the second product coordinate of the
  quotient map, paired with Sigma = {the quotient isogeny, product automorphisms}:
  constant and injective respectively, so neither is a lossy object, which is the
  finding (5b9e0d). (iii) The ell-fibre of P over E[ell]-translates (dropped:
  affine in x([ell]P), hence a coordinate change, and already filed). (iv) The
  per-lane id set of the overlap extract (655544; not a group object, stated so).
- **dominated_by.** 39ad61: per target, ties Bernstein-Lange (KR-RHO-ea34b8),
  dominated by rho on memory; per curve, dominates the program's own p^{1/4}
  charge only in exchange for class-side memory and only under H1; "n/a (no
  per-target result claimed)". 5b9e0d: "n/a (no result claimed on any cost
  axis)" after checking KR-RHO-755e35/0528e7/53c89f/13bf67/6239aa and
  KR-IC-081a58/cd159a/5931ee. 655544: "n/a (no result claimed)". No null was
  entered anywhere.
- **sota_delta.** Zero on every ECDLP cost axis for all three. Quantified
  program-level deltas: a class-side (S_c, T_c) axis with per-curve exponent 1/4
  -> 1/6 at S_c = p^{1/6}, conditional on H1 and leading only when
  S_g > L^2 N^{1/2} S_c; one new oracle class classified in both readings with
  threshold C = o(N^{1/2}); one measured instrument false negative of 141
  proposals and 76 hypotheses.
- **Enumerated closures (mechanisms named).** (a) Variety level of the rational
  graph quotient carries no k: the unipotent (x, y) -> (x, y - [k]x) maps the
  kernel to G x {O}. (b) The Kani route to [k] is blocked because its required
  input, the degree k^2, is the secret, and the rational torsion N is below it.
  (c) The point-dependent ell-torsion closure and the ell-fibre coordinate change
  are already filed (6eab6a, 809a81) and are cited, not re-derived. (d) The
  extract-based "empty lane" claim is closed by a count.
- **Open directions for the next session.** (1) Whether a cyclic-kernel
  square-root-Velu analogue exists in dimension 2 -- the only event that moves
  5b9e0d's threshold; a literature search (not run here) should precede any
  compute. (2) The merge exponent of torsor walks (39ad61 Stage 3) as a general
  T5 quantity for the whole goal. (3) After 655544's corrected extract exists,
  a genuine re-screen of the nine lanes at claim level, which this session did at
  title level only; the brief's "prefer empty lanes" instruction should be
  re-issued or withdrawn on that basis. (4) RQ-CLGP-b99df5 still lacks a record
  on higher-dimensional bridges; 5b9e0d covers the oracle side and leaves the
  vectorization side untouched, as its interpretation_limits say.

## Completion-gate self-check

- Deliverables: the three proposal files and this report exist; each proposal is
  a single top-level `idea:` mapping with `id` equal to the file name. Not
  machine-parsed here (no interpreter); long values are block scalars; one plain
  scalar containing ": " was found on self-review and the file was rewritten
  with a block scalar before hand-off.
- Write scope: only the four declared paths were written (and rewritten on
  return); nothing existing was edited.
- Every number re-derived or marked: the Bernstein-Lange constants and the CGK
  bound are quoted from fetched abstracts; the torsor law, the composite binding
  condition, the unipotent argument, the unit ambiguity and the Cheon optimum
  1.9 N^{1/3} C^{1/3} are derived in the records; the 141/76 counts are this
  session's tally of grep output at 5cd61253a and are stated as such.
- Schema: `added: '2026-10-01'` per the dispatcher's instruction (overriding
  BRIEF section 3's example date); `origin.date '2026-10-01'`; prior_art with
  KR-only `rows_checked` including the four mandatory rows on every record and,
  after the return, `nearest` refs that are all KR-*/KN-* ids; object frame,
  trichotomy, lossy-projection test and simulability stated on each (655544
  states non-applicability with the reason, as the card permits).
- Flags for the dispatcher: 655544 is a tooling record under an audit lane and
  carries `frontier_map: not_applicable`; the dispatcher's `build_frontier_map
  --match` is expected to return KR-RHO-ea34b8 for 39ad61 and KR-RHO-13bf67 or
  KR-IC-081a58 for 5b9e0d, both cited.
