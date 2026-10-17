# AES lab: Conductor access and official campaign admission

- **Status:** open
- **Kind:** access/tool limit; separate implementation and scientific-admission gaps
- **Affected work:** [AES native lab](../research/aes_open_angles_20261017/REPORT.md), `crypto` integration, and later official adoption
- **Next action owner:** current implementation session for prepared code; user/environment owner for Conductor endpoint
- **Last updated:** 2026-10-17

## Problem

The `crypto` repository requires a Conductor task reservation before edits, but
the installed CLI cannot contact or sign in to a control plane in this workspace.
This blocks applying its prepared native-lab integration under that repository's
current workflow. Work in the other repositories continues.

The concrete [prepared integration patch](../experiments/aes-distinguisher-lab-20261017/crypto-integration.patch)
adds the standalone native crate, tests, renderer, integration notes and advisory
cards. `git apply --check` passed against `crypto@c6d64436`. It has not been
applied; no `crypto` code or task-reservation state was changed.

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
- **Observed:** GOAL-AES-003's committed next action prohibits D-2 arm runs
  before a separate reviewed and committed execution-authorization decision.
  GOAL-AES-001 and GOAL-AES-002 retain their own exact next actions. They were
  inspected and remain unchanged.
- **Derived or proved:** no mathematical obstruction is established by either
  an unavailable coordination endpoint or a scientific admission requirement.
- **Missing capability:** reachable, authenticated Conductor endpoint or an
  explicit current user instruction permitting this task's standalone checkout;
  ordinary Coordinator lifecycle for any later official campaign arm.
- **Limits:** the new component experiments and finite endpoint search do not
  establish a full-round AES break, absence of distinguishers, novelty or a
  published-frontier improvement.

## What would unblock it

- [ ] Configure a reachable Conductor endpoint and authenticate through the
  supported environment/CLI flow, then obtain a reservation for the exact scope;
  alternatively record the user's explicit instruction for this task to use a
  standalone checkout without Conductor.
- [ ] Apply the prepared native source/protocol integration, run required native
  and repository checks, and deliver its scoped PR.
- [ ] Before official campaign execution, satisfy that arm's existing review,
  authorization, protocol, source/input binding, lane and runner requirements.

These are independent obligations. Resolving access does not approve a scientific
claim; an independent scientific review does not repair missing environment access.

## Next discriminating step

Use the supplied endpoint or explicit standalone instruction to repeat the
coordination check, without changing account, bypassing the service or fabricating
a lease. Continue the already implemented `cryptanalysis` suite and advisory
autoresearcher documentation. New formal quartet/SAT/learned experiments retain
their full implementation, control and admission obligations.

Recheck when environment access or a current user instruction changes. Until
then, retain the `crypto` integration as prepared rather than applied. No
mathematical conclusion follows. Unresolved.
