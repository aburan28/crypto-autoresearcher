#set page(width: 297mm, height: 210mm, margin: 16mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set heading(numbering: none)

= Pages publication preflight — 2026-10-23

*Scope.* Local dashboard generation and pinned source binding for
crypto-autoresearcher main `e9b91d62a9b81a3e33a62f9f3e5036e8f7707907`.
No hosted publication or new scientific measurement occurred.

#image("publication-gate.svg", width: 100%)

The owner authorized: “Re-enable and publish after all checks pass.” As of
01:48:39 UTC, the Pages workflow was still `disabled_manually`, and public
`data/meta.json` still named the October 11 commit
`bb9e9f01f3f9fcdf6e456acd7e01cd9af6c05bc3`. Current PR/CI checks were
queued at the last check. The reason for the earlier manual disable is unknown.

== Local result

- Full-history build: 27,585 records, 55,318 files, 523,416,604 bytes;
  6,590 Git commits and 88,459 paths indexed, so record dates are available.
- Reader checks: 132 Python tests on Python 3.11.17 and 19 Node tests on
  Node 22.23.4 passed.
- Nine archived primary comparison rows have no payload error. Seven pinned
  cryptanalysis source files match SHA-256; 90 source fields and 144 displayed
  fields/source bindings match. The comparison payload SHA-256 is
  `c03a242b79197f0603bbf6657766a90e030f6d419c907c3e5ac68e07021d043b`.
- The generated integrity payload still exposes 24 unparseable records,
  225 duplicate IDs, 306 ID/path mismatches, and 1,678 dangling references.
  The separate full ledger gate remains red.

== Evidence and next gate

The exact build output is in `evidence/site-report.json`; the source and
payload check is in `evidence/snapshot-check.json`. Test logs and the
read-only public status are in `evidence/`. Two negative controls rejected a
mutated displayed operation count and optimized Python that disables checks.
The PR-scoped merge hygiene check passed in a full-tree scratch checkout.
The checker source is
`check_snapshot.py`; the editable diagram source is `publication-gate.dot`.

Before publication, recheck the exact current main head and all required and
applicable PR/CI checks. If main moved, rebuild on that head with full Git
history. Then enable and dispatch Pages, require hosted build and deploy to
pass, and read back public metadata and the nine-row comparison payload.
The live commit must equal the published main commit. A deployed dashboard
would be a current reader snapshot, not validation of every archived result.

No canonical benchmark graph changes: this build's comparison payload is
byte-identical to the prior checked one, and no benchmark value changed.
