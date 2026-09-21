# Lens calibration — UNRUN, and the false verdict it produced

**Status: the calibration control did not run. Its reported verdict is retracted.**
Under `AGENTS.md` rule 5 an infrastructure failure is never evidence, in either
direction. This document records what was attempted, what broke, what was
salvageable, and what remains open.

---

## 1. Why calibration was attempted

`SCREENING.md` §2 records that the screen **fails its own criterion 4**: it
demanded "instrument fidelity before measurement — a positive control that can
fail, evaluated before the primary run" and then screened 102 ideas with no
control confirming the three adversarial lenses can ever return *not refuted*.

That leaves `0/102 survivors` with two live readings which the screening cannot
separate:

1. the catalogue is genuinely not mint-ready; or
2. the lenses refute whatever is placed in front of them.

The calibration was a **blind positive/negative control**: two entries written in
identical catalogue form, judged by the same three lenses, with ground truth
withheld from the lenses.

| entry | ground truth (withheld) |
|---|---|
| `CAL-1` | **known-defective** — the gate of `IDEA-20260803-48e258`, evaluated at `w = 2^30` where all three committed vOW readings coincide |
| `CAL-2` | **known-sound** — `CTRL-20260805-histograms`, already executed, reproducing 183,312 / 174,033 / 16,018 exactly with two independent pivot decompositions agreeing at 149,410 |

Four outcomes were pre-registered: **calibrated** (CAL-1 refuted, CAL-2 cleared)
· **over-strict** (both refuted) · **inert** (neither refuted) · **inverted**.
Only *calibrated* would make `0/102` citable as a finding about the catalogue.

---

## 2. What broke — two independent infrastructure failures

**(a) The lenses had no file access.** Every `Read`, `Grep`, `Glob`, `Bash` and
`ToolSearch` call from all three lens agents was rejected before execution:

> `The permission handler returned updatedInput for Bash that failed schema validation: Bash failed due to the following issue: The required parameter 'command' is missing. This is a configuration issue in your canUseTool callback, PermissionRequest hook, or permission-prompt tool — updatedInput must satisfy the tool's input schema. The tool input from the model was valid.`

The same error appeared for `Glob` (`pattern`), `Grep` (`pattern`), `Read`
(`file_path`) and `ToolSearch` (`query`). The transcript is explicit that **the
tool input from the model was valid** — the permission layer stripped the
required parameter. The premise-verification lens therefore could not open a
single committed artifact, which is the one thing that lens exists to do.

**(b) The structured-output validator rejected conforming payloads.** The agents
submitted objects that manifestly satisfy the schema and were rejected anyway.
Verbatim from the transcript:

```
INPUT:  {"lens": "premise-verification",
         "judgements": [{"id": "CAL-1", "refuted": true,  "finding": "..."},
                        {"id": "CAL-2", "refuted": false, "finding": "..."}]}
RESULT: Output does not match required schema:
        root: must have required property 'lens',
        root: must have required property 'judgements'
```

Both properties are present. This is a validator defect, not a model failure. It
recurred across five attempts per agent until the retry cap fired.

**Consequence.** All three agents returned nothing, so the workflow's
post-processing counted `0` refutations of `CAL-1` and `0` of `CAL-2` and
concluded:

> `INERT — the lenses cleared a known-defective entry. They have no discriminating power and the whole screening is void.`

**THAT VERDICT IS FALSE AND IS RETRACTED.** Zero refutations because zero
judgements were returned — not because any lens cleared anything. The script's
branch logic did not distinguish "0 refutations out of 3 judgements" from "0
judgements at all", which is a decision variable read off missing data: the exact
defect this session has flagged in `EV-ECDLP-008` (efficiencies voided because a
certifying gate never certified) and in `EXP-SIG-008`'s stale `summary.json`. It
was in my own script. The script is now fixed to require a non-empty judgement
set before emitting any verdict; the fix is untested and the control remains
unrun.

---

## 3. The salvageable signal — non-durable, and labelled as such

The rejected payloads are visible in the agent transcript. The
**premise-verification** lens produced, consistently across all five rejected
attempts, and *without any file access*:

| entry | verdict | finding (verbatim, abridged) |
|---|---|---|
| `CAL-1` | **refuted: true** | "gate does not test the claimed object and its band is self-referential" |
| `CAL-2` | **refuted: false** | "committed triple is exactly arithmetically self-consistent" |

**That is the pre-registered *calibrated* outcome** — refute the defective entry,
clear the sound one — reached blind, on hand arithmetic alone.

**Why it is not sufficient.** It is one lens of three; it comes from a run that
failed; the payloads were never accepted, so nothing is durably archived by the
harness; and the lens explicitly recorded that it could not verify anything at
source, so it judged on internal consistency rather than by its own method. It is
**evidence against reading (2)** — the lenses are not unconditional refuters — and
it is **not** a calibration. The `gate` and `closure` lenses produced no payload
that survives inspection, so nothing is claimed about them.

**Net: the confound in `SCREENING.md` §2 stands, partially mitigated.** `0/102`
still may not be cited as a finding about the catalogue.

---

## 4. A genuine finding, recovered from the failure

The premise lens's stated reason for refuting `CAL-1` is **not** the defect that
was planted, and it is sharper than the planted one:

> the claim is the crossover **locus** `p*(w)`, but the test only evaluates a
> **margin in bits** at fixed `p` and fixed `w = 2^30`, never exercising the
> root-finding.

The planted defect was that `48e258`'s gate is evaluated where all three vOW
readings coincide (criterion 2). This is a *different and more basic* failure:
**the gate does not test the object the claim is about.** A known-answer gate on
a margin cannot validate machinery whose output is a locus, no matter where it is
evaluated.

That is a fifth independent defect in the six proposals filed on 2026-08-03, and
the second in `48e258` alone. It is recorded here rather than in a correction
record because it arrives from a failed run and has not been independently
confirmed; it should be re-derived before `48e258` is repaired or cited.

---

## 5. What is owed

1. **Re-run the calibration** once the permission handler and the
   structured-output validator are working. Until then the control is UNRUN and
   `SCREENING.md`'s 0/102 stays confounded.
2. **Do not self-calibrate.** The obvious shortcut — applying the three lenses by
   hand from this session, whose tools work — is invalid: this session authored
   the ground truth and cannot judge blind.
3. **Do not mint on `SCREENING.md` alone.** Its shortlist is empty; that
   recommendation is unaffected by this failure, since an uncalibrated screen
   cannot license minting either way.
4. **Re-derive the §4 finding independently** before acting on it.

## 6. What this document does not claim

- It does **not** establish that the lenses are calibrated, over-strict, inert or
  inverted. The control is unrun.
- It does **not** establish that the catalogue is or is not mint-ready.
- It does **not** void `SCREENING.md`. The screening ran; 84 `REPAIRABLE` entries
  and their named repairs are unaffected by a missing calibration, because a
  repair is a pre-ledger action that costs nothing irreversible.
- It mints no identifier, changes no status, and resolves no open problem.
