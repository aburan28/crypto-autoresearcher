# AES lab: Conductor access and official campaign admission

- **Status:** open; task access resolved and integration delivered, root regression and later scientific admission remain
- **Kind:** historical access/tool limit; existing base build failure; separate scientific-admission gaps
- **Affected work:** [AES native lab](../research/aes_open_angles_20261017/REPORT.md), `crypto` integration, and later official adoption
- **Next action owner:** implementation session follows current PR checks/review; base ecbench/Gaudry repair owner remains unassigned; ordinary Coordinator lifecycle for later official admission
- **Last updated:** 2026-10-17

## Problem

The `crypto` repository's required Conductor service could not be reached in this
workspace. After reviewing the concrete integration, the current user authorized
this task to proceed in the standalone checkout. The native integration is now
applied locally. This resolves access for this task; the service remains
unavailable and no reservation or standing workflow change is claimed.

The concrete [prepared integration patch](../experiments/aes-distinguisher-lab-20261017/crypto-integration.patch)
adds the standalone native crate, tests, renderer, integration notes and advisory
cards. It is preserved as the original prepared patch. It applied against
`crypto@c6d64436`; eleven implementation/Cargo files match the companion exactly,
and native formatting, release Clippy and all fourteen native tests pass. All
nine blocked backlog proposals pass structural validation. The implementation
is delivered in [crypto PR #2105](https://github.com/aburan28/crypto/pull/2105),
head `7b675aacb422a61e5977562d4bafd337804ecdd0`.
The required root-library check was run and fails with 26 compile errors on
unchanged base inputs; no root regression pass is claimed. See the
[base-build problem](https://github.com/aburan28/crypto/blob/codex/aes-distinguisher-research/problems/aes-integration-root-library-baseline.md)
for source identities, complete errors and exit conditions. No task-reservation
state was changed.

Separately, a new tool or diagnostic is not an authorization to execute held
official AES arms. The standalone suite does not satisfy their original
frontier, scientific review, cost or execution-admission requirements.

## Evidence and uncertainty

- **Observed:** `conductor check` was initially unavailable. The CLI was then
  built from `github.com/aburan28/conductor/cmd/conductor@v0.1.4`. The required
  command against scopes `tools/aes-discover`, `research/aes_distinguisher_20261017`
  and the proposed problem record failed: `not logged in`, with connection
  refused at `http://localhost:8080/v1/local/session`. No reservation was obtained.
- **Observed:** the runtime reported no configured credential or outbound
  identity binding. No credential values were read or requested in chat.
- **Observed:** the current user subsequently authorized this standalone
  integration. The tool, source comparison script, focused CI and nine blocked
  native backlog proposals are applied in the `crypto` checkout.
- **Observed:** GOAL-AES-003's committed next action prohibits D-2 arm runs
  before a separate reviewed and committed execution-authorization decision.
  GOAL-AES-001 and GOAL-AES-002 retain their own exact next actions. They were
  inspected and remain unchanged.
- **Derived or proved:** no mathematical obstruction is established by either
  an unavailable coordination endpoint or a scientific admission requirement.
- **Missing capability:** the Conductor service remains unavailable for other
  tasks. This task has explicit standalone authorization. A repaired root
  ecbench/Gaudry baseline and successful regression check are still missing;
  ordinary Coordinator lifecycle for later official arms remains separate.
- **Limits:** the new component experiments and finite endpoint search do not
  establish a full-round AES break, absence of distinguishers, novelty or a
  published-frontier improvement.

## What would unblock it

- [x] The current user explicitly authorized this task's standalone checkout
  after reviewing the prepared integration. No reservation is fabricated.
- [x] Apply the native integration, pass its affected native/backlog checks,
  run the required root check and deliver the scoped PR with its actual result.
- [ ] Repair the unchanged base compile errors, complete the root regression
  check and satisfy applicable current-head CI/review before merging. Running
  the failed check above does not fulfill this regression-success requirement.
- [ ] Before official campaign execution, satisfy that arm's existing review,
  authorization, protocol, source/input binding, lane and runner requirements.

These are independent obligations. Resolving access does not approve a scientific
claim; an independent scientific review does not repair missing environment access.

## Next discriminating step

Follow PR #2105's applicable checks and review, and resolve the separately named
base-build regression gap with its owning change. New formal quartet/SAT/learned
experiments retain their full implementation, control and admission obligations;
the blocked cards do not authorize execution.

The original access failure is preserved above. Access for this task is resolved
by current authorization and the scoped integration is delivered. Root regression,
CI/review/merge and scientific admission remain tracked independently. No
mathematical conclusion follows.
