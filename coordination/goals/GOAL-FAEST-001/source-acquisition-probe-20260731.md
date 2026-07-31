# GOAL-FAEST-001 — Source-acquisition probe, 2026-07-31

Status: **acquisition blocker**. Pause condition #2 of `ledger/goals/GOAL-FAEST-001.yaml`
holds. No batch was opened, no worker was dispatched, no experiment was designed,
and no research claim of any kind was produced.

- Goal: `GOAL-FAEST-001`
- Question: `RQ-FAEST-001`
- Probe date: 2026-07-31 (proxy relay-failure records timestamped
  `2026-07-31T16:09:55-56Z`)
- Recorded by: coordinator

## What was being acquired

`RQ-FAEST-001` forbids designing any experiment until the relevant primary
sources are filed as `KN-LIT` entries:

> Every per-scheme technical claim in this record is sourced from secondary
> reporting or from memory of the literature and is UNVERIFIED. No experiment
> may be designed until the relevant primary sources are filed as KN-LIT
> entries.

`GOAL-FAEST-001.next_action` likewise gates `/propose-ideas RQ-FAEST-001` on
obtaining the Round-3 FAEST specification. The acquisition target was therefore
the Round-3 FAEST specification bundle (team tweaks due 2026-08-14) or,
failing that, the FAEST reference implementation.

## Declared source-preference order and observed results

Order attempted: NIST CSRC -> faest.info team site -> IACR eprint -> GitHub
reference implementation.

### Tier 1-3, direct HTTPS via the agent proxy (`curl`, agent proxy on port 40341)

| Target | Observed result |
| --- | --- |
| `https://csrc.nist.gov/projects/pqc-dig-sig` | CONNECT tunnel failed, gateway 403 (policy denial) |
| `https://faest.info/` | CONNECT tunnel failed, gateway 403 |
| `https://eprint.iacr.org/2023/1573` | CONNECT tunnel failed, gateway 403 |
| `https://arxiv.org/` | no connection (000) |
| `https://www.ietf.org/` | no connection (000) |
| `https://github.com/` | reachable (400 on bare root) |
| `https://raw.githubusercontent.com/` | reachable (301) |

The proxy status endpoint (`$HTTPS_PROXY/__agentproxy/status`) recorded
`recentRelayFailures` of kind `connect_rejected`, detail "gateway answered 403
to CONNECT (policy denial or upstream failure)", for hosts `faest.info:443`,
`eprint.iacr.org:443`, and `csrc.nist.gov:443`, timestamped
`2026-07-31T16:09:55-56Z`.

### Tier 1-3, WebFetch tool (a separate network path from `curl`)

| Target | Observed result |
| --- | --- |
| `https://faest.info/` | HTTP 403 |
| `https://csrc.nist.gov/projects/pqc-dig-sig/round-3-additional-signatures` | HTTP 403 |
| `https://eprint.iacr.org/2023/1573.pdf` | HTTP 403 |

### Tier 4, GitHub reference implementation

`github.com` is reachable at the network layer, but this session's GitHub API
access is scoped to the repository `aburan28/crypto-autoresearcher` only.
`api.github.com` returned: "This GitHub API path is not available: sessions are
bound to their configured repositories." Direct fetches of
`https://github.com/faest-sign/faest-ref` and `https://github.com/faest-sign/faest-spec`
returned 403. The FAEST reference implementation is therefore not obtainable
either.

### Secondary reporting (not a substitute)

WebSearch works and returned journalistic coverage of the 2026-05-14 NIST
Round-3 announcement. It returned no primary specification text. Under the
`RQ-FAEST-001` constraint quoted above, secondary reporting cannot unblock
ideation.

### Local repository check

- No FAEST material exists in `inputs/` (only `P13-WESOLOWSKI-2026` and
  ECDLP-era files).
- `grep -ril FAEST knowledge/` returns nothing: there is no vendored copy and
  no existing `KN-LIT` entry.

## What is concluded

1. The declared source-preference order (NIST CSRC -> faest.info -> IACR eprint
   -> GitHub reference implementation) is **exhausted** under the current
   network policy.
2. Pause condition #2 of `GOAL-FAEST-001` — "No Round-3 FAEST specification or
   reference implementation can be obtained under the network policy after the
   declared source-preference order is exhausted" — holds, and it holds *before
   any batch was opened*.
3. The correct state for `GOAL-FAEST-001` is `paused` with a single concrete
   resume action.

## What is NOT concluded

This is an **acquisition/infrastructure blocker, not negative evidence about
FAEST**. Per AGENTS.md rule 3 ("A timeout, crash, or implementation failure is
not evidence against a mathematical hypothesis"), and its plain extension to a
network-policy denial, this record says **nothing whatsoever** about:

- FAEST's security or its claimed security category;
- the tightness or looseness of any link in its claim chain (VOLEitH
  consistency-check soundness, Fiat-Shamir/grinding trade-off, QROM reduction
  slack, algebraic attacks on the AES constraint system);
- AES one-wayness;
- whether the campaign's research question is tractable or worth pursuing.

No hypothesis status changed, no evidence record exists, and no claim tier was
asserted. `RQ-FAEST-001` remains `active`.

## Concrete unblock conditions

Any **one** of the following removes the blocker:

1. **Network policy allowlisting** of `csrc.nist.gov`, `faest.info`, and
   `eprint.iacr.org` for CONNECT through the agent proxy, so the Round-3
   specification bundle can be fetched directly.
2. **Human-vendored copy**: a human places the Round-3 FAEST specification
   bundle (and, if available, the reference implementation) under
   `inputs/FAEST-R3-2026/`.
3. **Widened GitHub repo scope**: this session's GitHub binding is extended to
   the FAEST reference repositories (e.g. `faest-sign/faest-ref`,
   `faest-sign/faest-spec`), making the reference implementation and spec
   sources readable.

In every case the acquired primary sources must first be filed as `KN-LIT`
entries per the `RQ-FAEST-001` constraint, before `/propose-ideas RQ-FAEST-001`
is run, and the matched AES baseline cost must be written down before any
experiment is designed.
