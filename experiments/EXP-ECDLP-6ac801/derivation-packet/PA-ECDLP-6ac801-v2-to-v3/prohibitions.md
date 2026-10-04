# The reading rule, as an operational checklist

This is the rule from `MANIFEST.yaml`, restated as things to do and not do.
It is a checklist, not a new rule: `MANIFEST.yaml` governs.

---

## 1. The rule

**Until your seal exists, you read exactly the four files enumerated in
`MANIFEST.yaml` and nothing else in this repository.**

It is an **allowlist**. The set of permitted files is closed, finite and
hashed. Anything not on it is not permitted — you do not need to consult a
list of forbidden things, because "forbidden" is simply the complement of a
four-item list.

This is the point of the design. A prohibition list cannot be shown complete:
it enumerates what must not be read out of a repository of thousands of
record-bearing paths that grows every batch, and the last re-derivation of
this quantity was compromised by two paths its author had not thought to
list. You cannot be asked to obey a list nobody can finish. You can be asked
to read four files.

## 2. Do not

- **Do not read the experiment contract.** Not `specification.yaml`, not
  `specification.v2.yaml`, not `specification.v3.yaml`, not any
  `.proposed.yaml`. `quantity.md` quotes everything from it you need.
- **Do not read the amendment record** (`amendments/`).
- **Do not read any handoff, task card, dispatch queue, decision record,
  evidence record, goal record, checkpoint, correction, review report or
  validation report.**
- **Do not read any run directory** — no manifest, no `raw-result.json`, no
  `summary.json`, no analysis output, for this experiment or any other.
- **Do not read any existing implementation of this or a similar
  measurement.** Not `instrument.py`, not `run_stageb.py`, not a prior
  re-derivation's script, not a post-hoc diagnostic script. Write your own.
- **Do not read any prior file, review plan or coordinator prior.**
- **Do not read `knowledge/`, `docs/` or `inputs/` for this quantity.**

## 3. Do not, specifically about git

These are called out separately because they are the mechanical route by
which the previous reading was compromised, and because they are easy to run
without thinking.

- **Do not run `git log`, `git show`, `git blame`, `git diff` against
  history, or any command that prints a commit message.**
- **Do not read a commit message by any other route** — not a PR page, not a
  branch description, not a CI log.

**Honest disclosure, so you can judge your own exposure:** at least two
commit messages reachable from the branch this packet was authored on state a
prior cell's verdict in plain text. That contamination is permanent and
cannot be repaired. It is why the rule above is mechanical rather than a
matter of judgement: obeying the allowlist means you run no history command
at all, and the exposure does not arise.

`git status`, `git add` and `git commit` on **your own task directory** are
fine and are how you seal.

## 4. Do

- Read the four packet files.
- Write your own implementation from `quantity.md`.
- Use any language, any libraries, any standard `mix64`, any RNG. Nothing
  needs to match another implementation bit-for-bit (`quantity.md` §9).
- Compute `a = 1/4` first at each scale, and `N = 2^20` before `N = 2^24`.
- Report every field in `deliverables.md`, including the ones that look like
  bookkeeping. `cycle_mass`, `capped_mass`, `capped_walks` and the accounting
  identity are not bookkeeping — they are the defect this packet exists to
  close.
- Seal before you open anything else (`deliverables.md` §7).
- Record the complete list of files you read before sealing
  (`deliverables.md` §6).

## 5. If you slip

**Report it.** Say what you read and whether it was before or after your
seal.

The consequence is stated in advance so it holds no surprise, and it is
deliberately asymmetric: if you read something outside the packet before
sealing, your reading's **agreement** with the other reading carries no
independence weight for this batch. Its **disagreement** still carries full
weight — a disagreement reached despite having seen the other answer is
stronger evidence, not weaker.

So disclosing costs you only the weaker half of your result. Concealing
costs the batch its only independence claim, and the concealment is the kind
of thing a later audit finds. There is no version of this where concealing is
the better move.

## 6. If the packet is wrong

If you find that this packet is **incomplete** — that some quantity in
`deliverables.md` cannot be computed from what `quantity.md` gives you, or
that two files here contradict each other — **stop and report it as a defect
of the packet**. Do not fill the gap by reading outside the allowlist, and do
not fill it by choosing a convention yourself.

That failure mode is exactly what this whole exercise exists to detect. The
last re-derivation of this quantity disagreed with production because the
contract named a formula without stating it, and the re-deriver had to make a
defensible but arbitrary choice. **An incomplete packet is a finding, and a
valuable one.** Reporting it is a success, not a failure to deliver.

## 7. Who may not do this task

You must be in a session that authored **neither the contract, nor the
amendment, nor this packet**. Authorship of the packet is disqualifying for
obeying it: the author knows what was deliberately left out, which is
precisely the knowledge the seal is meant to exclude.
