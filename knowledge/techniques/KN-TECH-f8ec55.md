---
id: KN-TECH-f8ec55
type: technique
title: An amendment that replaces text in a machine-readable contract must carry a control that parses the result and asserts its CONTENT, not only its shape
tags: [amendment, machine-readable-contract, protocol-amendment, parse-control, splice, yaml, negative-object, entailed-check, control-design, governance, methodology, provenance, immutability]
confidence: reported
complexity: >-
  not a cost model - a design rule for the control that accompanies a textual
  amendment to a machine-readable contract. The operative quantity is which of
  the control's assertions can DISTINGUISH the amended document from the
  unamended one; a control whose assertions are all satisfied by the file it
  exists to detect the amendment of measures nothing, whatever its exit code
applicability: >-
  every proposed amendment that replaces or inserts literal text at a locator in
  a machine-parsed contract, specification, manifest or configuration that other
  records, runs and reviews are read against - and, by extension, any check
  whose pass could be entailed by the construction of its own input
source_refs: [EV-SSI-0a57ab, EV-SSI-804e09, DEC-20260906-408595, DEC-20260906-f709b2, TASK-20260906-ee372e, TASK-20260906-ba0284, TASK-20260906-dc4905, TASK-20260906-918585, EXP-WESOVOW-001]
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/tasks/TASK-20260906-ee372e/amendment_parse_control.py
  - coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/tasks/TASK-20260906-ee372e/amendment_parse_control_report.yaml
  - coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/reviews/TASK-20260906-ba0284/independent_parse_check.py
  - coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/reviews/TASK-20260906-ba0284/validation_report.yaml
added: '2026-09-06'
superseded_by: null
---

## The rule

**An amendment that replaces text in a machine-readable contract must carry a
control that parses the amended document and asserts both its SHAPE and its
CONTENT.** Shape alone is not enough, and the reason is mechanical rather than
stylistic: the unamended file usually already has the shape the amendment
preserves, so a shape-only control passes on the very file it exists to detect
the amendment of. Its green result then means "this document is a document of
the expected form", not "the amendment was applied".

The control is not a formality attached to the amendment. It is the only thing
standing between a proposed replacement and a contract that no longer loads.

## The failure that motivated it

RT-1 of the `TASK-20260905-6d5c9c` red-team report. A protocol amendment carried
an exact `replacement_text_in_full` for two lines of a frozen YAML experiment
contract. **The replacement did not parse when spliced at the declared indent**
— the draft's continuation lines sat two columns shallower than the anchor
required — and nothing in the amendment package would have caught it. It was
found by a reviewer splicing the text by hand, not by any check the amendment
carried. The amendment was mechanically inapplicable and had been reviewed twice
without anyone noticing.

## The assertion set that makes such a control informative rather than decorative

Four assertions, exercised as a set. The fourth is the one that discriminates
and the first three are cheap sanity:

1. **Parse.** The amended document loads under the parser its consumers use.
   This catches the RT-1 class directly.
2. **List length.** The container the replacement lives in has the expected
   number of items — catching a splice that absorbed a neighbour or dropped one.
3. **Item type.** The replaced item is of the expected type (here: a mapping,
   not a scalar) — catching a splice that folded the replacement into an
   adjacent scalar.
4. **CONTENT IDENTITY AGAINST THE REPLACEMENT'S OWN STANDALONE PARSE.** Parse
   the amendment's `replacement_text_in_full` *by itself*, and assert that the
   corresponding node of the amended document is key-for-key and value-for-value
   identical to it.

**Assertion 4 is the one that discriminates, and it must be named as such in the
control's own output and in the amendment record.** On the frozen unamended file
of the motivating case, assertions 1, 2 and 3 all PASS — the file already has
seven metrics entries and its item 5 is already a single-key mapping — and only
assertion 4 fires. A control reporting a single green verdict over all four
would let a reader believe the discrimination came from the set when it came
from one member.

A second, weaker lesson from the same case: **a shape assertion is often less
discriminating than it reads.** Here `metrics[5] is a single-key mapping` looks
specific, but `metrics[4]` of the same frozen contract is *also* a single-key
mapping, so the assertion separates fewer documents than a reader assumes.
Check, at design time, how large the set of documents passing each assertion
actually is.

## Exercise it on named negative objects, INCLUDING the unamended file

A control that has never failed is an intention. Before relying on a green
result, run the control on objects for which the correct answer is FAIL, name
each one, and record what it actually did:

- **The unamended file.** The most important object and the easiest to skip. If
  the control passes here, it cannot tell an amended contract from an unamended
  one and its green result on the amended contract carries no information.
- **The known-bad replacement text** (the superseded, non-parsing draft), which
  must fail at assertion 1.
- **A length-breaking object** and **a type-breaking object**, which must fail at
  2 and 3 *distinguishably* — a control that reports the same failure for both
  is one assertion wearing three names.
- **The positive control**: the amendment itself, which must pass.

Report **what the procedure actually did on each object, not what it should have
done**, and make the self-test's exit semantics explicit: if the self-test exits
0 when every object behaves *as declared*, and four of five objects are declared
to FAIL, then its exit code does **not** mean "the amendment applies". Say so in
the artifact, because a later reader skim-reads a green report as "done".

## Its two recorded gaps, which travel with it

**A technique promoted without its known gaps is the same defect one level up.**
Both gaps below were found by an independent review of the implementation
(`TASK-20260906-ba0284`, findings V-1 and V-2) and neither is repaired in the
committed control.

- **V-1 — an override path degenerates the discriminating assertion into a
  self-consistency check.** The implementation accepts a `--clause-1-file`
  override that supplies the replacement text from a file rather than from the
  amendment record. Under that flag, assertion 4 compares the spliced document
  against *the same bytes that were spliced in*, so it can no longer fail: the
  content check becomes a tautology. **The repair is to take `expected` from the
  amendment record always, whatever the input path.** The reviewer simulated
  that repair and reported all five declared objects' outcomes unchanged. The
  general form: *any flag that changes where the expected value comes from can
  silently turn a comparison into an identity.*
- **V-2 — no whole-document invariant.** The control asserts on the replaced
  node and says nothing about the rest of the document, so it cannot see
  collateral change outside the amended block. A splice that also perturbed an
  unrelated key would pass.

## The stronger form, which already exists as a committed artifact

V-2's gap is closed by a **recursive path-by-path structural diff of the frozen
document against the fully amended one, asserted against the amendment's own
declared difference set** — not merely reported, asserted. It is implemented at
`coordination/goals/GOAL-SSI-001/batches/BATCH-60d6b9/reviews/TASK-20260906-ba0284/independent_parse_check.py`,
it is roughly twenty lines of assertion on top of the diff, and on the motivating
case it returned exactly the five declared differences and nothing else. **A
control of this form subsumes assertions 2, 3 and 4 and adds the invariant they
lack**, and an amendment that can afford it should carry it instead of the
four-assertion set.

One consequence worth stating, because a later round found it the hard way: the
difference set the diff is asserted against must be **the set the enacting party
will actually produce**. If the enacting decision changes anything the amendment's
clauses do not change — a version field, say — the enacted artifact differs in
one more place than the verified document did, and the verification no longer
covers the artifact in force. Bind the ENACTED file by digest and re-run the
diff against it.

## What this technique does not claim

It is not a claim that the amendment is *correct*. **A green control means the
amendment is APPLICABLE, never that it is RIGHT** — nothing here checks whether
the replacement text says the right thing, whether the contract is internally
consistent afterwards, or whether any other consumer of the contract accepts the
amended file. It makes no claim about any mathematical, cryptographic or
cryptanalytic question, and states nothing about any isogeny problem, any
parameter set, any exponent, any cost or any security margin.

## Confidence and limits of the evidence

`reported`, not `established`. The method has been exercised in ONE campaign, on
ONE contract, by agents of ONE model family in one orchestrating session; the
parse results come from one YAML implementation on a plain multi-line scalar, and
whether another implementation agrees is untested. What *is* durable is
mechanical and re-runnable from committed bytes by anyone: the control fails on
the unamended file at its content assertion, and the structural diff returns the
declared difference set. The judgement that this generalises beyond this contract
is the weakest part and is marked as such.
